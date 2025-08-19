# core/translation_engine.py
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path
import json, time, uuid

SESSIONS_PATH = Path("sandbox-image") / "translation_sessions.json"

def _load_sessions():
    if SESSIONS_PATH.exists():
        try:
            return json.loads(SESSIONS_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}

def _save_sessions(data):
    SESSIONS_PATH.parent.mkdir(parents=True, exist_ok=True)
    SESSIONS_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

def translate_stub(text: str, target_lang: str) -> str:
    # Stub translator; later swap with Gemini Pro
    return f"{text} [{target_lang}]"

def options_templates(source_text: str):
    # Lightweight heuristics; swap with Gemini Pro ranked candidates later
    base = source_text.strip().rstrip(".!?")
    user2 = [
        f"Yes, I understand: {base}",
        f"No, not exactly about: {base}",
        "Can you clarify that?",
        "Please repeat slowly.",
        "Thank you, that helps."
    ]
    user1 = [
        "Great—here’s what I can do next.",
        "No problem, let me rephrase.",
        "I’ll need a bit more detail.",
        "Would you like me to proceed?",
        "I can summarize or provide steps."
    ]
    return user2, user1

@dataclass
class Turn:
    speaker: str  # "user1" or "user2"
    src_text: str
    translated_text: str
    user2_options: list[str] = field(default_factory=list)
    user1_options: list[str] = field(default_factory=list)
    selected_option: str | None = None
    ts: float = field(default_factory=time.time)

@dataclass
class TranslationSession:
    session_id: str
    initiator: str
    partner_type: str  # "person" | "user"
    lang_user1: str
    lang_user2: str
    max_pairs: int
    turn_index: int = 0
    status: str = "active"  # active | ended
    pin: str | None = None
    turns: list[Turn] = field(default_factory=list)

class TranslationEngine:
    def __init__(self):
        self._db = _load_sessions()

    def create(self, initiator: str, partner_type: str, lang1: str, lang2: str,
               max_pairs: int, pin: str | None = None) -> TranslationSession:
        session_id = str(uuid.uuid4())
        sess = TranslationSession(
            session_id=session_id,
            initiator=initiator,
            partner_type=partner_type,
            lang_user1=lang1,
            lang_user2=lang2,
            max_pairs=max_pairs,
            pin=pin
        )
        self._db[session_id] = self._to_json(sess)
        _save_sessions(self._db)
        return sess

    def get(self, session_id: str) -> TranslationSession | None:
        raw = self._db.get(session_id)
        if not raw:
            self._db = _load_sessions()
            raw = self._db.get(session_id)
            if not raw:
                return None
        return self._from_json(raw)

    def propose(self, session_id: str, user1_text: str) -> dict:
        sess = self.get(session_id)
        if not sess or sess.status != "active":
            raise ValueError("Invalid or ended session")
        if sess.turn_index >= sess.max_pairs:
            return {"ended": True, "message": "Max dialog pairs reached."}

        # User1 speaks → translate to user2
        t_user2 = translate_stub(user1_text, sess.lang_user2)
        u2_opts, u1_opts = options_templates(user1_text)
        # guarantee 5+5
        u2_opts = (u2_opts + ["OK.", "Understood.", "I disagree."])[:5]
        u1_opts = (u1_opts + ["Let’s continue.", "I’ll stop here."])[:5]

        turn = Turn(
            speaker="user1",
            src_text=user1_text,
            translated_text=t_user2,
            user2_options=u2_opts,
            user1_options=u1_opts
        )
        sess.turns.append(turn)
        self._db[session_id] = self._to_json(sess)
        _save_sessions(self._db)

        return {
            "session_id": session_id,
            "turn_index": sess.turn_index,
            "translated_for_user2": t_user2,
            "user2_expected": u2_opts,
            "user1_next": u1_opts,
            "remaining_pairs": sess.max_pairs - sess.turn_index
        }

    def record_user2(self, session_id: str, user2_text: str) -> dict:
        sess = self.get(session_id)
        if not sess or sess.status != "active":
            raise ValueError("Invalid or ended session")
        if not sess.turns:
            raise ValueError("No prior user1 turn to respond to.")
        last = sess.turns[-1]
        # check match with predefined; if no match, caller should use interject
        matched = user2_text in last.user2_options
        t_user1 = translate_stub(user2_text, sess.lang_user1)
        turn = Turn(
            speaker="user2",
            src_text=user2_text,
            translated_text=t_user1
        )
        sess.turns.append(turn)
        # completing one dialog pair
        sess.turn_index += 1
        self._db[session_id] = self._to_json(sess)
        _save_sessions(self._db)
        return {"matched": matched, "translated_for_user1": t_user1, "turn_index": sess.turn_index}

    def interject(self, session_id: str, clarified_text: str) -> dict:
        sess = self.get(session_id)
        if not sess or sess.status != "active":
            raise ValueError("Invalid or ended session")
        # Recalibrate with 2 new options each
        u2_opts = [f"(clarified) {clarified_text}", "Could you provide more detail?"][:2]
        u1_opts = ["Thanks—here’s a clearer version.", "Let me adjust my request."][:2]
        # Attach to last user1 turn as supplements
        for i in range(len(sess.turns) - 1, -1, -1):
            if sess.turns[i].speaker == "user1":
                sess.turns[i].user2_options = (sess.turns[i].user2_options + u2_opts)[-5:]
                sess.turns[i].user1_options = (sess.turns[i].user1_options + u1_opts)[-5:]
                break
        self._db[session_id] = self._to_json(sess)
        _save_sessions(self._db)
        return {"user2_expected_additional": u2_opts, "user1_next_additional": u1_opts}

    def end(self, session_id: str) -> dict:
        sess = self.get(session_id)
        if not sess:
            raise ValueError("Unknown session")
        sess.status = "ended"
        self._db[session_id] = self._to_json(sess)
        _save_sessions(self._db)
        return {"status": sess.status, "turns": len(sess.turns)}

    # ---- (de)serialization helpers ----
    def _to_json(self, sess: TranslationSession) -> dict:
        return {
            "session_id": sess.session_id,
            "initiator": sess.initiator,
            "partner_type": sess.partner_type,
            "lang_user1": sess.lang_user1,
            "lang_user2": sess.lang_user2,
            "max_pairs": sess.max_pairs,
            "turn_index": sess.turn_index,
            "status": sess.status,
            "pin": sess.pin,
            "turns": [t.__dict__ for t in sess.turns]
        }

    def _from_json(self, raw: dict) -> TranslationSession:
        sess = TranslationSession(
            session_id=raw["session_id"],
            initiator=raw["initiator"],
            partner_type=raw["partner_type"],
            lang_user1=raw["lang_user1"],
            lang_user2=raw["lang_user2"],
            max_pairs=raw["max_pairs"],
            turn_index=raw.get("turn_index", 0),
            status=raw.get("status", "active"),
            pin=raw.get("pin"),
            turns=[]
        )
        for tr in raw.get("turns", []):
            sess.turns.append(Turn(**tr))
        return sess
