import openai
import time
import logging
from typing import List, Dict, Generator, Optional, Tuple
from config import (
    AZURE_OPENAI_ENDPOINT,
    AZURE_OPENAI_API_KEY,
    AZURE_OPENAI_DEPLOYMENT_NAME,
    AZURE_OPENAI_API_VERSION,
    CURRENT_SYSTEM_PROMPT,
    CURRENT_MODEL_CONFIG,
    ConfigManager
)
from metrics_logger import MetricsLogger

logger = logging.getLogger(__name__)


class AzureOpenAIClient:
    def __init__(self):
        self.client = openai.AzureOpenAI(
            api_key=AZURE_OPENAI_API_KEY,
            api_version=AZURE_OPENAI_API_VERSION,
            azure_endpoint=AZURE_OPENAI_ENDPOINT
        )
        self.metrics = MetricsLogger()
        logger.info("Azure OpenAI client inicializado")
    
    def generate_response_stream(self, user_message: str, context_messages: List[Dict[str, str]] = None, 
                               context_sources: List[str] = None) -> Generator[str, None, Tuple[Dict, str]]:
        """Generar respuesta con streaming y métricas detalladas"""
        start_time = time.time()
        
        try:
            # Cargar configuración actual
            system_prompt = ConfigManager.load_system_prompt()
            model_config = ConfigManager.load_model_config()
            
            # Construir mensajes
            messages = [{"role": "system", "content": system_prompt}]
            
            # Agregar contexto si existe
            if context_messages:
                messages.extend(context_messages)
                logger.debug(f"Agregado contexto: {len(context_messages)} mensajes de {context_sources}")
            
            # Agregar mensaje actual
            messages.append({"role": "user", "content": user_message})
            
            # Estimar tokens de entrada
            input_tokens = self._estimate_tokens(messages)
            
            logger.info(f"Generando respuesta - Tokens entrada: {input_tokens}")
            
            # Realizar llamada con streaming
            response_chunks = []
            output_tokens = 0
            
            response_stream = self.client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=messages,
                **model_config
            )
            
            if model_config.get('stream', False):
                # Streaming habilitado
                for chunk in response_stream:
                    if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        response_chunks.append(content)
                        yield content
                
                full_response = ''.join(response_chunks)
                output_tokens = self._estimate_tokens([{"role": "assistant", "content": full_response}])
            else:
                # Sin streaming
                full_response = response_stream.choices[0].message.content
                output_tokens = self._estimate_tokens([{"role": "assistant", "content": full_response}])
                yield full_response
            
            # Calcular métricas
            end_time = time.time()
            response_time = end_time - start_time
            
            metrics = {
                "timestamp": time.time(),
                "input_tokens": input_tokens,
                "output_tokens": output_tokens,
                "total_tokens": input_tokens + output_tokens,
                "response_time": response_time,
                "model_config": model_config.copy(),
                "context_sources": context_sources or [],
                "user_message_length": len(user_message),
                "response_length": len(full_response),
                "streaming_enabled": model_config.get('stream', False)
            }
            
            # Registrar métricas
            self.metrics.log_interaction(metrics)
            
            logger.info(f"Respuesta generada - Tokens salida: {output_tokens}, Tiempo: {response_time:.2f}s")
            
            return metrics, full_response
            
        except openai.AuthenticationError as e:
            error_msg = "Error de autenticación: Verifica las credenciales de Azure OpenAI"
            logger.error(f"AuthenticationError: {e}")
            self.metrics.log_error("authentication_error", str(e))
            return {"error": "authentication"}, error_msg
        
        except openai.RateLimitError as e:
            error_msg = "Límite de tasa excedido. Intenta más tarde"
            logger.warning(f"RateLimitError: {e}")
            self.metrics.log_error("rate_limit_error", str(e))
            return {"error": "rate_limit"}, error_msg
        
        except openai.BadRequestError as e:
            if "maximum context length" in str(e).lower():
                error_msg = "Límite de tokens excedido. Usa 'clear' para limpiar contexto"
                logger.warning(f"Context length exceeded: {e}")
                self.metrics.log_error("context_length_error", str(e))
            else:
                error_msg = f"Error en solicitud: {e}"
                logger.error(f"BadRequestError: {e}")
                self.metrics.log_error("bad_request_error", str(e))
            return {"error": "bad_request"}, error_msg
        
        except Exception as e:
            error_msg = f"Error inesperado: {e}"
            logger.error(f"Unexpected error: {e}")
            self.metrics.log_error("unexpected_error", str(e))
            return {"error": "unexpected"}, error_msg
    
    def generate_response(self, user_message: str, context_messages: List[Dict[str, str]] = None,
                         context_sources: List[str] = None) -> Tuple[str, Dict]:
        """Generar respuesta sin streaming (método de compatibilidad)"""
        response_text = ""
        metrics = {}
        
        for chunk in self.generate_response_stream(user_message, context_messages, context_sources):
            if isinstance(chunk, str):
                response_text += chunk
            else:
                # Es el resultado final
                metrics, full_response = chunk
                return full_response, metrics
        
        return response_text, metrics
    
    def _estimate_tokens(self, messages: List[Dict[str, str]]) -> int:
        """Estimación de tokens para Azure OpenAI (aproximada)"""
        total_chars = sum(len(msg.get("content", "")) for msg in messages)
        # Estimación: 1 token ≈ 4 caracteres para modelos GPT
        return total_chars // 4
    
    def test_connection(self) -> bool:
        """Probar conexión con Azure OpenAI"""
        try:
            logger.info("Probando conexión con Azure OpenAI...")
            
            test_messages = [
                {"role": "system", "content": "Responde solo con 'OK'"},
                {"role": "user", "content": "Test de conexión"}
            ]
            
            response = self.client.chat.completions.create(
                model=AZURE_OPENAI_DEPLOYMENT_NAME,
                messages=test_messages,
                max_tokens=5,
                temperature=0
            )
            
            logger.info("Conexión exitosa con Azure OpenAI")
            return True
            
        except Exception as e:
            logger.error(f"Error de conexión con Azure OpenAI: {e}")
            return False
    
    def get_model_info(self) -> Dict:
        """Obtener información del modelo y configuración actual"""
        config = ConfigManager.load_model_config()
        system_prompt = ConfigManager.load_system_prompt()
        
        return {
            "endpoint": AZURE_OPENAI_ENDPOINT,
            "deployment": AZURE_OPENAI_DEPLOYMENT_NAME,
            "api_version": AZURE_OPENAI_API_VERSION,
            "model_config": config,
            "system_prompt_length": len(system_prompt),
            "streaming_enabled": config.get('stream', False)
        }
    
    def update_model_config(self, **kwargs) -> bool:
        """Actualizar configuración del modelo en tiempo real"""
        try:
            current_config = ConfigManager.load_model_config()
            
            # Validar y actualizar parámetros
            valid_params = ['temperature', 'max_tokens', 'top_p', 'frequency_penalty', 'presence_penalty', 'stream']
            
            for key, value in kwargs.items():
                if key in valid_params:
                    current_config[key] = value
            
            # Guardar configuración actualizada
            ConfigManager.save_model_config(current_config)
            
            logger.info(f"Configuración del modelo actualizada: {kwargs}")
            return True
            
        except Exception as e:
            logger.error(f"Error actualizando configuración: {e}")
            return False
    
    def get_usage_stats(self) -> Dict:
        """Obtener estadísticas de uso del cliente"""
        return self.metrics.get_summary_stats()