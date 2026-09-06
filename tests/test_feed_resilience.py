import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from predicter.feeds import espn_parse
from predicter.experiment import initialize, run
from predicter.engine import utcnow


def scoreboard(odds):
    return {'events': [{'id': '1', 'name': 'Away at Home', 'date': '2026-09-07T18:00Z',
                        'competitions': [{'competitors': [
                            {'homeAway': 'home', 'team': {'displayName': 'Home'}},
                            {'homeAway': 'away', 'team': {'displayName': 'Away'}}],
                            'status': {'type': {'state': 'pre'}}, 'odds': odds}]}]}


def valid_quote():
    return {'provider': {'name': 'DraftKings'}, 'moneyline': {
        'home': {'close': {'odds': '-110'}}, 'away': {'close': {'odds': '+100'}}}}


class FeedResilienceTests(unittest.TestCase):
    def test_null_entries_do_not_discard_valid_quotes(self):
        rows = espn_parse(scoreboard([None, valid_quote()]), 'mlb', 'now')
        self.assertEqual(len(rows[0]['bookmakers']), 1)
        self.assertEqual(rows[0]['bookmakers'][0]['key'], 'draftkings')

    def test_null_collection_and_provider_are_unpriced(self):
        for odds in (None, [None], [{'provider': None}], [{'provider': {'name': None}}]):
            with self.subTest(odds=odds):
                self.assertEqual(espn_parse(scoreboard(odds), 'mlb', 'now')[0]['bookmakers'], [])

    def test_incomplete_moneyline_is_not_a_price(self):
        for field in (None, {}, {'home': None}, {'home': {'close': None}}):
            q = valid_quote(); q['moneyline'] = field
            self.assertEqual(espn_parse(scoreboard([q]), 'mlb', 'now')[0]['bookmakers'], [])

    def test_unexpected_scan_failure_persists_health_and_trial(self):
        with tempfile.TemporaryDirectory() as d:
            state = initialize(utcnow())
            state['last_opportunities'] = [{'ticker': 'STALE-PRIOR-SCAN'}]
            original = copy.deepcopy(state)
            (Path(d)/'state.json').write_text(json.dumps(state))
            with patch('predicter.experiment.scan', side_effect=AttributeError('unexpected schema')), patch('predicter.experiment.enter') as entry, patch('builtins.print'):
                self.assertEqual(run(d), 1)
                entry.assert_not_called()
            saved = json.loads((Path(d)/'state.json').read_text())
            self.assertEqual(saved['started_at'], original['started_at'])
            self.assertEqual(saved['entries_end_at'], original['entries_end_at'])
            self.assertEqual(saved['policy_hash'], original['policy_hash'])
            self.assertEqual(saved['positions'], original['positions'])
            self.assertEqual(saved['scans'], 1)
            self.assertIn('AttributeError', saved['errors'][0])
            self.assertIn('AttributeError', (Path(d)/'README.md').read_text())
            self.assertEqual(saved['last_opportunities'], [])
