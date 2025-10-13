import os
from dotenv import load_dotenv
from ttkia_sdk.client import TtkIAAssistant
import time
from typing import Optional, List, Dict, Any, Union
 
# Cargar variables de entorno desde .env
load_dotenv()

# Configuración inicial desde variables de entorno
BASE_URL = os.getenv('TTKIA_BASE_URL')
TOKEN = os.getenv('TTKIA_APP_TOKEN')
LOG_LEVEL = os.getenv('TTKIA_LOG_LEVEL', 'INFO').upper()

# Validar que las variables estén configuradas
if not BASE_URL:
    raise ValueError("❌ TTKIA_BASE_URL no está configurada en el archivo .env")
if not TOKEN:
    raise ValueError("❌ TTKIA_APP_TOKEN no está configurada en el archivo .env")

print(f"🔑 Token configurado: {'✅ SI' if TOKEN else '❌ NO'}")

def print_separator(title):
    """Imprime un separador visual para las secciones"""
    print("\n" + "="*80)
    print(f"🔹 {title}")
    print("="*80)

def print_query_conditions(query_text, conversation_id, prompt, style, teacher_mode, web_search, sources_count, title):
    """Imprime las condiciones de la consulta de manera clara y destacada"""
    print("="*80)
    print(" CONDICIONES DE LA CONSULTA")
    print("="*80)
    
    # Información básica de la consulta
    print(f" PREGUNTA: '{query_text}'")
    print(f" WORKSPACE ID: {conversation_id}")
    print(f" TÍTULO: {title}")
    print("-" * 80)
    
    # Configuración de comportamiento
    print("⚙️  CONFIGURACIÓN DE COMPORTAMIENTO:")
    print(f"   Estilo: {style}")
    print(f"   Prompt: {prompt}")
    print(f"   Modo Extendido: {'✅ ACTIVADO' if teacher_mode else '❌ DESACTIVADO'}")
    print(f"   Búsqueda Web: {'✅ ACTIVADO' if web_search else '❌ DESACTIVADO'}")
    print(f"   Fuentes Disponibles: {sources_count} documentos")
    print("-" * 80)
    
    # Expectativas
    print("🔍 EXPECTATIVAS DE LA RESPUESTA:")
    if teacher_mode:
        print("   Modo Extendido (CoT): Razonamiento paso a paso explícito")
        print("   Debería mostrar proceso de pensamiento estructurado")
        print("   Secciones THINKING y ANSWER claramente separadas")
    if web_search:
        print("   Debería incluir información actualizada de internet")
        print("   Enlaces y referencias web en la respuesta")
    if sources_count > 0:
        print(f"   Debería referenciar documentos de la base de conocimiento")
        print(f"   Citas de los {sources_count} documentos disponibles")
    
    print("="*80)

