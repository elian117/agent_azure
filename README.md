# Agente Conversacional Avanzado - Azure OpenAI

Un agente conversacional CLI de nivel empresarial con características avanzadas que utiliza Azure OpenAI GPT-4 e implementa un sistema completo de memoria inteligente, streaming, métricas y configuración externa.

## Características Avanzadas Implementadas

### **Búsqueda Inteligente en Memoria**
- **Búsqueda por relevancia** usando TF-IDF simplificado
- **Contexto inteligente** que combina memoria reciente + conversaciones relevantes  
- **Filtrado de stop words** para búsquedas más precisas
- **Scoring de relevancia** para priorizar resultados

### **Streaming de Respuestas**  
- **Respuestas en tiempo real** - texto aparece mientras se genera
- **Indicadores visuales** de procesamiento y streaming
- **Fallback automático** a modo no-streaming si hay errores
- **Control total** del streaming desde configuración externa

### **Configuración Externa**
- **System prompt configurable** desde archivo `config/system_prompt.txt`
- **Parámetros del modelo** configurables en `config/model_config.json`
- **Cambios en tiempo real** sin reiniciar la aplicación
- **Validación automática** de parámetros

### **Gestión Avanzada de Memoria**
- **Resumenes automáticos** de conversaciones antiguas
- **Límites inteligentes de tokens** con truncado contextual
- **Agrupación por períodos** para optimizar almacenamiento
- **Análisis de temas principales** en resúmenes

### **Testing y Calidad**
- **Pruebas unitarias completas** para componentes críticos
- **Cobertura de funciones** principales del sistema de memoria
- **Mocks y fixtures** para testing aislado
- **Validación de configuración** automatizada

### **Logging y Métricas**
- **Sistema de logs estructurado** con diferentes niveles
- **Métricas detalladas** de tokens, tiempo de respuesta, errores
- **Dashboard en tiempo real** de estadísticas de uso
- **Exportación de métricas** por períodos configurables
- **Retención automática** de logs y métricas

## Arquitectura del Sistema

```
agente-conversacional-advanced/
├── main.py                # Punto de entrada principal
├── requirements.txt       # Dependencias 
├── README.md              # Esta documentación
├── src/
│   ├── config.py                   # Configuración avanzada + ConfigManager
│   ├── memory_system.py   # Sistema de memoria con búsqueda inteligente
│   ├── azure_client.py    # Cliente Azure con streaming + métricas
│   ├── metrics_logger.py           # Sistema de métricas y logging
│   └── cli_interface.py   # Interfaz CLI con comandos avanzados
├── config/
│   ├── system_prompt.txt          # System prompt personalizable
│   └── model_config.json          # Parámetros del modelo
├── data/
│   ├── conversation_history.json  # Historial completo de conversaciones
│   ├── conversation_summaries.json # Resúmenes automáticos
│   └── metrics.json               # Métricas de uso
├── logs/
│   └── agent.log                  # Logs estructurados del sistema
```

## 🚀 Instalación y Configuración

### 1. **Clonar y preparar entorno**
```bash
git clone <repositorio>
cd agente-conversacional-advanced
pip install -r requirements.txt
```

### 2. **Configurar credenciales de Azure OpenAI**

**Opción A: Variables de entorno**
```bash
export AZURE_OPENAI_ENDPOINT="https://recurso.azure.com"
export AZURE_OPENAI_API_KEY="api-key"
export AZURE_OPENAI_DEPLOYMENT_NAME="gpt-4"
export AZURE_OPENAI_API_VERSION="2024-06-01"
```

**Opción B: Editar src/config.py**
```python
AZURE_OPENAI_ENDPOINT = "https://recurso.azure.com"
AZURE_OPENAI_API_KEY = "api-key"
AZURE_OPENAI_DEPLOYMENT_NAME = "gpt-4"
AZURE_OPENAI_API_VERSION = "2024-06-01"
```

### 3. **Ejecutar agente**
```bash
python main.py
```

### 4. **Ejecutar pruebas (opcional)**
```bash
python main.py --test
```

## 🎮 Comandos Avanzados

### **Comandos Básicos**
```bash
help                    # Ayuda completa con ejemplos
exit / quit            # Salir con resumen detallado de sesión
clear                  # Limpiar memoria de corto plazo

```

### **Gestión de Memoria**
```bash
history                # Mostrar últimas 8 conversaciones
history 15            # Mostrar últimas 15 conversaciones
```

