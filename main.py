#!/usr/bin/env python3
"""
Agente Conversacional Avanzado CLI con Azure OpenAI
Prueba Técnica - Backend Engineer (Versión Completa)

Este script ejecuta el agente conversacional avanzado con todas las características:
- Búsqueda inteligente en memoria por relevancia
- Streaming de respuestas en tiempo real
- Configuración externa personalizable
- Gestión avanzada de memoria con resumenes automáticos
- Sistema de logging y métricas detallado
- Pruebas unitarias para componentes críticos
"""

import sys
import os
from pathlib import Path

# Agregar src al path para imports
PROJECT_ROOT = Path(__file__).parent
sys.path.append(str(PROJECT_ROOT / 'src'))

def check_environment():
    """Verificar que el entorno esté configurado correctamente"""
    print("Verificando entorno...")
    
    # Verificar Python
    if sys.version_info < (3, 8):
        print("Se requiere Python 3.8 o superior")
        return False
    
    print(f"Python {sys.version.split()[0]}")
    
    # Verificar dependencias
    try:
        import openai
        print(f"OpenAI SDK {openai.__version__}")
    except ImportError:
        print("OpenAI SDK no encontrado")
        print("Instala con: pip install openai")
        return False
    
    # Verificar estructura de directorios
    required_dirs = ['src', 'config', 'data', 'logs']
    for dir_name in required_dirs:
        dir_path = PROJECT_ROOT / dir_name
        if not dir_path.exists():
            print(f"Creando directorio: {dir_name}")
            dir_path.mkdir(exist_ok=True)
        else:
            print(f"Directorio {dir_name} existe")
    
    # Verificar archivos de configuración
    config_dir = PROJECT_ROOT / 'config'
    
    # Crear archivos de configuración si no existen
    model_config_file = config_dir / 'model_config.json'
    if not model_config_file.exists():
        print("Creando configuración por defecto del modelo...")
        import json
        default_config = {
            "temperature": 0.7,
            "max_tokens": 1500,
            "top_p": 0.9,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            "stream": True
        }
        with open(model_config_file, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=2)
    
    system_prompt_file = config_dir / 'system_prompt.txt'
    if not system_prompt_file.exists():
        print("Creando system prompt por defecto...")
        default_prompt = """Eres un asistente conversacional inteligente y útil. Tienes acceso al historial de conversación y puedes recordar interacciones previas relevantes.

Características:
- Respondes de manera clara, precisa y contextual
- Mantienes un tono amigable y profesional  
- Puedes recordar y referenciar conversaciones anteriores
- Adaptas tu respuesta según el contexto de la conversación

Instrucciones:
- Si referencias información de conversaciones anteriores, menciona brevemente el contexto
- Mantén tus respuestas enfocadas y relevantes
- Si no estás seguro de algo, admítelo honestamente"""
        
        with open(system_prompt_file, 'w', encoding='utf-8') as f:
            f.write(default_prompt)
    
    print("Entorno configurado correctamente")
    return True

def show_credentials_help():
    """Mostrar ayuda para configurar credenciales"""
    print("\nCONFIGURACIÓN DE CREDENCIALES")
    print("=" * 60)
    print("Para usar este agente, necesitas configurar tus credenciales de Azure OpenAI:")
    print()
    print("Método 1: Variables de entorno (recomendado)")
    print("   export AZURE_OPENAI_ENDPOINT='https://tu-recurso.cognitiveservices.azure.com'")
    print("   export AZURE_OPENAI_API_KEY='tu-api-key-aqui'")
    print("   export AZURE_OPENAI_DEPLOYMENT_NAME='tu-deployment'")
    print()
    print("Método 2: Editar src/config.py")
    print("   Cambia las variables AZURE_OPENAI_* con tus credenciales")
    print()
    print("Asegúrate de tener:")
    print("   • Un recurso de Azure OpenAI activo")
    print("   • Un deployment de GPT-4 o GPT-3.5-turbo")
    print("   • La API key con permisos suficientes")
    print("=" * 60)

