---
name: paperclip-hermes-notify
description: Use when a Producer needs to deliver a Paperclip question card to the existing Hermes conversation associated with a Discord channel.
---

# Paperclip question delivery

## Rules — read before running

Run the command below **exactly as written**. The only things you may change are `CHANNEL_ID`, `QUESTION_CARD`, and `SESSION_ID` obtained from the lookup below. Everything else is fixed. Never substitute a fresh session or a remembered session ID.

This procedure resumes saved conversation history in a CLI process; it does not inject a turn into the live Discord Gateway worker. Requires the same Hermes profile/home for lookup and resume, the Hermes MCP conversation tools available to Producer, and host-confirmed exclusive use of the target session with saved messages. If those prerequisites cannot be verified, return the actual blocker without launching. Route metadata or an unended session row alone does not establish exclusive use.

## Start

1. Set `CHANNEL_ID` to the destination Discord channel and `QUESTION_CARD` to the full question text and native card link.
2. Call the native Hermes MCP tool `conversations_list` with `{"platform":"discord","search":"<CHANNEL_ID>","limit":200}`. This is an MCP tool call, not a shell command. The server entrypoint is `hermes mcp serve`; its connection must already be available to Producer.
3. Call `conversation_get` with `{"session_key":"<returned session_key>"}` for candidates. Match the exact Discord `chat_id` and intended user-specific route. The fixed channel command requires a null `thread_id`. Stop on a missing, truncated, threaded or unresolved ambiguous result; do not pick the newest entry or fall back to a parent channel.
4. Immediately before launch, call `conversation_get` again for the selected key. If its `session_id` differs from the selected ID, return `session_route_changed` without launching or silently retargeting. Otherwise set `SESSION_ID` to that nonempty ID and reconfirm exclusive use of this same session.
5. With the prerequisites verified, run:

```bash
hermes chat --quiet --resume "${SESSION_ID}" --source tool --toolsets file,messaging \
  -q "Process this Producer question card using the existing conversation context: ${QUESTION_CARD}. Use send_message action=list, then action=send to discord:${CHANNEL_ID} to report your answer or explicit blocker with the native card link. Return that response and the actual success, platform, chat_id and message_id, or the actual error."
```

## Verify

- Confirm the CLI's actual resume confirmation on stderr shows restored messages for the selected session, and retain its final `session_id:` line. A missing session, empty-history/fresh-start fallback, or unexplained identity change is not verified intake. Record an explicitly reported compression descendant rather than silently substituting an unrelated session.
- Intake requires a substantive answer or explicit blocker for the question, not only a proposed send or receipt. Channel reporting additionally requires the actual messaging-tool receipt confirming Discord, the requested channel and a real message ID. Posting or transcript mirroring alone does not prove intake.
- Return the selected `session_key`, requested and actual session IDs, response, and actual channel receipt or error to Producer. Process creation or exit code zero alone proves neither intake nor channel reporting. If it fails, return the exact error to Producer. Do not retry with changed or added arguments.
