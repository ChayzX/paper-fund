#!/bin/bash
# Usage: run.sh open | close | report "Day N"   — runs all funds, then syncs ledgers to the paper-fund repo if it's cloned.
cd /home/user
case "$1" in
  open)   python3 fund_b.py open;  echo; python3 fund_c.py open ;;
  close)  python3 fund_b.py close; echo; python3 fund_c.py close ;;
  report) python3 fund.py report "$2"; echo; python3 fund_b.py report "$2"; echo; python3 fund_c.py report "$2" ;;
esac
if [ -d /home/user/paper-fund/.git ]; then
  cp *.py run.sh ledger*.json /home/user/paper-fund/ && cd /home/user/paper-fund && git add -A && \
  git commit -qm "$1 $2 $(date -u +%F)" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -m "Claude-Session: https://claude.ai/code/session_011o8fQGNQZuUFCQAPrN2nGW" && git push -q origin HEAD && echo "(synced to GitHub)"
fi
