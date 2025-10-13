import requests
import hashlib
import json
import logging
from typing import Optional, List, Dict, Any, Union
from pathlib import Path
import mimetypes


class TtkIAAssistant:
    """
    SDK para interactuar con la API de TtkIA.
    
    Características:
    - Logging configurable con diferentes niveles de verbosidad
    - Manejo de errores mejorado
    - Interfaz limpia sin prints hardcodeados
    - Configuración flexible de timeouts y reintentos
    """
    def __init__(
        self, 
        base_url: str, 
        app_token: str,  
        log_level: Union[str, int] = "INFO",
        logger_name: str = "ttkia_sdk",
        timeout: int = 30,
        max_retries: int = 3
    ):
        self.base_url = base_url.rstrip("/")
        self.app_token = app_token
        self.timeout = timeout
        self.max_retries = max_retries
        
        # Configurar logging
        self._setup_logger(logger_name, log_level)
        
        # Configurar session CON token desde el inicio
        self.session = requests.Session()
        self.session.timeout = self.timeout
        self.session.headers.update({
            "Authorization": f"Bearer {self.app_token}"
        })
        
        self.logger.info(f"TtkIA SDK inicializado para {self.base_url}")
        
        self._initialize_session()

    def _initialize_session(self):
        """Inicializar sesión llamando a /env"""
        try:
            response = self._make_request("POST", "/env")
            result = response.json()
            self.logger.info(f"✅ Sesión inicializada correctamente")
            return result
        except Exception as e:
            self.logger.warning(f"⚠️ No se pudo inicializar sesión: {e}")
            return None

    def _setup_logger(self, logger_name: str, log_level: Union[str, int]) -> None:
        """Configura el sistema de logging."""
        self.logger = logging.getLogger(logger_name)
        
        # Evitar duplicar handlers si ya existe
        if not self.logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
        
        # Convertir string a nivel numérico si es necesario
        if isinstance(log_level, str):
            level = getattr(logging, log_level.upper(), logging.INFO)
        else:
            level = log_level
            
        self.logger.setLevel(level)
        self.logger.debug(f"Logger configurado con nivel {level}")

    def set_log_level(self, log_level: Union[str, int]) -> None:
        """
        Cambia el nivel de logging dinámicamente.
        
        Args:
            log_level: Nivel como string ("DEBUG", "INFO", etc.) o entero
        """
        if isinstance(log_level, str):
            level = getattr(logging, log_level.upper(), logging.INFO)
        else:
            level = log_level
            
        self.logger.setLevel(level)
        self.logger.info(f"Nivel de logging cambiado a {logging.getLevelName(level)}")

    def _make_request(
        self, 
        method: str, 
        url: str, 
        data: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        headers: Optional[Dict] = None
    ) -> requests.Response:
        """
        Realiza una petición HTTP con manejo de errores y logging.
        
        Args:
            method: Método HTTP (GET, POST, etc.)
            url: URL completa del endpoint
            data: Datos para enviar como form data
            json_data: Datos para enviar como JSON
            headers: Headers adicionales
            
        Returns:
            Response object
            
        Raises:
            requests.RequestException: En caso de error en la petición
        """
        full_url = f"{self.base_url}{url}" if not url.startswith('http') else url
        
        request_headers = headers or {}
        if json_data:
            request_headers.setdefault('Content-Type', 'application/json')
        
        self.logger.debug(f"Realizando {method} a {full_url}")
        
        try:
            response = self.session.request(
                method=method,
                url=full_url,
                data=json.dumps(data) if data else None,
                json=json_data,
                headers=request_headers
            )
            
            self.logger.debug(f"Respuesta: {response.status_code}")
            
            if self.logger.level <= logging.DEBUG:
                # Solo mostrar contenido de respuesta en modo DEBUG
                content_preview = str(response.text)[:200]
                self.logger.debug(f"Contenido de respuesta: {content_preview}...")
            
            response.raise_for_status()
            return response
            
        except requests.RequestException as e:
            self.logger.error(f"Error en petición {method} {full_url}: {e}")
            raise


    def get_session_info(self) -> Dict[str, Any]:
        """Información de la sesión con App Token."""
        return {
            "authenticated": self.is_authenticated(),
            "base_url": self.base_url,
            "app_token_present": bool(self.app_token),
            "timeout": self.timeout
        }


    def get_conversations(self) -> List[Dict[str, Any]]:
        """
        Obtiene la lista de conversaciones del usuario.
        
        Returns:
            Lista de conversaciones
        """
        try:
            response = self._make_request("GET", "/auth/users/me")
            user_data = response.json()
            
            history_chat = user_data.get('history_chat', {})
            conversations = history_chat.get('conversations', [])
            
            self.logger.info(f"Obtenidas {len(conversations)} conversaciones")
            return conversations
            
        except Exception as e:
            self.logger.error(f"Error obteniendo conversaciones: {e}")
            return []

    def show_conversation(self, conversation_id: str) -> Dict[str, Any]:
        """
        Obtiene los detalles de una conversación específica.
        
        Args:
            conversation_id: ID de la conversación
            
        Returns:
            Datos de la conversación
        """
        try:
            payload = {"conversation_id": conversation_id}
            response = self._make_request(
                "POST", 
                "/conversation-info", 
                json_data=payload
            )
            
            self.logger.debug(f"Obtenida información de conversación: {conversation_id}")
            return response.json()
            
        except Exception as e:
            self.logger.error(f"Error obteniendo conversación {conversation_id}: {e}")
            raise

    def new_workspace(self) -> Dict[str, Any]:
        """
        Crea un nuevo workspace/conversación.
        
        Returns:
            Datos del nuevo workspace
        """
        try:
            response = self._make_request("POST", "/new-workspace")
            workspace_data = response.json()
            
            conversation_id = workspace_data.get('conversation_id', 'N/A')
            self.logger.info(f"Nuevo workspace creado: {conversation_id}")
            
            return workspace_data
            
        except Exception as e:
            self.logger.error(f"Error creando nuevo workspace: {e}")
            raise

    def get_sources(self) -> List[Dict[str, Any]]:
        """
        Obtiene las fuentes disponibles.
        
        Returns:
            Lista de fuentes disponibles
        """
        try:
            response = self._make_request("POST", "/get_sources")
            sources = response.json()
            
            if isinstance(sources, list):
                self.logger.info(f"Obtenidas {len(sources)} fuentes disponibles")
            else:
                self.logger.warning("Formato inesperado en respuesta de fuentes")
                
            return sources if isinstance(sources, list) else []
            
        except Exception as e:
            self.logger.error(f"Error obteniendo fuentes: {e}")
            return []

    def get_prompts(self) -> Dict[str, Any]:
        """
        Obtiene los prompts disponibles.
        
        Returns:
            Diccionario con prompts disponibles
        """
        try:
            response = self._make_request("GET", "/get_prompts")
            prompts = response.json()
            
            self.logger.info("Prompts obtenidos exitosamente")
            return prompts
            
        except Exception as e:
            self.logger.error(f"Error obteniendo prompts: {e}")
            return {}

    def get_styles(self) -> Dict[str, Any]:
        """
        Obtiene los estilos de respuesta disponibles.
        
        Returns:
            Diccionario con estilos disponibles
        """
        try:
            response = self._make_request("GET", "/get_styles")
            styles = response.json()
            
            self.logger.info("Estilos obtenidos exitosamente")
            return styles
            
        except Exception as e:
            self.logger.error(f"Error obteniendo estilos: {e}")
            return {}
    
    def upload_file(
        self,
        file_path: str,
        conversation_id: Optional[str] = None,
        custom_filename: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Sube un archivo al workspace/conversación especificada.
        
        Args:
            file_path: Ruta al archivo local que se desea subir
            conversation_id: ID de la conversación (opcional, se usará el activo si no se especifica)
            custom_filename: Nombre personalizado para el archivo (opcional)
            
        Returns:
            Diccionario con información del archivo subido
            
        Raises:
            FileNotFoundError: Si el archivo especificado no existe
            requests.RequestException: En caso de error en la petición
        """
        import os
        from pathlib import Path
        
        try:
            # Verificar que el archivo existe
            file_path_obj = Path(file_path)
            if not file_path_obj.exists():
                raise FileNotFoundError(f"El archivo {file_path} no existe")
            
            # Obtener información del archivo
            filename = custom_filename or file_path_obj.name
            file_size = file_path_obj.stat().st_size
            
            self.logger.info(f"Subiendo archivo: {filename} ({file_size} bytes)")
            
            # Preparar los datos del formulario
            files = {
                'file': (filename, open(file_path_obj, 'rb'), self._get_content_type(file_path_obj))
            }
            
            data = {}
            if conversation_id:
                data['conversation_id'] = conversation_id
            
            # Realizar la petición
            response = self.session.post(
                f"{self.base_url}/chat-upload",
                files=files,
                data=data,
                timeout=self.timeout
            )
            
            # Cerrar el archivo
            files['file'][1].close()
            
            self.logger.debug(f"Respuesta del servidor: {response.status_code}")
            response.raise_for_status()
            
            result = response.json()
            
            self.logger.info(f"Archivo subido exitosamente: {result.get('name', filename)}")
            self.logger.debug(f"Información del archivo: {result}")
            
            return result
            
        except FileNotFoundError:
            self.logger.error(f"Archivo no encontrado: {file_path}")
            raise
        except Exception as e:
            self.logger.error(f"Error subiendo archivo {file_path}: {e}")
            raise

    def _get_content_type(self, file_path: Path) -> str:
        """
        Determina el tipo de contenido MIME basado en la extensión del archivo.
        
        Args:
            file_path: Ruta del archivo
            
        Returns:
            Tipo de contenido MIME
        """
        import mimetypes
        
        # Mapeo de extensiones a tipos MIME comunes
        mime_types = {
            '.txt': 'text/plain',
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.ppt': 'application/vnd.ms-powerpoint',
            '.pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
            '.csv': 'text/csv',
            '.json': 'application/json',
            '.xml': 'application/xml',
            '.html': 'text/html',
            '.htm': 'text/html',
            '.md': 'text/markdown',
            '.rtf': 'application/rtf',
            '.odt': 'application/vnd.oasis.opendocument.text',
            '.ods': 'application/vnd.oasis.opendocument.spreadsheet',
            '.odp': 'application/vnd.oasis.opendocument.presentation',
            '.pbix': 'application/octet-stream'
        }
        
        extension = file_path.suffix.lower()
        
        # Intentar con nuestro mapeo personalizado primero
        if extension in mime_types:
            return mime_types[extension]
        
        # Usar mimetypes como fallback
        mime_type, _ = mimetypes.guess_type(str(file_path))
        return mime_type or 'application/octet-stream'

    def get_attachments(self, conversation_id: str) -> List[Dict[str, Any]]:
        """
        Obtiene la lista de archivos adjuntos de una conversación específica.
        
        Args:
            conversation_id: ID de la conversación
            
        Returns:
            Lista de archivos adjuntos
        """
        try:
            conversation_data = self.show_conversation(conversation_id)
            
            # La estructura correcta es file_attachments, no attachments.files
            attachments = conversation_data.get('file_attachments', [])
            
            self.logger.info(f"Obtenidos {len(attachments)} archivos adjuntos para conversación {conversation_id}")
            return attachments
            
        except Exception as e:
            self.logger.error(f"Error obteniendo adjuntos de conversación {conversation_id}: {e}")
            return []

    def query(
        self,
        query_text: str,
        conversation_id: Optional[str] = None,
        prompt: str = "default",
        style: str = "concise", 
        teacher_mode: bool = False,
        sources: Optional[List[str]] = None,
        attached_files: Optional[List[Dict[str, Any]]] = None,
        attached_urls: Optional[List[Dict[str, Any]]] = None,
        web_search: bool = False,
        title: Optional[str] = "New Query"
    ) -> Dict[str, Any]:
        """
        Realiza una consulta al asistente.
        
        Args:
            query_text: Texto de la consulta
            conversation_id: ID de la conversación (opcional)
            prompt: Prompt a usar (por defecto "default")
            style: Estilo de respuesta (por defecto "concise")
            teacher_mode: Activar modo profesor (por defecto False)
            sources: Lista de fuentes específicas a usar
            attached_files: Archivos adjuntos
            attached_urls: URLs adjuntas
            web_search: Activar búsqueda web (por defecto False)
            title: Título para la consulta
        
        Returns:
            Respuesta del asistente con metadatos
        """
        try:
            # Obtener fuentes automáticamente si no se proporcionan
            if sources is None:
                self.logger.debug("Obteniendo fuentes automáticamente")
                try:
                    all_sources = self.get_sources()
                    sources = [
                        source.get('title', '') 
                        for source in all_sources 
                        if source.get('title')
                    ]
                    self.logger.debug(f"Usando {len(sources)} fuentes automáticas")
                except Exception as e:
                    self.logger.warning(f"No se pudieron obtener fuentes automáticamente: {e}")
                    sources = []
            
            payload = {
                "query": query_text,
                "conversation_id": conversation_id,
                "prompt": prompt,
                "style": style,
                "teacher_mode": teacher_mode,
                "sources": sources or [],
                "attached_files": attached_files or [],
                "attached_urls": attached_urls or [],
                "web_search": web_search,
                "title": title
            }
            
            self.logger.info(f"Ejecutando consulta: '{query_text[:50]}...'")
            self.logger.debug(f"Parámetros: conversation_id={conversation_id}, "
                            f"prompt={prompt}, style={style}, web_search={web_search}")
            
            response = self._make_request(
                "POST", 
                "/query_complete", 
                json_data=payload
            )
            
            result = response.json()
            self.logger.info("Consulta completada exitosamente")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Error ejecutando consulta: {e}")
            raise

    def is_authenticated(self) -> bool:
        """
        Verifica si el cliente está autenticado.
        """
        if not self.app_token:
            return False
            
        try:
            response = self._make_request("GET", "/auth/users/me")
            if response.status_code == 200:
                return True
            else:
                self.logger.warning(f"Authentication failed: {response.status_code}")
                return False
        except requests.exceptions.HTTPError as e:
            if e.response and e.response.status_code == 401:
                self.logger.warning("Token is invalid or expired")
            else:
                self.logger.error(f"Authentication error: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Unexpected error during authentication check: {e}")
            return False

    def get_session_info(self) -> Dict[str, Any]:
        """
        Obtiene información sobre la sesión actual.
        
        Returns:
            Diccionario con información de la sesión
        """
        return {
            "authenticated": self.is_authenticated(),
            "username": self.username,
            "base_url": self.base_url,
            "app_token_present": bool(self.app_token),
            "timeout": self.timeout
        }

    def delete_conversation(self, conversation_id: str) -> bool:
        """
        Borra una conversación específica.
        
        Args:
            conversation_id: ID de la conversación a borrar
            
        Returns:
            True si se borró exitosamente, False en caso contrario
        """
        try:
            payload = {"conversation_id": conversation_id}
            
            response = self._make_request(
                "POST", 
                "/forget", 
                json_data=payload
            )
            
            self.logger.info(f"Conversación borrada exitosamente: {conversation_id}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error borrando conversación {conversation_id}: {e}")
            return False

    def get_quick_commands(self) -> Dict[str, Any]:
        """
        Obtiene TODOS los quick commands disponibles (propios y públicos).
        
        Returns:
            Dict con estructura:
            {
                "success": bool,
                "commands": [...],           # Lista de tus comandos
                "public_commands": [...],    # Lista de comandos públicos de otros usuarios
                "total": int,
                "max_commands": int,
                "available_slots": int
            }
            
            Cada comando contiene:
            - name: str
            - description: str
            - prompt: str
            - usage_count: int
            - is_public: bool
            - author: str (solo en públicos)
        """
        try:
            response = self._make_request("GET", "/commands/list")
            data = response.json()
            
            my_commands = data.get('commands', [])
            public_commands = data.get('public_commands', [])
            
            self.logger.info(
                f"Comandos obtenidos: {len(my_commands)} propios, "
                f"{len(public_commands)} públicos"
            )
            
            return data
            
        except Exception as e:
            self.logger.error(f"Error obteniendo quick commands: {e}")
            return {
                "success": False,
                "commands": [],
                "public_commands": [],
                "total": 0,
                "max_commands": 50,
                "available_slots": 50
            }


    def use_command(
        self,
        command_name: str,
        additional_context: str = "",
        conversation_id: Optional[str] = None,
        web_search: bool = False,
        teacher_mode: bool = False,
        style: str = "concise",
        prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Ejecuta un quick command (propio o público).
        
        El comando se ejecuta en el contexto del workspace especificado.
        Si el workspace tiene archivos adjuntos, el comando los usará automáticamente.
        
        Args:
            command_name: Nombre del comando (con o sin /)
            additional_context: Contexto adicional para el comando (opcional)
            conversation_id: ID del workspace/conversación (opcional)
                            - Si se proporciona: usa ese workspace
                            - Si no se proporciona: usa el workspace activo o crea uno nuevo
            web_search: Activar búsqueda web (default: False)
            teacher_mode: Activar modo profesor - query extendida + CoT (default: False)
            style: Estilo de respuesta - concise, detailed, technical, etc. (default: "concise")
            prompt: Prompt específico a usar (default: usa "default")
            
        Returns:
            Dict con la respuesta del asistente:
            {
                'success': bool,
                'conversation_id': str,
                'message_id': str,
                'query': str,
                'response_text': str,      # ← LA RESPUESTA
                'confidence': float,
                'recommended_response': str,
                'query_extended': str,     # Si teacher_mode=True
                'timing': dict,
                'docs': list,
                'webs': list,
                'links': list,
                'thinking_process': list   # Si teacher_mode=True
            }
            
        Raises:
            ValueError: Si el comando no existe
            
        Examples:
            >>> # Comando simple
            >>> result = client.use_command("analizar_logs")
            >>> print(result['response_text'])
            
            >>> # Con contexto adicional
            >>> result = client.use_command(
            ...     "analizar_logs",
            ...     additional_context="Error en línea 245"
            ... )
            
            >>> # Con búsqueda web para info actualizada
            >>> result = client.use_command(
            ...     "vulnerabilidades_cisco",
            ...     web_search=True
            ... )
            
            >>> # Modo profesor para aprender paso a paso
            >>> result = client.use_command(
            ...     "catalyst",
            ...     teacher_mode=True,
            ...     style="detailed"
            ... )
            
            >>> # Comando en workspace específico con todas las opciones
            >>> result = client.use_command(
            ...     "diagnostico_red",
            ...     additional_context="IP: 192.168.1.100",
            ...     conversation_id="conv-123",
            ...     web_search=True,
            ...     teacher_mode=True,
            ...     style="technical"
            ... )
        """
        # Buscar el comando (propio o público)
        clean_name = command_name.lower().lstrip('/')
        
        commands_data = self.get_quick_commands()
        cmd = None
        
        # Buscar en comandos propios
        for c in commands_data.get('commands', []):
            if c['name'].lower() == clean_name:
                cmd = c
                break
        
        # Si no está en propios, buscar en públicos
        if not cmd:
            for c in commands_data.get('public_commands', []):
                if c['name'].lower() == clean_name:
                    cmd = c
                    break
        
        # Error si no existe
        if not cmd:
            available_commands = [c['name'] for c in commands_data.get('commands', [])]
            available_public = [c['name'] for c in commands_data.get('public_commands', [])]
            
            error_msg = f"❌ Comando '/{clean_name}' no encontrado.\n\n"
            if available_commands:
                error_msg += f"Tus comandos disponibles: {', '.join(f'/{c}' for c in available_commands[:5])}\n"
            if available_public:
                error_msg += f"Comandos públicos: {', '.join(f'/{c}' for c in available_public[:5])}"
            
            self.logger.error(error_msg)
            raise ValueError(error_msg)
        
        # Construir query: prompt del comando + contexto adicional
        query_text = cmd['prompt']
        if additional_context:
            query_text = f"{query_text}\n\nContexto adicional:\n{additional_context}"
        
        # Log de ejecución con configuración
        cmd_type = "propio" if not cmd.get('author') else f"público (by {cmd['author']})"
        config_info = []
        if web_search:
            config_info.append("web_search")
        if teacher_mode:
            config_info.append("teacher_mode")
        if style != "concise":
            config_info.append(f"style={style}")
        
        config_str = f" [{', '.join(config_info)}]" if config_info else ""
        self.logger.info(f"Ejecutando comando /{cmd['name']} ({cmd_type}){config_str}")
        
        # Ejecutar usando query() con todas las opciones
        return self.query(
            query_text=query_text,
            conversation_id=conversation_id,
            prompt=prompt or "default",
            style=style,
            teacher_mode=teacher_mode,
            web_search=web_search,
            title=f"Comando: /{cmd['name']}"
        )