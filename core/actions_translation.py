# Add this import at the top of core/actions_translation.py
from orchestrator_core import register_action  # adjust import to your orchestrator

# Replace the existing function definitions with these registered versions

@register_action("translation_init")
def translation_init(context):
    """
    Prepare translation environment and initialize session.
    
    Context should contain:
    - initiator: User ID who starts the session
    - partner_type: "person" or "user" 
    - lang_user1: Source language code (e.g., "en")
    - lang_user2: Target language code (e.g., "es")
    - dialog_pairs: Number of expected dialog pairs
    - start_signal: Signal to begin translation (e.g., "@^2")
    - pin: Optional PIN for session security
    """
    try:
        params = context.get("params", {})
        safe_mode = context.get("safe_mode", True)
        step_id = context.get("step_id", "translation_init")
        
        if safe_mode:
            logger.info(f"[SAFE MODE] Would initialize translation session for {step_id}")
            result = {
                "status": "init_stub",
                "details": "Translation init placeholder - safe mode",
                "session_id": f"mock_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "initiator": params.get("initiator"),
                "lang_pair": f"{params.get('lang_user1', 'en')} → {params.get('lang_user2', 'es')}",
                "dialog_pairs": params.get("dialog_pairs", 2),
                "start_signal": params.get("start_signal", "@^2")
            }
        else:
            session_id = _engine.create_session(
                initiator=params.get("initiator"),
                partner_type=params.get("partner_type", "person"),
                lang_user1=params.get("lang_user1", "en"),
                lang_user2=params.get("lang_user2", "es"),
                dialog_pairs=params.get("dialog_pairs", 2),
                start_signal=params.get("start_signal", "@^2"),
                pin=params.get("pin")
            )
            
            result = {
                "status": "initialized",
                "details": "Translation session successfully initialized",
                "session_id": session_id,
                "initiator": params.get("initiator"),
                "lang_pair": f"{params.get('lang_user1')} → {params.get('lang_user2')}",
                "dialog_pairs": params.get("dialog_pairs"),
                "start_signal": params.get("start_signal")
            }
        
        logger.info(f"Translation session initialized: {result.get('session_id')}")
        return _log_step(step_id, result)
        
    except Exception as e:
        logger.error(f"Translation init failed: {e}")
        return {
            "status": "error",
            "details": f"Translation init failed: {str(e)}",
            "error_type": "translation_init_failed"
        }


@register_action("translation_process")
def translation_process(context):
    """
    Process translation request and handle text segments.
    
    Context should contain:
    - session_id: Active translation session ID
    - text: Text to process/translate
    - segment_id: Optional segment identifier
    - processing_type: Type of processing ("translate", "review", "refine")
    """
    try:
        params = context.get("params", {})
        safe_mode = context.get("safe_mode", True)
        step_id = context.get("step_id", "translation_process")
        
        if safe_mode:
            logger.info(f"[SAFE MODE] Would process translation for {step_id}")
            result = {
                "status": "process_stub",
                "details": "Translation process placeholder - safe mode",
                "session_id": params.get("session_id"),
                "text": params.get("text", ""),
                "segment_id": params.get("segment_id"),
                "processing_type": params.get("processing_type", "translate"),
                "processed_text": f"[SAFE MODE] Processed: {params.get('text', '')[:50]}...",
                "timestamp": datetime.now().isoformat()
            }
        else:
            processed = _engine.process_translation(
                session_id=params.get("session_id"),
                text=params.get("text"),
                segment_id=params.get("segment_id"),
                processing_type=params.get("processing_type", "translate")
            )
            
            result = {
                "status": "processed",
                "details": "Translation processing completed successfully",
                "session_id": params.get("session_id"),
                "text": params.get("text"),
                "segment_id": params.get("segment_id"),
                "processing_type": params.get("processing_type"),
                "processed_text": processed["text"],
                "timestamp": datetime.now().isoformat(),
                "quality_score": processed.get("quality_score", 0.0)
            }
        
        logger.info(f"Translation processing completed for {step_id}")
        return _log_step(step_id, result)
        
    except Exception as e:
        logger.error(f"Translation processing failed: {e}")
        return {
            "status": "error",
            "details": f"Translation process failed: {str(e)}",
            "error_type": "translation_process_failed"
        }


@register_action("translation_finalize")
def translation_finalize(context):
    """
    Finalize translation and return formatted output.
    
    Context should contain:
    - session_id: Active translation session ID
    - output_format: Desired output format ("text", "json", "xml", "csv")
    - include_metadata: Whether to include translation metadata
    - quality_check: Whether to perform final quality check
    """
    try:
        params = context.get("params", {})
        safe_mode = context.get("safe_mode", True)
        step_id = context.get("step_id", "translation_finalize")
        
        if safe_mode:
            logger.info(f"[SAFE MODE] Would finalize translation for {step_id}")
            result = {
                "status": "finalize_stub",
                "details": "Translation finalize placeholder - safe mode",
                "session_id": params.get("session_id"),
                "output_format": params.get("output_format", "text"),
                "include_metadata": params.get("include_metadata", True),
                "quality_check": params.get("quality_check", True),
                "final_output": "[SAFE MODE] Finalized translation output would appear here",
                "word_count": 150,
                "final_quality_score": 0.92,
                "timestamp": datetime.now().isoformat()
            }
        else:
            finalized = _engine.finalize_translation(
                session_id=params.get("session_id"),
                output_format=params.get("output_format", "text"),
                include_metadata=params.get("include_metadata", True),
                quality_check=params.get("quality_check", True)
            )
            
            result = {
                "status": "finalized",
                "details": "Translation finalization completed successfully",
                "session_id": params.get("session_id"),
                "output_format": params.get("output_format"),
                "include_metadata": params.get("include_metadata"),
                "quality_check": params.get("quality_check"),
                "final_output": finalized["output"],
                "word_count": finalized.get("word_count", 0),
                "final_quality_score": finalized.get("quality_score", 0.0),
                "timestamp": datetime.now().isoformat(),
                "metadata": finalized.get("metadata", {}) if params.get("include_metadata") else None
            }
        
        logger.info(f"Translation finalized for {step_id}")
        return _log_step(step_id, result)
        
    except Exception as e:
        logger.error(f"Translation finalization failed: {e}")
        return {
            "status": "error",
            "details": f"Translation finalize failed: {str(e)}",
            "error_type": "translation_finalize_failed"
        }


# Register additional existing actions for completeness
@register_action("translation_propose")
def translation_propose_registered(context):
    """Wrapper for existing translation_propose function."""
    params = context.get("params", {})
    safe_mode = context.get("safe_mode", True)
    step_id = context.get("step_id", "translation_propose")
    return translation_propose(step_id, params, safe_mode)


@register_action("translation_interject")
def translation_interject_registered(context):
    """Wrapper for existing translation_interject function."""
    params = context.get("params", {})
    safe_mode = context.get("safe_mode", True)
    step_id = context.get("step_id", "translation_interject")
    return translation_interject(step_id, params, safe_mode)


@register_action("translation_end")
def translation_end_registered(context):
    """Wrapper for existing translation_end function."""
    params = context.get("params", {})
    safe_mode = context.get("safe_mode", True)
    step_id = context.get("step_id", "translation_end")
    return translation_end(step_id, params, safe_mode)


# Note: You can remove the TRANSLATION_ACTIONS dictionary if using decorator registration
# The orchestrator will handle action dispatch through the @register_action decorators
