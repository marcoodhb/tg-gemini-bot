import time
from io import BytesIO

from google import genai
from google.genai import types
import PIL.Image

from .config import (
    GOOGLE_API_KEY, generation_config, safety_settings,
    gemini_err_info, new_chat_info, SYSTEM_INSTRUCTION, DEFAULT_MODEL,
)

_key_index = 0
client = genai.Client(api_key=GOOGLE_API_KEY[_key_index])

current_model = DEFAULT_MODEL

# Transient error codes that are safe to retry
_RETRY_CODES = {429, 500, 503}
_MAX_RETRIES = 3
_RETRY_DELAYS = [2, 4, 8]  # exponential backoff in seconds


def _is_retryable(exc: Exception) -> bool:
    """Check if exception is a transient Gemini API error."""
    s = str(exc)
    for code in _RETRY_CODES:
        if str(code) in s:
            return True
    return False


def _is_quota_error(exc: Exception) -> bool:
    """Detect quota exhaustion specifically (vs transient rate-limit)."""
    s = str(exc).lower()
    return "429" in s and ("quota" in s or "resource_exhausted" in s)


def _rotate_key() -> bool:
    """Move to the next API key, if any left. Returns True if rotated."""
    global client, _key_index
    if _key_index < len(GOOGLE_API_KEY) - 1:
        _key_index += 1
        client = genai.Client(api_key=GOOGLE_API_KEY[_key_index])
        print(f"Quota exhausted, rotated to API key index {_key_index}")
        return True
    print("Quota exhausted on all keys")
    return False


def _call_with_retry(fn_factory, *args, **kwargs):
    """fn_factory: callable with no args that returns the bound client method to call.
    Re-called each attempt so it picks up the current `client` after a key rotation."""
    last_exc = None
    for attempt in range(_MAX_RETRIES):
        try:
            fn = fn_factory()
            return fn(*args, **kwargs)
        except Exception as e:
            last_exc = e
            if _is_quota_error(e):
                _rotate_key()
                continue
            if _is_retryable(e) and attempt < _MAX_RETRIES - 1:
                time.sleep(_RETRY_DELAYS[attempt])
                continue
            raise
    raise last_exc


def get_current_model():
    return current_model


def set_model(model_name: str):
    global current_model
    current_model = model_name


def _build_gen_config():
    """Build GenerateContentConfig from config settings."""
    return types.GenerateContentConfig(
        max_output_tokens=generation_config.get("max_output_tokens", 1024),
        safety_settings=[
            types.SafetySetting(category=s["category"], threshold=s["threshold"])
            for s in safety_settings
        ],
        system_instruction=SYSTEM_INSTRUCTION if SYSTEM_INSTRUCTION else None,
    )


def list_models():
    return client.models.list()


def generate_content(prompt: str) -> str:
    try:
        response = _call_with_retry(
            lambda: client.models.generate_content,
            model=current_model,
            contents=prompt,
            config=_build_gen_config(),
        )
        result = response.text
    except Exception as e:
        result = f"{gemini_err_info}\n{repr(e)}"
    return result


def generate_text_with_image(prompt: str, image_bytes: BytesIO) -> str:
    """generate text from prompt and image"""
    img = PIL.Image.open(image_bytes)
    try:
        response = _call_with_retry(
            lambda: client.models.generate_content,
            model=current_model,
            contents=[prompt, img],
            config=_build_gen_config(),
        )
        result = response.text
    except Exception as e:
        result = f"{gemini_err_info}\n{repr(e)}"
    return result


def generate_text_with_file(prompt: str, file_bytes: bytes, mime_type: str) -> str:
    """generate text from prompt and file (video, audio, etc.)"""
    try:
        media_part = types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
        response = _call_with_retry(
            lambda: client.models.generate_content,
            model=current_model,
            contents=[prompt, media_part],
            config=_build_gen_config(),
        )
        result = response.text
    except Exception as e:
        result = f"{gemini_err_info}\n{repr(e)}"
    return result


class ChatConversation:
    """
    Kicks off an ongoing chat. If the input is /new,
    it triggers the start of a fresh conversation.
    """

    def __init__(self) -> None:
        self.chat = client.chats.create(
            model=current_model,
            config=_build_gen_config(),
        )

    def reset(self) -> None:
        """Start a fresh conversation, dropping all history."""
        self.__init__()

    def send_message(self, prompt: str) -> str:
        """send message"""
        prompt = prompt.removeprefix("/gemini")
        prompt = prompt.removeprefix("/Gemini")
        prompt = prompt.removeprefix("/ai")
        prompt = prompt.removeprefix("/AI")
        try:
            response = _call_with_retry(lambda: self.chat.send_message, prompt)
            result = response.text
        except Exception as e:
            result = f"{gemini_err_info}\n{repr(e)}"
        return result

    @property
    def history(self):
        return self.chat.get_history()

    @property
    def history_length(self):
        return len(self.history)


if __name__ == "__main__":
    print(list_models())
