from core.orchestrator import register_action

@register_action("translation_init")
def translation_init(context):
    """Initialize translation system"""
    print("Stub: translation_init called")
    context['translation_state'] = {
        'source_language': None,
        'target_language': None,
        'translation_service': 'default',
        'confidence_threshold': 0.8
    }
    return {"status": "ok", "data": context['translation_state']}

@register_action("set_translation_languages")
def set_translation_languages(context, source_lang=None, target_lang=None):
    """Set source and target languages for translation"""
    print(f"Stub: set_translation_languages called with source='{source_lang}', target='{target_lang}'")
    
    if 'translation_state' not in context:
        translation_init(context)
    
    if source_lang:
        context['translation_state']['source_language'] = source_lang
    if target_lang:
        context['translation_state']['target_language'] = target_lang
    
    return {
        "status": "ok",
        "source": context['translation_state']['source_language'],
        "target": context['translation_state']['target_language']
    }

@register_action("translate_text")
def translate_text(context, text, source_lang=None, target_lang=None):
    """Translate text from source to target language"""
    print(f"Stub: translate_text called with text='{text}'")
    
    if 'translation_state' not in context:
        translation_init(context)
    
    # Use provided languages or fall back to context state
    src = source_lang or context['translation_state'].get('source_language')
    tgt = target_lang or context['translation_state'].get('target_language')
    
    if not src or not tgt:
        return {"status": "error", "message": "Source and target languages must be specified"}
    
    # Placeholder for actual translation logic
    translated_text = f"[TRANSLATED from {src} to {tgt}] {text}"
    
    return {
        "status": "ok",
        "original": text,
        "translated": translated_text,
        "source_language": src,
        "target_language": tgt,
        "confidence": 0.95
    }

@register_action("detect_language")
def detect_language(context, text):
    """Detect the language of input text"""
    print(f"Stub: detect_language called with text='{text}'")
    
    # Placeholder for actual language detection logic
    detected_lang = "en"  # Default to English for this example
    confidence = 0.9
    
    return {
        "status": "ok",
        "text": text,
        "detected_language": detected_lang,
        "confidence": confidence
    }

@register_action("get_supported_languages")
def get_supported_languages(context):
    """Get list of supported languages for translation"""
    print("Stub: get_supported_languages called")
    
    supported_languages = [
        {"code": "en", "name": "English"},
        {"code": "es", "name": "Spanish"},
        {"code": "fr", "name": "French"},
        {"code": "de", "name": "German"},
        {"code": "it", "name": "Italian"},
        {"code": "pt", "name": "Portuguese"},
        {"code": "zh", "name": "Chinese"},
        {"code": "ja", "name": "Japanese"},
        {"code": "ko", "name": "Korean"},
        {"code": "ar", "name": "Arabic"}
    ]
    
    return {
        "status": "ok",
        "supported_languages": supported_languages
    }

@register_action("translation_batch")
def translation_batch(context, texts, source_lang=None, target_lang=None):
    """Translate multiple texts in batch"""
    print(f"Stub: translation_batch called with {len(texts)} texts")
    
    if not isinstance(texts, list):
        return {"status": "error", "message": "texts must be a list"}
    
    results = []
    for text in texts:
        result = translate_text(context, text, source_lang, target_lang)
        results.append(result)
    
    return {
        "status": "ok",
        "results": results,
        "total_count": len(texts)
    }

@register_action("translation_cleanup")
def translation_cleanup(context):
    """Clean up translation resources and state"""
    print("Stub: translation_cleanup called")
    
    if 'translation_state' in context:
        del context['translation_state']
    
    return {"status": "ok"}