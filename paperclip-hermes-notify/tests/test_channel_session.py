"""Fixture-only tests; never open the operator's Hermes session store."""
import asyncio
import contextlib
import importlib.util
import io
import json
import os
import re
import shlex
import subprocess
from pathlib import Path
import sqlite3
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

HELPER = Path(__file__).resolve().parents[1] / 'scripts' / 'channel_session.py'


class ArtifactTests(unittest.TestCase):
    def test_query_command_is_bundled(self):
        self.assertTrue(HELPER.is_file(), 'Concrete session-query command is not bundled')


def load_helper():
    spec = importlib.util.spec_from_file_location('channel_session', HELPER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ResolveTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.mod = load_helper()
        self.entries = {
            'fixture-route-a': {'session_key': 'fixture-route-a', 'session_id': 'fixture-session-a',
                                'platform': 'discord', 'chat_id': '123', 'thread_id': None}}
        self.limit_hit = False

    async def query(self, name, arguments):
        if name == 'conversations_list':
            entries = [{'session_key': key, 'session_id': value['session_id']}
                       for key, value in self.entries.items()]
            return {'count': 200 if self.limit_hit else len(entries), 'conversations': entries}
        return dict(self.entries[arguments['session_key']])

    async def test_unique_exact_route(self):
        result = await self.mod.resolve_route('123', self.query)
        self.assertEqual(result['session_id'], 'fixture-session-a')
        self.assertEqual(result['session_key'], 'fixture-route-a')

    async def test_substring_match_is_not_the_destination(self):
        self.entries['unrelated'] = dict(self.entries['fixture-route-a'], chat_id='1234', session_key='unrelated')
        result = await self.mod.resolve_route('123', self.query)
        self.assertEqual(result['session_key'], 'fixture-route-a')

    async def test_ambiguous_user_routes_stop(self):
        self.entries['fixture-route-b'] = dict(self.entries['fixture-route-a'], session_key='fixture-route-b')
        with self.assertRaisesRegex(RuntimeError, 'ambiguous_channel_session'):
            await self.mod.resolve_route('123', self.query)

    async def test_missing_route_stops(self):
        self.entries.clear()
        with self.assertRaisesRegex(RuntimeError, 'channel_session_not_found'):
            await self.mod.resolve_route('123', self.query)

    async def test_truncated_search_stops(self):
        self.limit_hit = True
        with self.assertRaisesRegex(RuntimeError, 'session_search_truncated'):
            await self.mod.resolve_route('123', self.query)

    async def test_threaded_route_stops(self):
        self.entries['fixture-route-a']['thread_id'] = '456'
        with self.assertRaisesRegex(RuntimeError, 'threaded_route_not_supported'):
            await self.mod.resolve_route('123', self.query)

    async def test_list_detail_identity_race_stops(self):
        async def racing(name, arguments):
            result = await self.query(name, arguments)
            if name == 'conversation_get':
                result['session_id'] = 'fixture-new-session'
            return result
        with self.assertRaisesRegex(RuntimeError, 'session_route_changed'):
            await self.mod.resolve_route('123', racing)

    async def test_expected_session_must_not_change(self):
        with self.assertRaisesRegex(RuntimeError, 'session_route_changed'):
            await self.mod.resolve_route('123', self.query, expected_session='fixture-old-session')

    async def test_native_error_is_preserved(self):
        async def failing(name, arguments):
            return {'error': 'fixture native error, unchanged'}
        with self.assertRaisesRegex(RuntimeError, '^fixture native error, unchanged$'):
            await self.mod.resolve_route('123', failing)

    def test_sdk_tuple_is_decoded(self):
        result = ([SimpleNamespace(text=json.dumps({'count': 0, 'conversations': []}))], {})
        self.assertEqual(self.mod.decode_result(result)['count'], 0)


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.mod = load_helper()
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.home = Path(self.tmp.name)
        with sqlite3.connect(self.home / 'state.db') as db:
            db.executescript('CREATE TABLE sessions(id TEXT, archived INTEGER);'
                             'CREATE TABLE messages(session_id TEXT, role TEXT, content TEXT);')
            db.execute('INSERT INTO sessions VALUES (?, ?)', ('fixture-session', 0))
            db.execute('INSERT INTO messages VALUES (?, ?, ?)', ('fixture-session', 'user', 'FIXTURE ONLY'))

    def test_nonempty_history_is_counted_without_modifying_database(self):
        before = (self.home / 'state.db').read_bytes()
        self.assertEqual(self.mod.saved_message_count(self.home, 'fixture-session'), 1)
        self.assertEqual((self.home / 'state.db').read_bytes(), before)

    def test_empty_history_stops(self):
        with sqlite3.connect(self.home / 'state.db') as db:
            db.execute('DELETE FROM messages')
        with self.assertRaisesRegex(RuntimeError, 'empty_session_history'):
            self.mod.saved_message_count(self.home, 'fixture-session')

    def test_archived_session_stops(self):
        with sqlite3.connect(self.home / 'state.db') as db:
            db.execute('UPDATE sessions SET archived = 1')
        with self.assertRaisesRegex(RuntimeError, 'session_archived'):
            self.mod.saved_message_count(self.home, 'fixture-session')

    def test_missing_session_stops(self):
        with self.assertRaisesRegex(RuntimeError, 'saved_session_not_found'):
            self.mod.saved_message_count(self.home, 'fixture-missing')

    def test_missing_database_is_not_created(self):
        absent = self.home / 'absent-home'
        with self.assertRaises(FileNotFoundError):
            self.mod.saved_message_count(absent, 'fixture-session')
        self.assertFalse(absent.exists())

    def run_command(self, arguments, route_key='fixture-route'):
        async def query(name, args):
            if name == 'conversations_list':
                return {'count': 1, 'conversations': [
                    {'session_key': route_key, 'session_id': 'fixture-session'}]}
            return {'session_key': route_key, 'session_id': 'fixture-session',
                    'platform': 'discord', 'chat_id': '123', 'thread_id': None}
        out, err = io.StringIO(), io.StringIO()
        with patch.object(self.mod, 'native_query', return_value=query), \
                patch.dict(os.environ, {'HERMES_HOME': str(self.home)}), \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = self.mod.main(arguments)
        return code, out.getvalue(), err.getvalue()

    def test_concrete_resolve_then_check_commands(self):
        code, binding, _ = self.run_command(['resolve', '--channel-id', '123'])
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(binding)['exclusive_use'], 'not_checked')
        code, session_id, _ = self.run_command(['check', '--channel-id', '123', '--binding', binding])
        self.assertEqual(code, 0)
        self.assertEqual(session_id, 'fixture-session\n')

    def test_changed_route_key_stops_even_if_session_id_matches(self):
        _, binding, _ = self.run_command(['resolve', '--channel-id', '123'])
        code, stdout, stderr = self.run_command(
            ['check', '--channel-id', '123', '--binding', binding], route_key='different-route')
        self.assertEqual(code, 1)
        self.assertEqual(stdout, '')
        self.assertEqual(stderr.strip(), 'session_route_changed')

    def test_cross_profile_binding_stops(self):
        _, raw, _ = self.run_command(['resolve', '--channel-id', '123'])
        binding = json.loads(raw)
        binding['hermes_home'] = '/fixture/other-profile'
        code, stdout, stderr = self.run_command(
            ['check', '--channel-id', '123', '--binding', json.dumps(binding)])
        self.assertEqual(code, 1)
        self.assertEqual(stdout, '')
        self.assertEqual(stderr.strip(), 'session_binding_target_changed')


