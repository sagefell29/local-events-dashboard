
import argostranslate.translate


def translate_text(text: str, source_lang: str = "nl", target_lang: str = "en") -> str:
    """Translate text locally, returning the original text if translation fails."""
    if not text or not text.strip():
        return text

    try:
        return argostranslate.translate.translate(
            text,
            source_lang,
            target_lang,
        )
    except Exception:
        # Keep the dashboard usable if translation fails.
        return text