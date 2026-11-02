---
name: paperclip-hermes-notify
description: Use when a Producer needs the existing Hermes conversation for a Discord channel to answer a Paperclip question card and post the answer or blocker to that channel.
---

# Paperclip question delivery

## Rules — read before running

Run the block below **exactly as written**. Only change the five input assignments: `SKILL_DIR`, `HERMES_HOME`, `HERMES_PYTHON`, `CHANNEL_ID`, and `QUESTION_CARD`. `SESSION_BINDING` and `SESSION_ID` must come from the commands, never from memory or manual substitution. If it fails, return the exact error to Producer. Do not retry with changed or added arguments.

`SKILL_DIR` is the absolute directory containing this file and its bundled `scripts/` folder. Keep the default `HERMES_HOME` and `HERMES_PYTHON` values unless Producer provides other paths; do not search for them yourself. Put the full question text and native card link between the two `CARD` lines as-is; do not quote or escape it.

This resumes saved history in a CLI process, not the live Discord Gateway worker. The query helper checks routing and saved-history metadata, not Gateway ownership, and provides no lock. Run the delivery block only when Producer's request explicitly includes `handoff_confirmed`. Otherwise, report `exclusive_session_handoff_unverified` to Producer and stop. Do not invent an ownership check or bypass it with an environment flag.

## Start

Run this as **one Bash block**, changing only the five input values:

```bash
(
SKILL_DIR='/absolute/path/to/paperclip-hermes-notify'
export HERMES_HOME="${HOME}/.hermes"
HERMES_PYTHON="${HOME}/.hermes/hermes-agent/venv/bin/python"
CHANNEL_ID='<destination Discord channel ID>'
QUESTION_CARD="$(cat <<'CARD'
<full question text and native card link>
CARD
)"

SESSION_BINDING="$("${HERMES_PYTHON}" -B "${SKILL_DIR}/scripts/channel_session.py" \
  resolve --channel-id "${CHANNEL_ID}")" || exit "$?"

SESSION_ID="$("${HERMES_PYTHON}" -B "${SKILL_DIR}/scripts/channel_session.py" \
  check --channel-id "${CHANNEL_ID}" --binding "${SESSION_BINDING}")" || exit "$?"

hermes chat --quiet --resume "${SESSION_ID}" --source tool --toolsets file,messaging \
  -q "Process this Producer question card using the existing conversation context: ${QUESTION_CARD}. Use send_message action=list, then action=send to discord:${CHANNEL_ID} to report your answer or explicit blocker with the native card link. End that Discord message with this exact line: Source: Paperclip Producer via paperclip-hermes-notify. Return that response and the actual success, platform, chat_id and message_id, or the actual error."
)
```

## Verify

- Require an actual answer or explicit blocker for the question. Channel reporting additionally requires the actual messaging receipt: success, Discord, the requested `chat_id`, and a real `message_id`.
- Return the response and actual receipt or error to Producer. Process creation, exit zero, posting alone or transcript mirroring proves neither intake nor a completed handoff.
