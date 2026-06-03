import os
from re import split

""" Required """

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GOOGLE_API_KEY = split(r'[,;，；]+', os.environ.get("GOOGLE_API_KEY"))

""" Optional """

ALLOWED_USERS = split(r'[ ,;，；]+', os.getenv("ALLOWED_USERS", '').replace("@", "").lower())
ALLOWED_GROUPS = [g.strip() for g in split(r'[,;，；]+', os.getenv("ALLOWED_GROUPS", '')) if g.strip()]

SYSTEM_INSTRUCTION = os.getenv("SYSTEM_INSTRUCTION", "")
DEFAULT_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.1-flash-lite")

# After setting up 3 rounds of dialogue, prompt the user to start a new dialogue
prompt_new_threshold = int(6)

# The default prompt when the photo has no accompanying text
default_photo_caption = "describe esta imagen"
# The default prompt for video messages
default_video_caption = "describe lo que está pasando en este video"
# The default prompt for audio/voice messages
default_audio_caption = "transcribe este audio"

""" Below is some text related to the user """
help_text = "Puedes enviarme texto o imágenes. Al enviar imágenes, incluye el texto en el mismo mensaje."
command_list = (
    "/new — Iniciar nuevo chat\n"
    "/get_model — Ver modelo actual\n"
    "/set_model — Cambiar modelo de Gemini\n"
    "/list_models — Listar modelos disponibles\n"
    "/get_my_info — Obtener tu ID de Telegram\n"
    "/help — Obtener ayuda"
)
command_format_error_info = "Error de formato en el comando"
command_invalid_error_info = "Comando inválido, usa /help para ayuda"
user_no_permission_info = "No tienes permiso para usar este bot."
gemini_err_info = "Algo salió mal. Por favor intenta de nuevo."
new_chat_info = "Empezamos un chat nuevo."
prompt_new_info = "Escribe /new para iniciar un chat nuevo."
unable_to_recognize_content_sent = "El contenido enviado no es reconocido."
group_not_allowed = "Este grupo no está autorizado. Por favor agrega el siguiente ID a la variable ALLOWED_GROUPS y redeploya:"
bot_joined_group = "¡Hola! Por favor agrega el siguiente ID de grupo a la variable ALLOWED_GROUPS y redeploya para activar este bot:"

""" Below is some text related to the log """
send_message_log = "Mensaje enviado. El contenido devuelto es:"
send_photo_log = "Foto enviada. El contenido devuelto es:"
unnamed_user = "UsuarioSinNombre"
event_received = "evento recibido"
the_content_sent_is = "El contenido enviado es:"
the_reply_content_is = "El contenido de respuesta es:"
the_accompanying_message_is = "El mensaje adjunto es:"
the_logarithm_of_historical_conversations_is = "El número de conversaciones históricas es:"
no_rights_to_use = "Sin permisos para usar"
send_unrecognized_content = "Contenido no reconocido enviado"


""" read https://ai.google.dev/api/rest/v1/GenerationConfig """
generation_config = {
    "max_output_tokens": 4096,
}

""" read https://ai.google.dev/api/rest/v1/HarmCategory """
safety_settings = [
    {
        "category": "HARM_CATEGORY_HARASSMENT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_HATE_SPEECH",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
        "threshold": "BLOCK_NONE"
    },
    {
        "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
        "threshold": "BLOCK_NONE"
    },
]
