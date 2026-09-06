import json
import sqlite3
from pathlib import Path
from .engine import stamp, utcnow


class Ledger:
    def __init__(self, path='data/paper.sqlite'):
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path)
        self.db.row_factory = sqlite3.Row
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS bets (
          id INTEGER PRIMARY KEY, event_id TEXT UNIQUE, created TEXT, payload TEXT,
          stake_cents INTEGER, result TEXT, profit_cents INTEGER, settled TEXT);
        CREATE TABLE IF NOT EXISTS scans (
          id INTEGER PRIMARY KEY, created TEXT, payload TEXT);
        ''')

    def summary(self):
        rows = list(self.db.execute('SELECT * FROM bets ORDER BY id'))
        profit = sum(r['profit_cents'] or 0 for r in rows)
        exposure = sum(r['stake_cents'] for r in rows if r['result'] is None)
        settled = [r for r in rows if r['result'] is not None]
        risked = sum(r['stake_cents'] for r in settled if r['result'] != 'void')
        peak, balance, drawdown = 100000, 100000, 0
        for r in sorted(settled, key=lambda r: (r['settled'], r['id'])):
            balance += r['profit_cents']
            peak = max(peak, balance)
            drawdown = max(drawdown, (peak - balance) / peak)
        scored = [r for r in settled if r['result'] in ('win', 'loss')]
        brier = sum((json.loads(r['payload'])['probability'] - (r['result'] == 'win'))**2 for r in scored) / len(scored) if scored else None
        return dict(starting_bankroll=1000, equity=(100000+profit)/100,
                    available=(100000+profit-exposure)/100, exposure=exposure/100,
                    profit=profit/100, settled=len(settled), roi=profit/risked if risked else None,
                    max_drawdown=drawdown, brier=brier, open_bets=len(rows)-len(settled))

    def record_scan(self, report):
        with self.db:
            self.db.execute('INSERT INTO scans(created,payload) VALUES (?,?)',
                            (report['created'], json.dumps(report)))

    def paper(self, rows):
        accepted = []
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            for row in rows:
                s = self.summary()
                now = utcnow()
                if row['stake'] <= 0 or row['reason'] != 'Paper candidate':
                    continue
                if stamp(row['commence_time']) <= now or not row['quote_time'] or not 0 <= (now-stamp(row['quote_time'])).total_seconds() <= 300:
                    continue
                cents = int(round(min(row['stake'], s['equity']*.01,
                                      s['available'], max(0, s['equity']*.05-s['exposure']))*100))
                if cents < 100:
                    continue
                copy = dict(row, stake=cents/100)
                cur = self.db.execute('INSERT OR IGNORE INTO bets(event_id,created,payload,stake_cents) VALUES (?,?,?,?)',
                                      (row['event_id'], now.isoformat(), json.dumps(copy), cents))
                if cur.rowcount:
                    accepted.append(copy)
        return accepted

    def settle(self, bet_id, result):
        if result not in ('win', 'loss', 'push', 'void'):
            raise ValueError('Invalid result')
        with self.db:
            self.db.execute('BEGIN IMMEDIATE')
            row = self.db.execute('SELECT * FROM bets WHERE id=?', (bet_id,)).fetchone()
            if not row or row['result']:
                raise ValueError('Bet absent or already settled')
            data = json.loads(row['payload'])
            if stamp(data['commence_time']) > utcnow():
                raise ValueError('Cannot settle before event start')
            profit = round(row['stake_cents']*(data['decimal_odds']-1)) if result == 'win' else -row['stake_cents'] if result == 'loss' else 0
            self.db.execute('UPDATE bets SET result=?,profit_cents=?,settled=? WHERE id=?',
                            (result, profit, utcnow().isoformat(), bet_id))

    def bets(self):
        return [dict(r) for r in self.db.execute('SELECT * FROM bets ORDER BY id DESC')]
