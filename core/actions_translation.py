"""
core/actions_translation.py
Handlers for translation_* actions, delegating to TranslationEngine.
"""

from pathlib import Path
from datetime import datetime
from typing import Dict, Any
import json
import logging

from core.translation_engine import TranslationEngine

# Create a singleton-ish engine instance for this session
_engine = TranslationEngine()

logger = logging.getLogger(__name__)

def _log_step(step_id: str, payload: dict) -> dict:
    """
    Save step results to a per-step log file and return the payload.
    """
    logs_dir = Path("orchestrator_artifacts")
    logs_dir.mkdir(exist_ok=True)
    log_file = logs_dir / f"{datetime.now():%Y%m%d_%H%M%S}_{step_id}.log"
    
    try:
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(f"Step ID: {step_id}\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n")
            f.write(f"Payload: {json.dumps(payload, indent=2)}\n")
        
        # Add log file path to payload for orchestrator tracking
        payload["_log_file"] = str(log_file)
        
    except Exception as e:
        logger.error(f"Failed to write log for step {step_id}: {e}")
        payload["_log_error"] = str(e)
    
    return payload

def translation_init(step_id: str, params: dict, safe_mode: bool = True) -> dict:
    """
    Initialize a new translation session.
    
    Expected params:
    - initiator: User ID who starts the session
    - partner_type: "person" or "user" 
    - lang_user1: Source language code (e.g., "en")
    - lang_user2: Target language code (e.g., "es")
    - dialog_pairs: Number of expected dialog pairs
    - start_signal: Signal to begin translation (e.g., "@^2")
    - pin: Optional PIN for session security
    """
    try:
        if safe_mode:
            logger.info(f"[SAFE MODE] Would initialize translation session for {step_id}")
            result = {
                "session_id": f"mock_session_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                "status": "initialized_safe_mode",
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
                "session_id": session_id,
                "status": "initialized",
                "initiator": params.get("initiator"),
                "lang_pair": f"{params.get('lang_user1')} → {params.get('lang_user2')}",
                "dialog_pairs": params.get("dialog_pairs"),
                "start_signal": params.get("start_signal")
            }
        
        logger.info(f"Translation session initialized: {result['session_id']}")
        return _log_step(step_id, result)
        
    except Exception as e:
        logger.error(f"Translation init failed for {step_id}: {e}")
        error_result = {
            "status": "error",
            "error": str(e),
            "error_type": "translation_init_failed"
        }
        return _log_step(step_id, error_result)

def translation_propose(step_id: str, params: dict, safe_mode: bool = True) -> dict:
    """
    Propose a set of translation options for given text.
    
    Expected params:
    - session_id: Active translation session ID
    - text: Text to translate
    - n: Number of translation options to generate (default: 5)
    - context: Optional context for better translations
    """
    try:
        if safe_mode:
            logger.info(f"[SAFE MODE] Would generate translation proposals for {step_id}")
            result = {
                "session_id": params.get("session_id"),
                "text": params.get("text", ""),
                "options": [
                    f"[SAFE MODE] Translation option 1 for: {params.get('text', '')[:50]}...",
                    f"[SAFE MODE] Translation option 2 for: {params.get('text', '')[:50]}...",
                    f"[SAFE MODE] Translation option 3 for: {params.get('text', '')[:50]}..."
                ],
                "status": "proposed_safe_mode",
                "n_requested": params.get("n", 5)
            }
        else:
            options = _engine.propose_translations(
                session_id=params.get("session_id"),
                text=params.get("text"),
                n=params.get("n", 5),
                context=params.get("context")
            )
            
            result = {
                "session_id": params.get("session_id"),
                "text": params.get("text"),
                "options": options,
                "status": "proposed",
                "n_generated": len(options)
            }
        
        logger.info(f"Generated {len(result['options'])} translation proposals")
        return _log_step(step_id, result)
        
    except Exception as e:
        logger.error(f"Translation propose failed for {step_id}: {e}")
        error_result = {
            "status": "error",
            "error": str(e),
            "error_type": "translation_propose_failed",
            "session_id": params.get("session_id")
        }
        return _log_step(step_id, error_result)

