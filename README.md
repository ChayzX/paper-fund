# paper-fund

A one-week paper-trading experiment (Sep 30 – Oct 7, 2026). **Simulated money, real prices** (Yahoo Finance),
0.05% slippage charged on every fill. Run by Claude Code on a schedule; every event commits the updated ledgers here,
so `git log` is the trade-by-trade history.

| Fund | Start | Strategy |
|---|---|---|
| **A — Safe** (`fund.py`, `ledger.json`) | $100 | Buy & hold: 40% SPY, 20% XLK, 10% XLV, 15% BTC, 15% SHV. -8% stop → SHV |
| **B — Aggressive** (`fund_b.py`, `ledger_b.json`) | $100 | 50% swing (MSTR, ETH, PLTR, TQQQ; -15% stop) + 50% daily momentum day-trade (-3% stop, flat by close) |
| **C — High-risk day trading** (`fund_c.py`, `ledger_c.json`) | $1000 | Cash account. 10:00 ET buy top-2 leveraged-ETF gainers (>+1%), -4% stop / +6% take-profit on 5-min bars, flat by 3:50 ET |

Benchmark: just holding SPY from $766.42.

## Schedule (UTC)
- 14:00 weekdays — `./run.sh open` (B + C day trades)
- 19:50 weekdays — `./run.sh close`
- 20:20 daily — `./run.sh report "Day N"` (all three funds)

## Run it yourself
```bash
./run.sh report "manual"   # needs only python3 + internet; no API keys
```