def print_response_analysis(response, query_description, teacher_mode_param=False):
    """Analiza y muestra la respuesta de manera detallada para verificar condiciones"""
    print("="*80 )
    print("📈 ANÁLISIS DE LA RESPUESTA")
    print("="*80 )
    
    # Mostrar la respuesta principal
    response_text = response.get('response_text', '[Sin respuesta]')
    print(f"\n💬 RESPUESTA COMPLETA:")
    print("-"*80)
    print(response_text)
    print("-"*80)
    
    # Análisis de cumplimiento de condiciones
    print("\n✅❌ VERIFICACIÓN DE CONDICIONES:\n")
    
    # Verificar si hay referencias a documentos
    documents_used = response.get('docs', [])
    links_used = response.get('links', [])
    web_results = response.get('webs', [])
    
    print(f"📚 Documentos RAG utilizados: {len(documents_used)}")
    if documents_used:
        print("   ✅ CORRECTO: Se usó la base de conocimiento")
        for i, doc in enumerate(documents_used[:3], 1):
            doc_name = doc.get('source', doc.get('title', 'Documento sin nombre'))
            print(f"      [{i}] {doc_name}")
        if len(documents_used) > 3:
            print(f"      ... y {len(documents_used) - 3} documentos más")
    else:
        print("   ⚠️  ATENCIÓN: No se utilizaron documentos de la base de conocimiento")
    
    print(f"🔗 Enlaces estáticos utilizados: {len(links_used)}")
    if links_used:
        print("   ✅ CORRECTO: Se usaron enlaces de referencia")
        for i, link in enumerate(links_used[:3], 1):
            link_name = link.get('source', link.get('title', 'Enlace sin nombre'))
            print(f"      [{i}] {link_name}")
        if len(links_used) > 3:
            print(f"      ... y {len(links_used) - 3} enlaces más")
    
    print(f"🌐 Resultados web utilizados: {len(web_results)}")
    if web_results:
        print("   ✅ CORRECTO: Se realizó búsqueda web como se solicitó")
        for i, result in enumerate(web_results[:2], 1):
            title = result.get('title', 'Sin título')
            print(f"      [{i}] {title[:50]}...")
    else:
        print("   ❌ PROBLEMA: No se encontraron resultados web (¿estaba activado web_search?)")
    
    # Verificar calidad de respuesta
    confidence = response.get('confidence')
    if confidence:
        confidence_val = confidence if isinstance(confidence, (int, float)) else 0
        if confidence_val >= 0.8:
            print(f"  Confianza: {confidence} ✅ ALTA CONFIANZA")
        elif confidence_val >= 0.6:
            print(f"  Confianza: {confidence} ⚠️  CONFIANZA MEDIA")
        else:
            print(f"  Confianza: {confidence} ❌ BAJA CONFIANZA")
    else:
        print("  Confianza: No disponible")
    
    # Verificar entornos inferidos
    inferred_envs = response.get('inferred_environments', [])
    if inferred_envs:
        print(f"  Entornos inferidos: {', '.join(inferred_envs)} ✅")
    else:
        print("  Entornos inferidos: Ninguno ⚠️")
    
    # Metadatos técnicos
    print(f"\n🔧 METADATOS TÉCNICOS:")
    print(f"   🆔 ID Conversación: {response.get('conversation_id', 'N/A')}")
    print(f"   🆔 ID Mensaje: {response.get('message_id', 'N/A')}")
    
    # Análisis del texto para modo extendido (CoT)
    if teacher_mode_param:
        # Verificar si existe thinking_process (campo clave de CoT)
        thinking_process = response.get('thinking_process', [])
        
        if thinking_process and len(thinking_process) > 0:
            print("   Modo Extendido (CoT): ✅ thinking_process presente")
            print(f"      Número de pasos: {len(thinking_process)}")
            # Mostrar el primer paso del thinking_process
            for i in range(len(thinking_process)):
                step = thinking_process[i]
                if isinstance(step, str):
                    print(f"      Paso {i+1}: {step[:150].replace('\n', ' ')}...")
                else:
                    print(f"      Paso {i+1}: {str(step)[:150]}...")
        else:
            print("   Modo Extendido (CoT): ❌ NO hay thinking_process")
    else:
        print("   Modo Extendido (CoT): ❌ No activado en esta consulta")

    print("="*80)

def wait_between_queries(seconds=2):
    """Espera entre consultas para no saturar el servidor"""
    print(f"⏱️  Esperando {seconds} segundos...")
    time.sleep(seconds)


# Inicializar el asistente
assistant = TtkIAAssistant(
    base_url=BASE_URL,
    app_token=TOKEN,
    log_level=LOG_LEVEL,  
    logger_name="my_ttkia_client"
)

conversation_id = None