class CommandBlockTests(unittest.TestCase):
    def run_block(self, fail_action='', question=None, shell_flags=()):
        skill = (HELPER.parents[1] / 'SKILL.md').read_text()
        block = re.findall(r'```bash\n(.*?)\n```', skill, re.S)[0]
        if question is None:
            question = 'Fixture: "quoted", apostrophe\'s, $literal and $(printf LITERAL).\nfixture://card'
        values = {'SKILL_DIR': '/fixture/skill with spaces', 'HERMES_HOME': '/fixture/hermes',
                  'HERMES_PYTHON': 'fixture_python', 'CHANNEL_ID': '123'}
        for key, value in values.items():
            block, count = re.subn(r'^(?:export )?' + key + r'=.*$',
                                   lambda _: key + '=' + shlex.quote(value), block, flags=re.M)
            self.assertEqual(count, 1)
        # Fill the literal body last, without changing the input-reading command
        # or treating assignment-shaped lines in the question as shell inputs.
        placeholder = '<full question text and native card link>'
        self.assertEqual(block.count(placeholder), 1)
        block = block.replace(placeholder, question)
        prefix = r'''
if [[ "$FIXTURE_FAIL_ACTION" = read ]]; then
  read() { printf '%s\n' 'fixture input failure, unchanged' >&2; return 27; }
fi
fixture_python() {
  if [[ "$3" = "$FIXTURE_FAIL_ACTION" ]]; then
    printf '%s\n' 'fixture query failure, unchanged' >&2
    return 27
  fi
  case "$3" in
    resolve) printf '%s\n' '{"session_id":"fixture-session"}' ;;
    check) printf '%s\n' 'fixture-session' ;;
    *) return 91 ;;
  esac
}
hermes() { printf '%s\0' "$@"; }
'''
        env = dict(os.environ, FIXTURE_FAIL_ACTION=fail_action)
        result = subprocess.run(['/bin/bash', *shell_flags, '-c', prefix + block],
                                env=env, capture_output=True)
        return result, question

    def assert_delivery(self, result, question):
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stderr, b'')
        args = result.stdout.decode().split('\0')[:-1]
        expected_prompt = (
            'Process this Producer question card using the existing conversation context: '
            + question + '. Use send_message action=list, then action=send to discord:123 '
            'to report your answer or explicit blocker with the native card link. '
            'End that Discord message with this exact line: '
            'Source: Paperclip Producer via paperclip-hermes-notify. '
            'Return that response and the actual success, platform, chat_id and message_id, '
            'or the actual error.'
        )
        self.assertEqual(args, ['chat', '--quiet', '--resume', 'fixture-session',
                                '--source', 'tool', '--toolsets', 'file,messaging',
                                '-q', expected_prompt])

    def test_bash_preserves_special_characters_as_literal_input(self):
        cases = (
            "apostrophe's",
            '"double quotes" and single \'quotes\'',
            '$literal $(printf SHOULD_NOT_RUN) `printf SHOULD_NOT_RUN`',
            '中文問題\n  indented line\nbackslash \\path and ) * ? [abc]',
            '',
            '  leading and trailing spaces  ',
            'line\n',
            'line\n\n',
            "CHANNEL_ID='literal question line'\nQUESTION_CARD=literal text",
        )
        for question in cases:
            with self.subTest(question=question):
                result, _ = self.run_block(question=question)
                self.assert_delivery(result, question)

    def test_input_reading_succeeds_with_errexit_and_nounset(self):
        result, question = self.run_block(shell_flags=('-e', '-u'))
        self.assert_delivery(result, question)

    def test_fixed_block_preserves_literal_question_and_flags(self):
        result, question = self.run_block()
        self.assert_delivery(result, question)

    def test_unexpected_read_failure_stops_before_hermes(self):
        result, _ = self.run_block('read')
        self.assertEqual(result.returncode, 27)
        self.assertEqual(result.stdout, b'')
        self.assertEqual(result.stderr, b'fixture input failure, unchanged\n')

    def test_resolve_failure_stops_before_hermes(self):
        result, _ = self.run_block('resolve')
        self.assertEqual(result.returncode, 27)
        self.assertEqual(result.stdout, b'')
        self.assertEqual(result.stderr, b'fixture query failure, unchanged\n')

    def test_recheck_failure_stops_before_hermes(self):
        result, _ = self.run_block('check')
        self.assertEqual(result.returncode, 27)
        self.assertEqual(result.stdout, b'')
        self.assertEqual(result.stderr, b'fixture query failure, unchanged\n')


if __name__ == '__main__':
    unittest.main()
