from core.llm import GeminiProvider  # or adjust to match your provider import

# Instantiate your default LLM provider (Gemini Pro)
provider = GeminiProvider()

def translate_text(text: str, src_lang: str = None, tgt_lang: str = "english") -> str:
    """
    Translate text from src_lang to tgt_lang using the configured LLM provider.
    If src_lang is None, provider should auto-detect.
    """
    # Build a simple, explicit prompt
    lang_clause = f" from {src_lang}" if src_lang else ""
    prompt = f"Translate the following text{lang_clause} to {tgt_lang}:\n\n{text}"

    # Call your provider and return cleaned output
    response = provider.generate(
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3  # low temp for deterministic output
    )
    return response.strip()
