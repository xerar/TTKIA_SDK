from ttkia_sdk.client import TtkIAAssistant
import os
from dotenv import load_dotenv

load_dotenv()

client = TtkIAAssistant(
    base_url=os.getenv('TTKIA_BASE_URL'),
    app_token=os.getenv('TTKIA_APP_TOKEN'),
    log_level="INFO"
)

print("="*60)
print("EJEMPLOS DE USO CON DIFERENTES CONFIGURACIONES")
print("="*60)

# 1. Comando simple (defaults)
print("\n1️⃣  Comando simple (defaults)")
result = client.use_command("analizar_logs")
print(result['response_text'][:200] + "...")

# 2. Con contexto adicional
print("\n2️⃣  Con contexto adicional")
result = client.use_command(
    "analizar_logs",
    additional_context="Error en servidor web nginx - línea 245: connection timeout"
)
print(result['response_text'][:200] + "...")

# 3. Con web search (para info actualizada)
print("\n3️⃣  Con búsqueda web activada")
result = client.use_command(
    "vulnerabilidades_cisco",
    web_search=True
)
print(result['response_text'][:200] + "...")
print(f"Webs consultadas: {len(result.get('webs', []))}")

# 4. Modo profesor (query extendida + reasoning)
print("\n4️⃣  Modo profesor (teacher_mode)")
result = client.use_command(
    "catalyst",
    teacher_mode=True,
    style="detailed"
)
print(f"Query original: {result.get('query', 'N/A')[:100]}...")
print(f"Query extendida: {result.get('query_extended', 'N/A')[:100]}...")
print(f"Thinking steps: {len(result.get('thinking_process', []))}")
print(result['response_text'][:200] + "...")

# 5. Comando en workspace con archivos
print("\n5️⃣  Comando en workspace con archivos")
workspace = client.new_workspace()
conv_id = workspace['conversation_id']

# Subir archivos al workspace
# client.upload_file("config.json", conversation_id=conv_id)
# client.upload_file("logs.txt", conversation_id=conv_id)

result = client.use_command(
    "revisar_codigo",
    conversation_id=conv_id,
    additional_context="Revisar problemas de seguridad",
    style="technical"
)
print(result['response_text'][:200] + "...")

# 6. TODO junto: web search + teacher mode + style + contexto
print("\n6️⃣  Configuración completa")
result = client.use_command(
    "diagnostico_red",
    additional_context="Red empresarial con IP 192.168.1.100 presenta intermitencia",
    web_search=True,
    teacher_mode=True,
    style="technical"
)
print(f"Confidence: {result.get('confidence', 'N/A')}")
print(f"Documentos usados: {len(result.get('docs', []))}")
print(f"Web sources: {len(result.get('webs', []))}")
print(f"Thinking steps: {len(result.get('thinking_process', []))}")
print(result['response_text'][:300] + "...")

print("\n" + "="*60)
print("✅ EJEMPLOS COMPLETADOS")
print("="*60)