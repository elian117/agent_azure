import sys
import signal
import time
import logging
from memory_system import MemorySystem
from azure_client import AzureOpenAIClient
from config import ConfigManager, LOG_FILE, LOG_FORMAT, LOG_LEVEL

# Configurar logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format=LOG_FORMAT,
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


class AdvancedConversationalAgent:
    def __init__(self):
        self.memory = MemorySystem()
        self.azure_client = AzureOpenAIClient()
        self.running = True
        
        # Configurar manejo de señales
        signal.signal(signal.SIGINT, self.signal_handler)
        
        logger.info("Agente conversacional avanzado inicializado")
    
    def signal_handler(self, sig, frame):
        """Manejar Ctrl+C elegantemente"""
        print("\n\nCerrando sesión...")
        self.show_session_summary()
        print("¡Hasta luego!")
        logger.info("Sesión terminada por usuario")
        sys.exit(0)
    
    def show_welcome_message(self):
        """Mensaje de bienvenida avanzado"""
        print("=" * 80)
        print("AGENTE CONVERSACIONAL - AZURE OPENAI")
        print("=" * 80)
        print("¡Bienvenido! Este es tu asistente conversacional con características avanzadas:")
        print("")
        print("Características:")
        print("  • Memoria inteligente con búsqueda por relevancia")
        print("  • Respuestas en streaming (tiempo real)")
        print("  • Configuración externa personalizable")
        print("  • Métricas y logging detallado")
        print("  • Resúmenes automáticos de conversaciones")
        print("")
        print("Comandos disponibles:")
        print("  • 'exit' / 'quit'      → Salir con resumen de sesión")
        print("  • 'clear'              → Limpiar memoria de corto plazo")
        print("  • 'history'            → Mostrar historial reciente")
        print("  • 'config'             → Mostrar/editar configuración")
        print("  • 'metrics'            → Ver métricas de uso")
        print("  • 'info'               → Información del sistema")
        print("  • 'help'               → Mostrar esta ayuda")
        print("")
        print("=" * 80)
    
    def show_streaming_indicator(self, show: bool = True):
        """Mostrar/ocultar indicador de streaming"""
        if show:
            print("Asistente: ", end="", flush=True)
        else:
            print()  # Nueva línea al terminar
    
    def process_special_command(self, user_input: str):
        """Procesar comandos especiales avanzados"""
        parts = user_input.strip().split(maxsplit=1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if command in ['exit', 'quit']:
            print("\nCerrando sesión...")
            self.show_session_summary()
            print("¡Gracias por usar el agente conversacional!")
            return True
        
        elif command == 'clear':
            self.memory.clear_short_term()
            return "COMMAND_PROCESSED"
        
        elif command == 'history':
            limit = 10
            if args and args.isdigit():
                limit = int(args)
            self.memory.show_recent_history(limit)
            return "COMMAND_PROCESSED"
        
        elif command == 'config':
            if not args:
                self.show_config_menu()
            else:
                self.handle_config_command(args)
            return "COMMAND_PROCESSED"
        
        elif command == 'metrics':
            self.show_metrics_dashboard()
            return "COMMAND_PROCESSED"
        
        elif command == 'info':
            self.show_system_info()
            return "COMMAND_PROCESSED"
        
        elif command == 'help':
            self.show_welcome_message()
            return "COMMAND_PROCESSED"
        
        return False
    
    def show_config_menu(self):
        """Mostrar menú de configuración"""
        config_summary = ConfigManager.get_config_summary()
        model_config = ConfigManager.load_model_config()
        
        print("\nCONFIGURACIÓN ACTUAL")
        print("=" * 50)
        print(f"System Prompt: {config_summary['system_prompt_length']} caracteres")
        print(f"Archivo: {config_summary['system_prompt_file']}")
        print()
        print("Parámetros del Modelo:")
        for key, value in model_config.items():
            print(f"   • {key}: {value}")
        print()
        print("Sistema:")
        print(f"   • Métricas: {'✅' if config_summary['metrics_enabled'] else '❌'}")
        print(f"   • Logging: {'✅' if config_summary['logging_enabled'] else '❌'}")
        print(f"   • Log file: {config_summary['log_file']}")
        print()
        print("Comandos de configuración:")
        print("  • 'config temp 0.8'     → Cambiar temperatura")
        print("  • 'config tokens 2000'  → Cambiar max_tokens")
        print("  • 'config stream on'    → Activar streaming")
        print("  • 'config stream off'   → Desactivar streaming")
        print("=" * 50)
    
    def handle_config_command(self, args: str):
        """Manejar comandos de configuración"""
        parts = args.split()
        if len(parts) < 2:
            print("Formato incorrecto. Ejemplo: config temp 0.8")
            return
        
        param = parts[0].lower()
        value = parts[1]
        
        try:
            if param in ['temp', 'temperature']:
                success = self.azure_client.update_model_config(temperature=float(value))
            elif param in ['tokens', 'max_tokens']:
                success = self.azure_client.update_model_config(max_tokens=int(value))
            elif param == 'stream':
                stream_val = value.lower() in ['on', 'true', '1', 'yes']
                success = self.azure_client.update_model_config(stream=stream_val)
            elif param == 'top_p':
                success = self.azure_client.update_model_config(top_p=float(value))
            else:
                print(f"Parámetro desconocido: {param}")
                return
            
            if success:
                print(f"Configuración actualizada: {param} = {value}")
            else:
                print(f"Error actualizando configuración")
                
        except ValueError as e:
            print(f"Valor inválido: {e}")
    
    def show_metrics_dashboard(self):
        """Mostrar dashboard de métricas"""
        stats = self.azure_client.get_usage_stats()
        memory_stats = self.memory.get_memory_stats()
        
        print("\nMÉTRICAS")
        print("=" * 60)
        
        print("Sesión Actual:")
        current = stats.get('current_session', {})
        duration = current.get('session_duration', 0)
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        
        print(f"   • Duración: {hours}h {minutes}m")
        print(f"   • Interacciones: {current.get('interactions', 0)}")
        print(f"   • Tokens usados: {current.get('total_tokens', 0):,}")
        print(f"   • Tiempo promedio de respuesta: {current.get('average_response_time', 0):.2f}s")
        print(f"   • Errores: {sum(current.get('errors', {}).values())}")
        
        print("\nEstadísticas Globales:")
        print(f"   • Total sesiones: {stats.get('total_sessions', 0)}")
        print(f"   • Total interacciones: {stats.get('total_interactions', 0)}")
        print(f"   • Total tokens: {stats.get('total_tokens_used', 0):,}")
        print(f"   • Interacciones recientes (7d): {stats.get('recent_interactions_7d', 0)}")
        
        print("\nMemoria:")
        print(f"   • Conversaciones totales: {memory_stats.get('total_conversations', 0)}")
        print(f"   • Conversaciones activas: {memory_stats.get('active_conversations', 0)}")
        print(f"   • Tokens en memoria: {memory_stats.get('total_tokens', 0):,}")
        print(f"   • Resúmenes: {memory_stats.get('summaries_count', 0)}")
        print(f"   • Tamaño archivo memoria: {memory_stats.get('memory_file_size', 0) / 1024:.1f} KB")
        print("=" * 60)
    
    def show_system_info(self):
        """Mostrar información del sistema"""
        model_info = self.azure_client.get_model_info()
        config_summary = ConfigManager.get_config_summary()
        
        print("\n💻 INFORMACIÓN DEL SISTEMA")
        print("=" * 60)
        
        print("Azure OpenAI:")
        print(f"   • Endpoint: {model_info.get('endpoint', 'N/A')}")
        print(f"   • Deployment: {model_info.get('deployment', 'N/A')}")
        print(f"   • API Version: {model_info.get('api_version', 'N/A')}")
        print(f"   • Streaming: {'✅' if model_info.get('streaming_enabled') else '❌'}")
        
        print("\nConfiguración:")
        print(f"   • System prompt: {model_info.get('system_prompt_length', 0)} caracteres")
        print(f"   • Temperatura: {model_info.get('model_config', {}).get('temperature', 'N/A')}")
        print(f"   • Max tokens: {model_info.get('model_config', {}).get('max_tokens', 'N/A')}")
        
        print(f"\nArchivos:")
        print(f"   • Config: {config_summary.get('model_config_file', 'N/A')}")
        print(f"   • Memoria: {config_summary.get('memory_file', 'N/A')}")
        print(f"   • Logs: {config_summary.get('log_file', 'N/A')}")
        
        print("=" * 60)
    
    def show_session_summary(self):
        """Mostrar resumen al finalizar sesión"""
        stats = self.azure_client.get_usage_stats()
        current = stats.get('current_session', {})
        
        duration = current.get('session_duration', 0)
        hours = int(duration // 3600)
        minutes = int((duration % 3600) // 60)
        seconds = int(duration % 60)
        
        print("\nRESUMEN DE SESIÓN")
        print("=" * 50)
        print(f"Duración: {hours:02d}:{minutes:02d}:{seconds:02d}")
        print(f"Interacciones: {current.get('interactions', 0)}")
        print(f"Tokens usados: {current.get('total_tokens', 0):,}")
        if current.get('interactions', 0) > 0:
            print(f"Promedio por respuesta: {current.get('average_response_time', 0):.2f}s")
            print(f"Tokens promedio: {current.get('average_tokens_per_interaction', 0):.0f}")
        
        errors = sum(current.get('errors', {}).values())
        if errors > 0:
            print(f"Errores: {errors}")
        
        print("Todas las conversaciones han sido guardadas")
        print("=" * 50)
    
    def initialize(self):
        """Inicializar el agente avanzado"""
        self.show_welcome_message()
        
        # Probar conexión
        print("Probando conexión con Azure OpenAI...")
        if not self.azure_client.test_connection():
            print("No se pudo conectar con Azure OpenAI.")
            print("Verifica las credenciales en src/config.py")
            return False
        print("Conexión exitosa")
        
        # Mostrar información del modelo
        model_info = self.azure_client.get_model_info()
        print(f"Modelo: {model_info.get('deployment', 'N/A')}")
        print(f"Streaming: {'Activado' if model_info.get('streaming_enabled') else 'Desactivado'}")
        
        # Cargar memoria
        print("Cargando memoria de conversaciones...")
        self.memory.load_from_long_term()
        
        # Mostrar estadísticas iniciales
        memory_stats = self.memory.get_memory_stats()
        if memory_stats.get('total_conversations', 0) > 0:
            print(f"Memoria: {memory_stats['total_conversations']} conversaciones, {memory_stats['total_tokens']:,} tokens")
        print("-" * 80)
        logger.info("Agente inicializado exitosamente")
        return True
    
    def run(self):
        """Bucle principal con streaming avanzado"""
        if not self.initialize():
            return
        
        while self.running:
            try:
                # Entrada del usuario
                user_input = input(f"\n👤 Tú: ").strip()
                
                if not user_input:
                    continue
                
                # Procesar comandos especiales
                command_result = self.process_special_command(user_input)
                if command_result == True:  # exit
                    break
                elif command_result == "COMMAND_PROCESSED":  # comando ejecutado
                    continue
                
                # Preparar contexto inteligente
                start_time = time.time()
                context_messages, context_sources = self.memory.get_intelligent_context(user_input)
                
                logger.info(f"Contexto preparado: {len(context_messages)} mensajes de {context_sources}")
                
                # Mostrar indicador de streaming
                self.show_streaming_indicator(True)
                
                # Generar respuesta con streaming
                full_response = ""
                metrics = {}
                
                response_generator = self.azure_client.generate_response_stream(
                    user_input, context_messages, context_sources
                )
                
                for chunk in response_generator:
                    if isinstance(chunk, str):
                        # Es un chunk de texto
                        print(chunk, end="", flush=True)
                        full_response += chunk
                    else:
                        # Es el resultado final con métricas
                        metrics, complete_response = chunk
                        full_response = complete_response
                        break
                
                # Finalizar streaming
                self.show_streaming_indicator(False)
                
                # Mostrar métricas si no hay errores
                if not metrics.get('error'):
                    response_time = metrics.get('response_time', 0)
                    tokens_used = metrics.get('total_tokens', 0)
                    print(f"{response_time:.1f}s | {tokens_used} tokens")
                    
                    # Guardar en memoria
                    self.memory.add_interaction(
                        user_input, 
                        full_response, 
                        metadata={
                            'response_time': response_time,
                            'tokens': tokens_used,
                            'context_sources': context_sources
                        }
                    )
                    
                    logger.info(f"Interacción completada: {tokens_used} tokens, {response_time:.2f}s")
                else:
                    # Manejar errores
                    error_type = metrics.get('error')
                    print(f"\n {full_response}")
                    
                    if error_type == 'context_length_error':
                        print("💡 Intenta usar 'clear' para reducir el contexto")
                    elif error_type == 'rate_limit_error':
                        print("⏳ Espera un momento antes del siguiente mensaje")
                
            except KeyboardInterrupt:
                break
            except EOFError:
                print("\n")
                self.show_session_summary()
                print("¡Hasta luego!")
                break
            except Exception as e:
                print(f"\nError inesperado: {e}")
                logger.error(f"Error en bucle principal: {e}")
                print("Continuando...")


def main():
    """Función principal avanzada"""
    print("INICIANDO AGENTE CONVERSACIONAL")
    print("=" * 50)
    
    # Verificar Python
    if sys.version_info < (3, 8):
        print("Requiere Python 3.8+")
        return
    
    print(f"Python: {sys.version.split()[0]}")
    
    # Verificar dependencias
    try:
        import openai
        print(f"OpenAI: {openai.__version__}")
    except ImportError:
        print("OpenAI no encontrado. Ejecuta: pip install openai")
        return
    
    # Crear y ejecutar agente
    agent = AdvancedConversationalAgent()
    
    try:
        agent.run()
    except KeyboardInterrupt:
        print("\n\nInterrumpido por usuario")
        agent.show_session_summary()
    except Exception as e:
        print(f"\nError crítico: {e}")
        logger.error(f"Error crítico: {e}")
    finally:
        logger.info("Sesión finalizada")


if __name__ == "__main__":
    main()