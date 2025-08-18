# Add these to replace the existing stubs at the bottom of core/actions_translation.py

def translate_text(step_id: str, params: dict, safe_mode: bool = True) -> dict:
    """
    Direct translation of text without session management.
    
    Expected params:
    - text: Text to translate
    - source_lang: Source language code (e.g., "en")
    - target_lang: Target language code (e.g., "es")
    - context: Optional context for better translation
    """
    try:
        if safe_mode:
            logger.info(f"[SAFE MODE] Would translate text for {step_id}")
            result = {
                "original_text": params.get("text", ""),
                "translated_text": f"[SAFE MODE] Translated: {params.get('text', '')[:50]}...",
                "source_lang": params.get("source_lang", "auto"),
                "target_lang": params.get("target_lang", "en"),
                "status": "translated_safe_mode",
                "confidence": 0.95
            }
        else:
            # TODO: Implement actual translation logic
            translated = _engine.translate_direct(
                text=params.get("text"),
                source_lang=params.get("source_lang", "auto"),
                target_lang=params.get("target_lang", "en"),
                context=params.get("context")
            )
            
            result = {
                "original_text": params.get("text"),
                "translated_text": translated["text"],
                "source_lang": translated["detected_lang"],
                "target_lang": params.get("target_lang"),
                "status": "translated",
                "confidence": translated.get("confidence", 0.0)
            }
        
        logger.info(f"Text translation completed for {step_id}")
        return _log_step(step_id, result)
        
    except Exception as e:
        logger.error(f"Text translation failed for {step_id}: {e}")
        error_result = {
            "status": "error",
            "error": str(e),
            "error_type": "translate_text_failed",
            "original_text": params.get("text", "")
        }
        return _log_step(step_id, error_result)


def init_dual_party_session(step_id: str, params: dict, safe_mode: bool = True) -> dict:
    """
    Initialize a two-party translation session with both participants.
    
    Expected params:
    - user1_id: First participant ID
    - user2_id: Second participant ID
    - lang_user1: Language for user 1
    - lang_user2: Language for user 2
    - session_name: Optional session name
    - privacy_mode: Whether to enable private mode
    """
    try:
        if safe_mode:
            logger.info(f"[SAFE MODE] Would initialize dual party session for {step_id}")
            result = {
                "session_id": f"dual_mock_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "user1_id": params.get("user1_id"),
                "user2_id": params.get("user2_id"),
                "lang_pair": f"{params.get('lang_user1', 'en')} ↔ {params.get('lang_user2', 'es')}",
                "session_name": params.get("session_name", "Dual Translation Session"),
                "privacy_mode": params.get("privacy_mode", False),
                "status": "dual_initialized_safe_mode",
                "participants_connected": 2
            }
        else:
            # TODO: Implement actual dual party session logic
            session_id = _engine.create_dual_session(
                user1_id=params.get("user1_id"),
                user2_id=params.get("user2_id"),
                lang_user1=params.get("lang_user1", "en"),
                lang_user2=params.get("lang_user2", "es"),
                session_name=params.get("session_name"),
                privacy_mode=params.get("privacy_mode", False)
            )
            
            result = {
                "session_id": session_id,
                "user1_id": params.get("user1_id"),
                "user2_id": params.get("user2_id"),
                "lang_pair": f"{params.get('lang_user1')} ↔ {params.get('lang_user2')}",
                "session_name": params.get("session_name"),
                "privacy_mode": params.get("privacy_mode", False),
                "status": "dual_initialized",
                "participants_connected": 2
            }
        
        logger.info(f"Dual party session initialized: {result['session_id']}")
        return _log_step(step_id, result)
        
    except Exception as e:
        logger.error(f"Dual party session init failed for {step_id}: {e}")
        error_result = {
            "status": "error",
            "error": str(e),
            "error_type": "dual_session_init_failed"
        }
        return _log_step(step_id, error_result)


def recalibrate_translation(step_id: str, params: dict, safe_mode: bool = True) -> dict:
    """
    Recalibrate translation quality based on user feedback.
    
    Expected params:
    - session_id: Active translation session ID
    - feedback_type: Type of feedback ("quality", "accuracy", "style")
    - rating: Numeric rating (1-5 or 1-10)
    - corrections: List of correction examples
    - preferences: User preference adjustments
    """
    try:
        if safe_mode:
            logger.info(f"[SAFE MODE] Would recalibrate translation for {step_id}")
            result = {
                "session_id": params.get("session_id"),
                "feedback_type": params.get("feedback_type", "quality"),
                "rating": params.get("rating", 5),
                "corrections_applied": len(params.get("corrections", [])),
                "calibration_score": 0.85,
                "status": "recalibrated_safe_mode",
                "improvements": [
                    "Adjusted formality level",
                    "Updated terminology preferences",
                    "Enhanced context awareness"
                ]
            }
        else:
            # TODO: Implement actual recalibration logic
            calibration = _engine.recalibrate_session(
                session_id=params.get("session_id"),
                feedback_type=params.get("feedback_type", "quality"),
                rating=params.get("rating"),
                corrections=params.get("corrections", []),
                preferences=params.get("preferences", {})
            )
            
            result = {
                "session_id": params.get("session_id"),
                "feedback_type": params.get("feedback_type"),
                "rating": params.get("rating"),
                "corrections_applied": len(params.get("corrections", [])),
                "calibration_score": calibration.get("score", 0.0),
                "status": "recalibrated",
                "improvements": calibration.get("improvements", [])
            }
        
        logger.info(f"Translation recalibrated for session: {params.get('session_id')}")
        return _log_step(step_id, result)
        
    except Exception as e:
        logger.error(f"Translation recalibration failed for {step_id}: {e}")
        error_result = {
            "status": "error",
            "error": str(e),
            "error_type": "recalibration_failed",
            "session_id": params.get("session_id")
        }
        return _log_step(step_id, error_result)


# Update the TRANSLATION_ACTIONS registry to include the new functions
TRANSLATION_ACTIONS.update({
    "translate_text": translate_text,
    "init_dual_party_session": init_dual_party_session,
    "recalibrate_translation": recalibrate_translation
})