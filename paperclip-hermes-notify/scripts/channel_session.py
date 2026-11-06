"""Read-only current-channel resolver for the installed Hermes runtime.

Calls native MCP conversation handlers in-process without starting EventBridge.
Reads only session metadata/message counts. Never launches an agent or sends a message.
"""
import argparse
import asyncio
import importlib
import json
import os
from pathlib import Path
import sqlite3
import sys


def decode_result(result):
    if isinstance(result, tuple):
        result = result[0]
    if hasattr(result, 'content'):
        result = result.content
    if isinstance(result, list):
        result = ''.join(getattr(item, 'text', '') for item in result)
    if isinstance(result, str):
        result = json.loads(result)
    if not isinstance(result, dict):
        raise RuntimeError('invalid_mcp_response')
    if 'error' in result:
        raise RuntimeError(str(result['error']))
    return result


def native_query():
    # Source installs keep the runtime at <source>/venv. A normal installed
    # module also works; never install packages or search other profiles here.
    source = Path(sys.prefix).parent
    if (source / 'mcp_serve.py').is_file():
        sys.path.insert(0, str(source))
    native = importlib.import_module('mcp_serve')
    bridge = native.EventBridge()
    server = native.create_mcp_server(event_bridge=bridge)

    async def query(name, arguments):
        if bridge._running:
            raise RuntimeError('unexpected_event_poller_started')
        return decode_result(await server.call_tool(name, arguments))

    return query


async def resolve_route(channel_id, query, expected_session=None):
    listed = decode_result(await query('conversations_list', {
        'platform': 'discord', 'search': channel_id, 'limit': 200}))
    candidates = listed.get('conversations')
    if not isinstance(candidates, list):
        raise RuntimeError('invalid_conversations_list')
    if len(candidates) >= 200 or listed.get('count', 0) >= 200:
        raise RuntimeError('session_search_truncated')
    matches = []
    for candidate in candidates:
        key = candidate.get('session_key')
        if not isinstance(key, str) or not key:
            raise RuntimeError('missing_session_key')
        detail = decode_result(await query('conversation_get', {'session_key': key}))
        if detail.get('platform') != 'discord' or str(detail.get('chat_id')) != channel_id:
            continue
        if detail.get('thread_id') is not None:
            raise RuntimeError('threaded_route_not_supported')
        sid = detail.get('session_id')
        if detail.get('session_key') != key or sid != candidate.get('session_id'):
            raise RuntimeError('session_route_changed')
        if not isinstance(sid, str) or not sid or '\n' in sid or '\r' in sid:
            raise RuntimeError('missing_or_invalid_session_id')
        matches.append({'session_key': key, 'session_id': sid, 'chat_id': channel_id,
                        'platform': 'discord', 'thread_id': None})
    if not matches:
        raise RuntimeError('channel_session_not_found')
    if len(matches) != 1:
        raise RuntimeError('ambiguous_channel_session')
    result = matches[0]
    if expected_session is not None and result['session_id'] != expected_session:
        raise RuntimeError('session_route_changed')
    return result


def saved_message_count(home, session_id):
    path = Path(home).resolve() / 'state.db'
    if not path.is_file():
        raise FileNotFoundError(str(path))
    # Do not construct SessionDB: its constructor can migrate a live database.
    with sqlite3.connect(path.as_uri() + '?mode=ro', uri=True) as db:
        row = db.execute('SELECT archived FROM sessions WHERE id = ?', (session_id,)).fetchone()
        if row is None:
            raise RuntimeError('saved_session_not_found')
        if row[0]:
            raise RuntimeError('session_archived')
        count = db.execute("SELECT COUNT(*) FROM messages WHERE session_id = ? AND role = 'user'",
                           (session_id,)).fetchone()[0]
    # A valid session can be empty immediately after /new. The count is
    # diagnostic metadata, not a prerequisite for using the current route.
    return count


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['resolve', 'check'])
    parser.add_argument('--channel-id', required=True)
    parser.add_argument('--binding', help='Exact JSON emitted by resolve; required for check')
    args = parser.parse_args(argv)
    if args.action == 'check' and not args.binding:
        parser.error('check requires --binding')
    try:
        if not args.channel_id.isdigit():
            raise RuntimeError('invalid_discord_channel_id')
        home = Path(os.environ.get('HERMES_HOME', str(Path.home() / '.hermes'))).resolve()
        previous = json.loads(args.binding) if args.action == 'check' else None
        if previous is not None and (previous.get('hermes_home') != str(home)
                                     or previous.get('chat_id') != args.channel_id):
            raise RuntimeError('session_binding_target_changed')
        expected = previous['session_id'] if previous is not None else None
        result = asyncio.run(resolve_route(args.channel_id, native_query(), expected))
        if previous is not None and result['session_key'] != previous.get('session_key'):
            raise RuntimeError('session_route_changed')
        result['hermes_home'] = str(home)
        result['saved_user_message_count'] = saved_message_count(home, result['session_id'])
        result['exclusive_use'] = 'not_checked'
        print(json.dumps(result), file=sys.stderr)
        print(json.dumps(result) if args.action == 'resolve' else result['session_id'])
        return 0
    except Exception as error:
        # Preserve the real error, do not retry or invent a replacement route.
        print(str(error), file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
