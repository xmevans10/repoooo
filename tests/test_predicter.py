import copy
import json
import tempfile
import unittest
from datetime import timedelta
from unittest.mock import patch
from predicter.engine import analyze, decimal, devig, utcnow
from predicter.ledger import Ledger
from predicter.kalshi import fee, scan


def event():
    now = utcnow()
    return dict(id='test', sport_key='baseball_mlb', name='A at B',
                commence_time=(now+timedelta(hours=1)).isoformat(), retrieved_at=now.isoformat(),
                bookmakers=[dict(key=k, prices={'A': p, 'B': q}, last_update=now.isoformat())
                    for k,p,q in [('draftkings',2.2,1.75), ('fanduel',1.8,2.1),
                                  ('betmgm',1.8,2.1), ('pinnacle',1.8,2.1)]])


class EngineTests(unittest.TestCase):
    def test_odds_and_margin(self):
        self.assertEqual(decimal(150), 2.5)
        self.assertEqual(decimal(-200), 1.5)
        self.assertEqual(devig({'A':1.91,'B':1.91}), {'A':.5,'B':.5})
        for invalid in [0, 50, float('nan')]:
            with self.assertRaises(ValueError): decimal(invalid)

    def test_target_excluded(self):
        rows = analyze([event()])
        r = next(r for r in rows if r['book']=='draftkings' and r['outcome']=='A')
        self.assertGreater(r['stake'],0)
        self.assertNotIn('draftkings',r['references'])
        self.assertAlmostEqual(r['probability'], 2.1/3.9)
        self.assertLessEqual(r['stake'],10)

    def test_stale_missing_and_live(self):
        e = event()
        for b in e['bookmakers']: b['last_update'] = None
        self.assertTrue(all(r['stake']==0 for r in analyze([e])))
        e = event(); e['commence_time'] = (utcnow()-timedelta(seconds=1)).isoformat()
        self.assertEqual(analyze([e]),[])
        e = event();e['bookmakers'][0]['last_update']=(utcnow()-timedelta(minutes=6)).isoformat()
        self.assertTrue(all(r['stake']==0 for r in analyze([e]) if r['book']=='draftkings'))

    def test_draw_market_mismatch(self):
        e=event();e['bookmakers'][1]['prices']={'A':3,'B':3,'Draw':3}
        self.assertTrue(all(r['stake']==0 for r in analyze([e])))

    def test_partial_market_and_future_timestamp(self):
        e=event();e['bookmakers'][1]['prices']={'A':2}
        self.assertTrue(all(r['stake']==0 for r in analyze([e])))
        e=event();e['bookmakers'][0]['last_update']=(utcnow()+timedelta(minutes=1)).isoformat()
        self.assertTrue(all(r['stake']==0 for r in analyze([e]) if r['book']=='draftkings'))


class LedgerTests(unittest.TestCase):
    def test_exposure_duplicates_and_settlement(self):
        with tempfile.TemporaryDirectory() as d:
            ledger=Ledger(d+'/test.sqlite')
            r=analyze([event()])[0]
            rows=[dict(r,event_id=str(i),stake=10) for i in range(10)]
            ledger.paper(rows);ledger.paper(rows)
            self.assertEqual(ledger.summary()['exposure'],50)
            self.assertEqual(ledger.summary()['open_bets'],5)
            with self.assertRaises(ValueError): ledger.settle(1,'win')
            with patch('predicter.ledger.utcnow',return_value=utcnow()+timedelta(hours=2)):
                ledger.settle(1,'win')
                with self.assertRaises(ValueError): ledger.settle(1,'win')
                ledger.settle(2,'loss');ledger.settle(3,'push');ledger.settle(4,'void')
            self.assertAlmostEqual(ledger.summary()['profit'],2)
            self.assertEqual(ledger.summary()['exposure'],10)
            self.assertAlmostEqual(ledger.summary()['available'],992)
            self.assertIsNotNone(ledger.summary()['brier'])


class KalshiTests(unittest.TestCase):
    def test_fee_rounding(self):
        self.assertEqual(fee(100,.5,1),1.75)
        self.assertEqual(fee(1,.5,1),.02)
        self.assertEqual(fee(100,.5,2),3.5)
        with self.assertRaises(ValueError): fee(1,.5,float('nan'))

    def test_no_forecast_no_trade(self):
        m=dict(ticker='X',event_ticker='E',title='Test',rules_primary='Rule',yes_ask_dollars='.5')
        with patch('predicter.kalshi.fetch',side_effect=[{'series':{}},{'markets':[m]}]):
            r=scan()['markets'][0]
        self.assertEqual(r['contracts'],0)

    def test_rule_mismatch_rejected(self):
        m=dict(ticker='X',event_ticker='E',title='Test',rules_primary='Rule',yes_ask_dollars='.5')
        with patch('predicter.kalshi.fetch',side_effect=[{'series':{}},{'markets':[m]}]):
            r=scan(forecasts={'X':{'rules_verified':True,'rules_primary':'Different'}})['markets'][0]
        self.assertEqual(r['contracts'],0)
        self.assertIn('rules',r['reason'])

class BenchmarkTests(unittest.TestCase):
    def test_exact_match_and_wrong_date_rejection(self):
        from predicter.benchmark import match
        e=event();e.update(sport_key='mlb',status='pre',commence_time='2026-09-06T17:35:00Z')
        e['bookmakers']=[dict(key='draftkings',prices={'Los Angeles Angels':2.5,'Pittsburgh Pirates':1.6})]
        m={'rules':'If Los Angeles A wins the Los Angeles A vs Pittsburgh professional baseball game originally scheduled for Sep 6, 2026 at 1:35 PM EDT, then the market resolves to Yes.'}
        self.assertEqual(match(m,[e])[2],'Los Angeles Angels')
        e['commence_time']='2026-09-07T17:35:00Z'
        self.assertIsNone(match(m,[e]))

    def test_ambiguous_match_rejected(self):
        from predicter.benchmark import resolve
        self.assertIsNone(resolve('New York',['New York Mets','New York Yankees']))


if __name__=='__main__': unittest.main()
