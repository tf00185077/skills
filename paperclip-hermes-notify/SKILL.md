---
name: paperclip-hermes-notify
description: Use when a Producer needs to deliver a Paperclip question card to the existing Hermes conversation associated with a Discord channel.
---

# Paperclip question delivery

## Rules — read before running

Run the block below **exactly as written**. Only change the five input assignments: `SKILL_DIR`, `HERMES_HOME`, `HERMES_PYTHON`, `CHANNEL_ID`, and `QUESTION_CARD`. `SESSION_BINDING` and `SESSION_ID` must come from the commands, never from memory or manual substitution. If it fails, return the exact error to Producer. Do not retry with changed or added arguments.

`SKILL_DIR` is the absolute directory containing this file and its bundled `scripts/` folder. Use the target Hermes profile home and the Python interpreter from the same Hermes installation as `hermes`; the paths below are the default local installation. `QUESTION_CARD` contains the full question and native card link.

This resumes saved history in a CLI process, not the live Discord Gateway worker. **Before delivery, the session owner must have confirmed exclusive handoff.** The query helper checks routing and saved-history metadata, not Gateway ownership, and provides no lock. Without that handoff, report `exclusive_session_handoff_unverified` and do not run the delivery block. Do not invent an ownership check or bypass it with an environment flag.

## Start

The bundled helper calls the installed native MCP conversation handlers in-process. Producer needs no preconfigured MCP connection. It starts no event poller, reads no conversation contents, and never starts an agent or sends a message. It rejects missing, ambiguous, threaded, truncated, changed, archived or empty-history targets.

Run this as **one Bash block**, changing only the five input values:

```bash
SKILL_DIR='/absolute/path/to/paperclip-hermes-notify'
export HERMES_HOME="${HOME}/.hermes"
HERMES_PYTHON="${HOME}/.hermes/hermes-agent/venv/bin/python"
CHANNEL_ID='<destination Discord channel ID>'
QUESTION_CARD='<full question text and native card link>'

SESSION_BINDING="$("${HERMES_PYTHON}" -B "${SKILL_DIR}/scripts/channel_session.py" \
  resolve --channel-id "${CHANNEL_ID}")" || exit "$?"

SESSION_ID="$("${HERMES_PYTHON}" -B "${SKILL_DIR}/scripts/channel_session.py" \
  check --channel-id "${CHANNEL_ID}" --binding "${SESSION_BINDING}")" || exit "$?"

hermes chat --quiet --resume "${SESSION_ID}" --source tool --toolsets file,messaging \
  -q "Process this Producer question card using the existing conversation context: ${QUESTION_CARD}. Use send_message action=list, then action=send to discord:${CHANNEL_ID} to report your answer or explicit blocker with the native card link. Return that response and the actual success, platform, chat_id and message_id, or the actual error."
```

`resolve` prints a current binding as JSON. `check` queries again, requires the same profile/channel/session key/session ID, verifies saved user messages through SQLite `mode=ro`, and prints only the session ID to stdout. Both print metadata to stderr, including `exclusive_use: "not_checked"`; that is not an ownership guarantee. Neither command constructs or migrates the session database.

## Verify

- The CLI stderr must confirm restored messages and include its final `session_id:` line. Missing resume confirmation, a fresh-start fallback or an unexplained identity change is not verified intake; record an explicitly reported compression descendant.
- Require an actual answer or explicit blocker for the question. Channel reporting additionally requires the actual messaging receipt: success, Discord, the requested `chat_id`, and a real `message_id`.
- Return the binding, requested/actual session IDs, response and actual receipt or error to Producer. Process creation, exit zero, posting alone or transcript mirroring proves neither intake nor a completed handoff. Do not alter arguments and retry.

To test the bundled helper without a live agent or real session data:

```bash
SKILL_DIR='/absolute/path/to/paperclip-hermes-notify'
python3 -B -m unittest discover -s "${SKILL_DIR}/tests" -v
```