def translation_interject(step_id: str, params: dict, safe_mode: bool = True) -> dict:
    """
    Record an interjection/amendment to an in-progress translation.
    
    Expected params:
    - session_id: Active translation session ID
    - note: Interjection note or correction
    - type: Type of interjection ("correction", "clarification", "context")
    - target_segment: Optional segment ID being corrected
    """
    try:
        if safe_mode:
            logger.info(f"[SAFE MODE] Would record interjection for {step_id}")
            result = {
                "session_id": params.get("session_id"),
                "note": params.get("note"),
                "type": params.get("type", "correction"),
                "status": "interjected_safe_mode",
                "timestamp": datetime.now().isoformat()
            }
        else:
            _engine.record_interjection(
                session_id=params.get("session_id"),
                note=params.get("note"),
                interjection_type=params.get("type", "correction"),
                target_segment=params.get("target_segment")
            )
            
            result = {
                "session_id": params.get("session_id"),
                "note": params.get("note"),
                "type": params.get("type", "correction"),
                "status": "interjected",
                "timestamp": datetime.now().isoformat()
            }
        
        logger.info(f"Recorded translation interjection: {params.get('type', 'correction')}")
        return _log_step(step_id, result)
        
    except Exception as e:
        logger.error(f"Translation interject failed for {step_id}: {e}")
        error_result = {
            "status": "error",
            "error": str(e),
            "error_type": "translation_interject_failed",
            "session_id": params.get("session_id")
        }
        return _log_step(step_id, error_result)

def translation_end(step_id: str, params: dict, safe_mode: bool = True) -> dict:
    """
    Close the translation session and return its complete record.
    
    Expected params:
    - session_id: Active translation session ID
    - save_record: Whether to save session record to file (default: True)
    - output_format: Format for saved record ("json", "txt", "csv")
    """
    try:
        if safe_mode:
            logger.info(f"[SAFE MODE] Would close translation session for {step_id}")
            result = {
                "session_id": params.get("session_id"),
                "status": "closed_safe_mode",
                "record": {
                    "session_duration": "00:15:30",
                    "total_translations": 12,
                    "interjections": 3,
                    "final_quality_score": 0.87
                },
                "saved_to": f"[SAFE MODE] Would save to: translation_record_{params.get('session_id')}.json"
            }
        else:
            record = _engine.close_session(
                session_id=params.get("session_id"),
                save_record=params.get("save_record", True),
                output_format=params.get("output_format", "json")
            )
            
            result = {
                "session_id": params.get("session_id"),
                "status": "closed",
                "record": record,
                "session_duration": record.get("duration", "unknown"),
                "total_translations": record.get("translation_count", 0),
                "interjections": record.get("interjection_count", 0)
            }
            
            if params.get("save_record", True):
                result["saved_to"] = record.get("saved_file")
        
        logger.info(f"Translation session closed: {params.get('session_id')}")
        return _log_step(step_id, result)
        
    except Exception as e:
        logger.error(f"Translation end failed for {step_id}: {e}")
        error_result = {
            "status": "error", 
            "error": str(e),
            "error_type": "translation_end_failed",
            "session_id": params.get("session_id")
        }
        return _log_step(step_id, error_result)

# Action registry mapping for orchestrator dispatch
TRANSLATION_ACTIONS = {
    "translation_init": translation_init,
    "translation_propose": translation_propose,
    "translation_interject": translation_interject,
    "translation_end": translation_end
}

def get_translation_action(action_name: str):
    """Get translation action handler by name."""
    return TRANSLATION_ACTIONS.get(action_name)

def is_translation_action(action_name: str) -> bool:
    """Check if action name is a translation action."""
    return action_name in TRANSLATION_ACTIONS