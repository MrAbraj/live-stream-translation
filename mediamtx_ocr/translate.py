import os
import html
from google.cloud import translate_v2 as translate
from functools import lru_cache
os.environ.setdefault("GOOGLE_APPLICATION_CREDENTIALS", "assets/service-account.json")

translation_cache = {}
@lru_cache(maxsize=1024)
def translate_text(text: str, target_language: str = "hi") -> str:
    client = translate.Client()
    try:
        response = client.translate(
            text,
            target_language=target_language,
            format_="text",
            source_language="en",
            model="nmt"
        )
        return html.unescape(response.get("translatedText", "").strip())
    except Exception as e:
        print(f"Translation failed: {e}")
        return ""

def get_translated_dict(result_dict: dict, target_language: str = "hi") -> dict:
    translated = {}
    for i, text in result_dict.items():
        if not text:
            translated[i] = ""
            continue
        normalized_text = text.strip().lower()
        translated[i] = translate_text(normalized_text, target_language)
    return translated