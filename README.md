# TTKIA SDK Client

Cliente oficial en Python para interactuar con la API de TTKIA.

## Características

- Autenticación vía token de aplicación (Bearer Token)
- Soporte completo para workspaces, consultas, prompts, estilos, adjuntos y más
- Logging configurable (DEBUG, INFO, WARNING...)
- Control de errores y manejo de sesiones con `requests`
- Soporte para subida de archivos y análisis de respuesta

## Instalación

```bash
pip install -r requirements.txt
```

## Configuración

Crea un archivo `.env` con tus credenciales:

```env
TTKIA_BASE_URL=URL_BASE_TTKIA
TTKIA_APP_TOKEN=TU_TOKEN_AQUI
TTKIA_LOG_LEVEL=INFO
```

## Uso básico

```python
from ttkia_sdk.client import TtkIAAssistant
from dotenv import load_dotenv
import os

load_dotenv()

assistant = TtkIAAssistant(
    base_url=os.getenv("TTKIA_BASE_URL"),
    app_token=os.getenv("TTKIA_APP_TOKEN"),
    log_level=os.getenv("TTKIA_LOG_LEVEL", "INFO")
)

# Crear nuevo workspace
ws = assistant.new_workspace()
conversation_id = ws["conversation_id"]

# Realizar una consulta
response = assistant.query(
    query_text="¿Qué es SD-WAN?",
    conversation_id=conversation_id,
    teacher_mode=True,
    web_search=True
)

print(response["response_text"])
```

## Uso avanzado

El archivo `example_script.py` incluye un recorrido completo por los métodos del SDK, incluyendo:

- `get_styles()` y `get_prompts()` para obtener configuraciones disponibles
- `get_sources()` para recuperar los documentos base RAG
- `upload_file()` para añadir documentos a una conversación
- `get_attachments()` para consultar archivos subidos
- `show_conversation()` para ver el estado del workspace
- `delete_conversation()` para limpieza al finalizar pruebas
- `is_authenticated()` y `get_session_info()` para verificación de sesión
- `get_conversations()` para obtener la lista de conversaciones

Además, se analiza en detalle cada respuesta (`response_text`, `docs`, `webs`, `confidence`, etc.), incluyendo condiciones esperadas para modo `teacher_mode`, uso de búsqueda web y referencias.

## Requisitos

- Python 3.7+
- requests
- python-dotenv

```bash
pip install requests python-dotenv
```

---

## Aviso
Este SDK está diseñado para usuarios con acceso autorizado a una instancia de TTKIA. El token de aplicación debe mantenerse confidencial.
