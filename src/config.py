# =====================================================
# CONFIGURACIÓN AZURE OPENAI AVANZADA
# =====================================================
import os
import json
from pathlib import Path

AZURE_OPENAI_ENDPOINT = "AZURE-ENDPOINT"
AZURE_OPENAI_API_KEY = "API-TOKEN"
AZURE_OPENAI_DEPLOYMENT_NAME = "DEPLOYMENT"
AZURE_OPENAI_API_VERSION = "2025-01-01-preview"

# Directorios del proyecto
PROJECT_ROOT = Path(__file__).parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

# Asegurar que los directorios existen
CONFIG_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# Archivos de configuración
SYSTEM_PROMPT_FILE = CONFIG_DIR / "system_prompt.txt"
MODEL_CONFIG_FILE = CONFIG_DIR / "model_config.json"
MEMORY_FILE_PATH = DATA_DIR / "conversation_history.json"
SUMMARY_FILE_PATH = DATA_DIR / "conversation_summaries.json"
METRICS_FILE_PATH = DATA_DIR / "metrics.json"

# Configuración de memoria avanzada
SHORT_TERM_MEMORY_LIMIT = 10  # Más interacciones para mejor contexto
LONG_TERM_SUMMARY_THRESHOLD = 50  # Resumir cada 50 interacciones
MAX_CONTEXT_TOKENS = 6000  # Límite inteligente de tokens
RELEVANCE_SEARCH_LIMIT = 5  # Top 5 conversaciones relevantes

# Configuración de logging
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_FILE = LOGS_DIR / "agent.log"

# Configuración de métricas
ENABLE_METRICS = True
METRICS_RETENTION_DAYS = 30

# Configuración por defecto (se sobrescribe con archivo externo)
DEFAULT_MODEL_CONFIG = {
    "temperature": 0.8,
    "max_tokens": 2048,
    "top_p": 0.9,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
    "stream": True
}

# System prompt por defecto
DEFAULT_SYSTEM_PROMPT = """Eres un asistente conversacional inteligente y útil. Tienes acceso al historial de conversación y puedes recordar interacciones previas relevantes. 

Características:
- Respondes de manera clara, precisa y contextual
- Mantienes un tono amigable y profesional  
- Puedes recordar y referenciar conversaciones anteriores
- Adaptas tu respuesta según el contexto de la conversación

Instrucciones:
- Si referencias información de conversaciones anteriores, menciona brevemente el contexto
- Mantén tus respuestas enfocadas y relevantes
- Si no estás seguro de algo, admítelo honestamente"""


class ConfigManager:
    """Gestor de configuración externa"""
    
    @staticmethod
    def load_system_prompt():
        """Cargar system prompt desde archivo externo"""
        try:
            if SYSTEM_PROMPT_FILE.exists():
                with open(SYSTEM_PROMPT_FILE, 'r', encoding='utf-8') as f:
                    return f.read().strip()
            else:
                # Crear archivo con prompt por defecto
                ConfigManager.save_system_prompt(DEFAULT_SYSTEM_PROMPT)
                return DEFAULT_SYSTEM_PROMPT
        except Exception as e:
            print(f"Error cargando system prompt: {e}")
            return DEFAULT_SYSTEM_PROMPT
    
    @staticmethod
    def save_system_prompt(prompt):
        """Guardar system prompt en archivo externo"""
        try:
            with open(SYSTEM_PROMPT_FILE, 'w', encoding='utf-8') as f:
                f.write(prompt)
        except Exception as e:
            print(f"Error guardando system prompt: {e}")
    
    @staticmethod
    def load_model_config():
        """Cargar configuración del modelo desde archivo externo"""
        try:
            if MODEL_CONFIG_FILE.exists():
                with open(MODEL_CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Validar configuración
                    return ConfigManager._validate_model_config(config)
            else:
                # Crear archivo con configuración por defecto
                ConfigManager.save_model_config(DEFAULT_MODEL_CONFIG)
                return DEFAULT_MODEL_CONFIG
        except Exception as e:
            print(f"Error cargando configuración del modelo: {e}")
            return DEFAULT_MODEL_CONFIG
    
    @staticmethod
    def save_model_config(config):
        """Guardar configuración del modelo en archivo externo"""
        try:
            with open(MODEL_CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            print(f"Error guardando configuración del modelo: {e}")
    
    @staticmethod
    def _validate_model_config(config):
        """Validar y normalizar configuración del modelo"""
        validated = DEFAULT_MODEL_CONFIG.copy()
        
        # Validar temperatura
        if 'temperature' in config:
            temp = float(config['temperature'])
            validated['temperature'] = max(0.0, min(2.0, temp))
        
        # Validar max_tokens
        if 'max_tokens' in config:
            tokens = int(config['max_tokens'])
            validated['max_tokens'] = max(1, min(4000, tokens))
        
        # Validar top_p
        if 'top_p' in config:
            top_p = float(config['top_p'])
            validated['top_p'] = max(0.0, min(1.0, top_p))
        
        # Validar penalties
        for penalty in ['frequency_penalty', 'presence_penalty']:
            if penalty in config:
                val = float(config[penalty])
                validated[penalty] = max(-2.0, min(2.0, val))
        
        # Validar stream
        if 'stream' in config:
            validated['stream'] = bool(config['stream'])
        
        return validated
    
    @staticmethod
    def get_config_summary():
        """Obtener resumen de la configuración actual"""
        system_prompt = ConfigManager.load_system_prompt()
        model_config = ConfigManager.load_model_config()
        
        return {
            "system_prompt_length": len(system_prompt),
            "system_prompt_file": str(SYSTEM_PROMPT_FILE),
            "model_config": model_config,
            "model_config_file": str(MODEL_CONFIG_FILE),
            "memory_file": str(MEMORY_FILE_PATH),
            "metrics_enabled": ENABLE_METRICS,
            "logging_enabled": True,
            "log_file": str(LOG_FILE)
        }

# Cargar configuración al importar el módulo
CURRENT_SYSTEM_PROMPT = ConfigManager.load_system_prompt()
CURRENT_MODEL_CONFIG = ConfigManager.load_model_config()