### **Configuración Dinámica**
```bash
config                # Ver configuración actual
config temp 0.8       # Cambiar temperatura (creatividad)
config tokens 2000    # Cambiar límite de tokens de respuesta
config stream on      # Activar streaming de respuestas
config stream off     # Desactivar streaming
config top_p 0.9      # Cambiar parámetro top_p
```

### **Métricas y Monitoring**
```bash
metrics               # Dashboard completo de métricas
info                  # Información técnica del sistema
```

## Configuración Avanzada

### **Personalizar System Prompt**
Edita `config/system_prompt.txt`:
```
Eres un asistente especializado en [tu dominio].

Características especiales:
- Experto en [área específica]
- Siempre proporcionas ejemplos prácticos  
- Referencias fuentes cuando es posible

Responde siempre en español y mantén un tono [profesional/casual].
```

### **Ajustar Parámetros del Modelo**
Edita `config/model_config.json`:
```json
{
  "temperature": 0.8,
  "max_tokens": 2000,
  "top_p": 0.9,
  "frequency_penalty": 0.1,
  "presence_penalty": 0.1,
  "stream": true
}
```

### **Configurar Memoria y Métricas**
En `src/config.py`:
```python
# Memoria
SHORT_TERM_MEMORY_LIMIT = 20           # Más contexto
RELEVANCE_SEARCH_LIMIT = 8             # Más resultados de búsqueda  
MAX_CONTEXT_TOKENS = 8000              # Mayor contexto

# Métricas
ENABLE_METRICS = True                   # Activar métricas
METRICS_RETENTION_DAYS = 60             # Retener por más tiempo
```

## Testing y Calidad

### **Ejecutar Pruebas**
```bash
# Todas las pruebas
python main.py --test

# Pruebas específicas con pytest (si está instalado)
pytest tests/ -v

# Con cobertura
pytest tests/ --cov=src --cov-report=html
```

### **Pruebas Incluidas**
- ✅ **TestMemorySystem**: Sistema de memoria avanzado
- ✅ **TestConfigManager**: Gestor de configuración
- ✅ **TestMetricsLogger**: Sistema de métricas
- ✅ **Búsqueda por relevancia**: Algoritmo TF-IDF
- ✅ **Persistencia**: Carga/guardado de datos
- ✅ **Validación**: Parámetros de configuración

## 📊 Métricas y Monitoreo

### **Métricas Capturadas**
- **Por interacción**: tokens entrada/salida, tiempo respuesta
- **Por sesión**: duración, total interacciones, errores
- **Globales**: uso histórico, tendencias, rendimiento
- **Errores**: tipos, frecuencia, contexto

### **Logs Estructurados**
```
2024-01-15 14:23:45 - memory_system - INFO - Memoria cargada: 45 conversaciones
2024-01-15 14:23:47 - azure_client - INFO - Respuesta generada - 287 tokens, 2.3s
2024-01-15 14:23:47 - metrics_logger - DEBUG - Métricas registradas: 287 tokens
```
### **Problemas de Configuración**  
```bash
# Verificar configuración actual
👤 Tú: config

# Resetear a valores por defecto
rm config/model_config.json
python main.py  # Se recreará automáticamente
```

### **Problemas de Streaming**
```bash
# Desactivar streaming si hay problemas
👤 Tú: config stream off

# Verificar en logs
tail -f logs/agent.log
```

### **Debugging Avanzado**
```python
# En src/config.py, cambiar nivel de log
LOG_LEVEL = "DEBUG"  # Más detalle en logs

# Ver métricas detalladas
👤 Tú: metrics
```

## Optimizaciones de Rendimiento

### **Para Uso Intensivo**
- Aumentar `MAX_CONTEXT_TOKENS` para más contexto
- Activar resúmenes automáticos más frecuentes
- Configurar retención de métricas según necesidades

### **Para Recursos Limitados**
- Reducir `SHORT_TERM_MEMORY_LIMIT`
- Desactivar streaming: `"stream": false`
- Configurar `ENABLE_METRICS = False`

## Características Técnicas Destacadas

### **Streaming Robusto**
- Manejo de chunks de texto en tiempo real
- Fallback automático en caso de errores
- Control granular de la experiencia de usuario

### **Gestión Inteligente de Tokens**
- Estimación precisa de tokens por mensaje
- Truncado contextual preservando información relevante
- Límites dinámicos según configuración

### **Arquitectura Modular**
- Separación clara de responsabilidades
- Interfaces bien definidas entre componentes
- Fácil extensibilidad y mantenimiento

---
