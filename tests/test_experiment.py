import unittest
from datetime import timedelta
from predicter.engine import utcnow
from predicter.experiment import initialize, enter, settle, accounting, assess


def sample():
    now=utcnow()
    b=dict(ticker='TEST',event='Away at Home',selection='Home',probability=.7,raw_gap=.2,
           commence_time=(now+timedelta(hours=2)).isoformat(),retrieved_at=now.isoformat(),source='test')
    m=dict(ticker='TEST',event='EVENT',rules='Exact rules',rules_secondary='Secondary',
           fee_type='quadratic',fee_multiplier=1)
    fresh=dict(status='active',rules_primary='Exact rules',rules_secondary='Secondary',
               yes_ask_dollars='.5',yes_bid_dollars='.49',yes_ask_size_fp='1000')
    return now,b,m,fresh


class ExperimentTests(unittest.TestCase):
    def test_fees_limits_dedup_settlement(self):
        now,b,m,fresh=sample();s=initialize(now)
        get=lambda url:{'market':fresh}
        enter(s,[b],[m],now,get);enter(s,[b],[m],now,get)
        self.assertEqual(len(s['positions']),1)
        p=s['positions'][0]
        self.assertLessEqual(p['cost_cents'],1000)
        self.assertGreater(p['fee_cents'],0)
        self.assertEqual(accounting(s)['equity_cents'],100000)
        settle(s,now,lambda url:{'market':{'status':'settled','result':'yes'}})
        expected=100000+p['contracts']*100-p['cost_cents']
        self.assertEqual(accounting(s)['equity_cents'],expected)
        settle(s,now,lambda url:self.fail('Settled position fetched twice'))
        self.assertEqual(accounting(s)['exposure_cents'],0)

    def test_exposure_cap(self):
        now,b,m,fresh=sample();s=initialize(now)
        for i in range(20):
            enter(s,[dict(b,ticker=str(i))],[dict(m,ticker=str(i),event=str(i))],now,lambda url:{'market':fresh})
        self.assertLessEqual(accounting(s)['exposure_cents'],5000)

    def test_changed_rules_missing_depth_wide_spread(self):
        now,b,m,fresh=sample()
        for change in [dict(rules_primary='different'),dict(yes_ask_size_fp='0'),dict(yes_bid_dollars='.1')]:
            s=initialize(now)
            enter(s,[b],[m],now,lambda url:{'market':dict(fresh,**change)})
            self.assertEqual(s['positions'],[])

    def test_expired_window_and_near_start(self):
        now,b,m,fresh=sample();s=initialize(now-timedelta(days=31))
        enter(s,[b],[m],now,lambda url:self.fail('Should not request a quote'))
        self.assertEqual(s['positions'],[])
        s=initialize(now);b['commence_time']=(now+timedelta(minutes=5)).isoformat()
        enter(s,[b],[m],now,lambda url:self.fail('Too near start'))
        self.assertEqual(s['positions'],[])

    def test_missing_settlement_keeps_exposure(self):
        now,b,m,fresh=sample();s=initialize(now)
        enter(s,[b],[m],now,lambda url:{'market':fresh})
        settle(s,now,lambda url:{'market':{'status':'settled'}})
        self.assertTrue(s['errors'])
        self.assertGreater(accounting(s)['exposure_cents'],0)

    def test_no_trades_not_success(self):
        now=utcnow();s=initialize(now-timedelta(days=31))
        self.assertIn('Inconclusive',assess(s,now)['verdict'])
        self.assertIsNone(assess(s,now)['roi'])

    def test_positive_sample_still_needs_minimum(self):
        now,b,m,fresh=sample();s=initialize(now)
        enter(s,[b],[m],now,lambda url:{'market':fresh})
        settle(s,now,lambda url:{'market':{'status':'settled','result':'yes'}})
        self.assertIn('Inconclusive',assess(s,now+timedelta(days=31))['verdict'])
