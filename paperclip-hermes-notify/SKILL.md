---
name: paperclip-hermes-notify
description: Use when a Producer needs to send a Paperclip question card to a Discord channel through Hermes.
---

# Paperclip question notification

## Start

Set `CHANNEL_ID` to the destination Discord channel and `QUESTION_CARD` to the question text and native card link, then run:

```bash
hermes chat --quiet --source tool --toolsets file,messaging \
  -q "Use send_message action=list, then action=send to discord:${CHANNEL_ID}. Send this question card: ${QUESTION_CARD}. Return the actual success, platform, chat_id and message_id, or the actual error."
```

## Verify

Delivery succeeds when the messaging-tool receipt confirms Discord, the requested channel and a real message ID. Process creation or exit code zero without that receipt is not verified delivery. Return the actual receipt or error to Producer.