try:
    print_separator("INICIALIZACIÓN Y AUTENTICACIÓN")
    
    print("🔐 Iniciando sesión...")
    if not assistant.is_authenticated():
        raise Exception("Error en la autenticación")
    print("✅ Conexión exitosa")

    # Obtener estilos y prompts disponibles
    print("\n🎨 Obteniendo configuración disponible...")
    styles = assistant.get_styles()
    prompts = assistant.get_prompts()
    
    available_styles = [style['id'] for style in styles['styles']]
    available_prompts = [prompt['id'] for prompt in prompts['prompts']]
    
    print(f"📋 Estilos disponibles: {available_styles}")
    print(f"🎯 Prompts disponibles: {available_prompts}")
    
    # Usar el primer estilo y prompt disponible como defaults
    default_style = available_styles[0] if available_styles else "default"
    default_prompt = available_prompts[0] if available_prompts else "default"
    
    print(f"✅ Usando por defecto - Estilo: '{default_style}', Prompt: '{default_prompt}'")

    # Obtener fuentes disponibles una vez para todas las consultas
    print("\n📚 Obteniendo fuentes disponibles...")
    all_sources = assistant.get_sources()
    sources_list = [source.get('title', '') for source in all_sources if source.get('title')]
    print(f"📖 Fuentes encontradas: {len(sources_list)} archivos")
    print(f"📋 Primeras 3 fuentes: {sources_list[:3]}")

    print_separator("CREANDO WORKSPACE ÚNICO PARA TODAS LAS PRUEBAS")

    # Crear nuevo workspace que usaremos para todo
    ws = assistant.new_workspace()
    conversation_id = ws.get("conversation_id")
    print(f"✅ Workspace creado: {conversation_id}")
    print("🎯 Todas las consultas se realizarán en este workspace")

    # Mostrar detalles del workspace inicial
    print(f"\n🔍 Estado inicial del workspace:")
    conv_details = assistant.show_conversation(conversation_id)
    messages_count = len(conv_details.get('messages', []))
    print(f"  📨 Número de mensajes: {messages_count}")
    print(f"  📅 Creada: {conv_details.get('created_at', 'N/A')}")
    print(f"  📝 Título: {conv_details.get('title', 'N/A')}")

    print_separator("PRUEBA 1: CONSULTA CON ANÁLISIS COMPLETO")

    # Parámetros de la consulta
    QUERY = "¿Qué sabemos de Fortimanager?"
    STYLE = available_styles[1] if len(available_styles) > 1 else default_style
    PROMPT = default_prompt
    TEACHER_MODE = True
    WEB_SEARCH = True
    TITLE = "CONSULTA API BASICA"
    
    # 🎯 MOSTRAR CONDICIONES ANTES DE LA CONSULTA
    print_query_conditions(
        query_text=QUERY,
        conversation_id=conversation_id,
        prompt=PROMPT,
        style=STYLE,
        teacher_mode=TEACHER_MODE,
        web_search=WEB_SEARCH,
        sources_count=len(sources_list),
        title=TITLE
    )
    
    print("\n🚀 Ejecutando consulta...")
    
    # Realizar la consulta
    query1_response = assistant.query(
        query_text=QUERY,
        conversation_id=conversation_id,
        prompt=PROMPT,
        style=STYLE,
        sources=sources_list,  # 📚 Pasar todas las fuentes
        teacher_mode=TEACHER_MODE,     # 👨‍🏫 Activamos modo teacher
        web_search=WEB_SEARCH,
        title=TITLE
    )
    
    # 📊 MOSTRAR ANÁLISIS DESPUÉS DE LA RESPUESTA
    print_response_analysis(query1_response, QUERY, teacher_mode_param=TEACHER_MODE)
    
    wait_between_queries()

    print_separator("PRUEBA 2: CONSULTA SIN WEB SEARCH (MISMO WORKSPACE)")

    # Segunda consulta para comparar
    QUERY2 = "¿Cómo se configura un firewall básico?"
    TEACHER_MODE2 = False
    WEB_SEARCH2 = False
    STYLE2 = default_style
    TITLE2 = "CONSULTA SIN WEB"
    PROMPT2 = default_prompt

    print_query_conditions(
        query_text=QUERY2,
        conversation_id=conversation_id,
        prompt=PROMPT2,
        style=STYLE2,
        teacher_mode=TEACHER_MODE2,
        web_search=WEB_SEARCH2,
        sources_count=len(sources_list),
        title=TITLE2
    )
    
    print("\n🚀 Ejecutando segunda consulta en el mismo workspace...")
    
    query2_response = assistant.query(
        query_text=QUERY2,
        conversation_id=conversation_id,
        prompt=PROMPT2,
        style=STYLE2,
        sources=sources_list,
        teacher_mode=TEACHER_MODE2,
        web_search=WEB_SEARCH2,
        title=TITLE2
    )
    
    print_response_analysis(query2_response, QUERY2, teacher_mode_param=TEACHER_MODE2)
    
    wait_between_queries()

    print_separator("PRUEBA 3: CONSULTA CON ARCHIVO ADJUNTO (MISMO WORKSPACE)")
    
    # Segunda consulta para comparar
    QUERY3 = "¿Podrías resumir el contenido del archivo adjunto prueba.txt?"
    TEACHER_MODE3 = False
    WEB_SEARCH3 = False
    STYLE3 = default_style
    TITLE3 = "CONSULTA ARCHIVO ADJUNTO"
    PROMPT3 = default_prompt

    # Subir archivo a la conversación en curso
    print("📎 Subiendo archivo ./prueba.txt al workspace activo...")
    upload_result = assistant.upload_file(
        file_path="./prueba.txt",
        conversation_id=conversation_id
    )
    print(f"✅ Archivo subido: {upload_result.get('name')}")

    # Obtener lista de adjuntos de la conversación
    print("\n📋 Lista de adjuntos en el workspace:")
    attachments = assistant.get_attachments(conversation_id)
    for i, att in enumerate(attachments, 1):
        print(f"   [{i}] {att.get('name')} ({att.get('size')} bytes)")

    print_query_conditions(
        query_text=QUERY3,
        conversation_id=conversation_id,
        prompt=PROMPT3,
        style=STYLE3,
        teacher_mode=TEACHER_MODE3,
        web_search=WEB_SEARCH3,
        sources_count=len(sources_list),
        title=TITLE3
    )
    
    print("\n🚀 Consultando sobre el archivo adjunto en el mismo workspace...")
    
    query3_response = assistant.query(
        query_text=QUERY3,
        conversation_id=conversation_id,
        prompt=PROMPT3,
        style=STYLE3,
        sources=sources_list,
        teacher_mode=TEACHER_MODE3,
        web_search=WEB_SEARCH3,
        title=TITLE3
    )

    print_response_analysis(query3_response, "Consulta archivo adjunto")

    wait_between_queries()

    print_separator("ESTADO FINAL DEL WORKSPACE")

    # Mostrar estado final del workspace antes de borrarlo
    print(f"📊 Estado final del workspace {conversation_id}:")
    final_conv_details = assistant.show_conversation(conversation_id)
    final_messages_count = len(final_conv_details.get('messages', []))
    final_attachments_count = len(final_conv_details.get('file_attachments', []))
    
    print(f"  📨 Total de mensajes: {final_messages_count}")
    print(f"  📎 Total de adjuntos: {final_attachments_count}")
    print(f"  📅 Última actualización: {final_conv_details.get('updated_at', 'N/A')}")
    
    # Mostrar los mensajes del workspace
    messages = final_conv_details.get('messages', [])
    print(f"\n📝 Historial de mensajes del workspace:")
    for i, msg in enumerate(messages, 1):
        role = msg.get('role', 'unknown')
        content_preview = msg.get('content', '')[:50].replace('\n', ' ')
        timestamp = msg.get('timestamp', 'N/A')
        print(f"   [{i}] {role}: {content_preview}... ({timestamp})")

except Exception as e:
    print(f"\n❌ Error durante la ejecución: {e}")
    print(f"📍 Tipo de error: {type(e).__name__}")
    import traceback
    print(f"🔍 Traceback completo:")
    traceback.print_exc()

finally:
    print_separator("LIMPIEZA Y CIERRE")
    
    # Borrar el workspace de pruebas
    if conversation_id:
        try:
            print(f"🗑️  Borrando workspace de pruebas: {conversation_id}")
            delete_success = assistant.delete_conversation(conversation_id)
            if delete_success:
                print("✅ Workspace borrado exitosamente")
            else:
                print("⚠️  No se pudo confirmar el borrado del workspace")
        except Exception as delete_error:
            print(f"❌ Error borrando workspace: {delete_error}")
    
    
    print("\n🏁 Script de pruebas finalizado.")
    print("🧹 Workspace de pruebas eliminado - no hay basura en el backend")
    print("📝 Revisa los logs del servidor para información adicional.")
