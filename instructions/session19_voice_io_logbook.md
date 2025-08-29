# Session 19 — Voice I/O System Completion Logbook

**Date:** 2025‑08‑28  
**Author:** Basil & Copilot

---

## Objective
Implement full duplex voice input for all browsers, with backend flag control and clean rollback rungs.

---

## Rungs, Commits, Tags

| Rung | Description | Key Files | Commit Msg | Tag |
|------|-------------|-----------|------------|-----|
| 1 | Add `stt_enabled` config flag and `.env.example` template | `src/utils/config.py`, `.env.example` | `feat(config): add stt_enabled config + env.example template` | `backup-session19-rung1-stt-flag` |
| 2 | Backend `/speech` endpoint scaffold, guarded by `stt_enabled` | `src/api/main.py` | `feat(api): add /speech endpoint scaffold gated by stt_enabled` | `backup-session19-rung2-speech-scaffold` |
| 3 | On‑device STT mic component posting direct to `/message` | `frontend/src/components/MicCapture.tsx` | `feat(frontend): add on-device STT mic capture posting to /message` | `backup-session19-rung3-miccapture` |
| 4 | Server‑fallback mic capture posting audio to `/speech` | `frontend/src/components/MicCaptureServerFallback.tsx` | `feat(frontend): add server-fallback mic capture posting to /speech` | `backup-session19-rung4-miccapture-fallback` |
| 5 | `SmartMicCapture` wrapper selecting client vs server path | `frontend/src/components/SmartMicCapture.tsx` | `feat(frontend): unify on-device and server-fallback mic into SmartMicCapture` | `backup-session19-rung5-smartmic` |
| 5b | Conversation view refactor to use only `SmartMicCapture` | `frontend/src/components/ConversationView.tsx` | `refactor(frontend): replace direct mic components with SmartMicCapture` | `backup-session19-rung5b-convo-integration` |

---

## Rollback Ladder
Each rung is tagged and pushed to origin. To revert to a rung:
```bash
git checkout <tag>