def run_tests():
    """Ejecutar pruebas unitarias"""
    print("\nEJECUTANDO PRUEBAS UNITARIAS")
    print("=" * 50)
    
    try:
        import unittest
        
        # Descubrir y ejecutar pruebas
        test_dir = PROJECT_ROOT / 'tests'
        if test_dir.exists():
            loader = unittest.TestLoader()
            suite = loader.discover(str(test_dir), pattern='test_*.py')
            runner = unittest.TextTestRunner(verbosity=2)
            result = runner.run(suite)
            
            if result.wasSuccessful():
                print("Todas las pruebas pasaron")
                return True
            else:
                print(f"{len(result.failures)} pruebas fallaron")
                return False
        else:
            print("Directorio de pruebas no encontrado")
            return True
            
    except Exception as e:
        print(f"Error ejecutando pruebas: {e}")
        return False

def main():
    """Función principal del agente avanzado"""
    print("🚀 AGENTE CONVERSACIONAL AVANZADO - AZURE OPENAI")
    print("=" * 60)
    print("Versión completa con todas las características avanzadas")
    print()
    
    # Verificar entorno
    if not check_environment():
        print("\nEl entorno no está configurado correctamente")
        return 1
    
    # Verificar credenciales básicas
    try:
        from config import AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_API_KEY
        
        if AZURE_OPENAI_ENDPOINT.startswith('https://tu-') or len(AZURE_OPENAI_API_KEY) < 20:
            print("\nCredenciales de Azure OpenAI no configuradas")
            show_credentials_help()
            
            response = input("\n¿Continuar de todos modos? (y/N): ").strip().lower()
            if response != 'y':
                return 1
    
    except ImportError as e:
        print(f"Error importando configuración: {e}")
        return 1
    
    # Opción de ejecutar pruebas
    if len(sys.argv) > 1 and sys.argv[1] == '--test':
        success = run_tests()
        return 0 if success else 1
    
    # Mostrar información de inicio
    print("\nCARACTERÍSTICAS AVANZADAS HABILITADAS:")
    print("   Streaming de respuestas en tiempo real")
    print("   Configuración externa personalizable")
    print("   Métricas detalladas y logging")
    print("   Resúmenes automáticos de conversaciones")
    print("   Límites inteligentes de tokens")
    print("   Pruebas unitarias (ejecuta con --test)")
    
    # Importar y ejecutar el agente
    try:
        from cli_interface import main as run_advanced_agent
        
        print(f"\nIniciando agente...")
        print("Usa 'help' para ver todos los comandos disponibles")
        print("-" * 60)
        
        run_advanced_agent()
        return 0
        
    except KeyboardInterrupt:
        print("\n\n¡Hasta luego!")
        return 0
    except ImportError as e:
        print(f"Error importando componentes: {e}")
        return 1
    except Exception as e:
        print(f"Error inesperado: {e}")
        return 1


def show_help():
    """Mostrar ayuda del sistema"""
    print("AYUDA - AGENTE CONVERSACIONAL AVANZADO")
    print("=" * 60)
    print()
    print("MODO DE USO:")
    print("   python main.py           # Ejecutar agente")
    print("   python main.py --test    # Ejecutar pruebas")
    print("   python main.py --help    # Mostrar esta ayuda")
    print()
    print("COMANDOS DURANTE LA EJECUCIÓN:")
    print("   help                    # Ayuda completa")
    print("   exit / quit            # Salir con resumen")
    print("   clear                  # Limpiar memoria corta")
    print("   history [N]            # Mostrar últimas N conversaciones")
    print("   config                 # Ver/cambiar configuración")
    print("   metrics               # Dashboard de métricas")
    print("   info                  # Información del sistema")
    print()
    print("CONFIGURACIÓN:")
    print("   config temp 0.8       # Cambiar temperatura")
    print("   config tokens 2000    # Cambiar max_tokens")
    print("   config stream on/off  # Activar/desactivar streaming")
    print()
    print("ARCHIVOS IMPORTANTES:")
    print("   config/model_config.json    # Configuración del modelo")
    print("   config/system_prompt.txt    # Prompt del sistema")
    print("   data/conversation_history.json  # Historial de conversaciones")
    print("   data/metrics.json           # Métricas de uso")
    print("   logs/agent.log             # Logs del sistema")
    print()
    print("CREDENCIALES:")
    print("   Configura variables de entorno o edita src/config.py")
    print("   Necesitas: endpoint, api_key, deployment_name")
    print("=" * 60)


if __name__ == "__main__":
    # Mostrar ayuda si se solicita
    if len(sys.argv) > 1 and sys.argv[1] in ['--help', '-h', 'help']:
        show_help()
        sys.exit(0)
    
    # Ejecutar función principal
    exit_code = main()
    sys.exit(exit_code)