"""Fund B (aggressive): $100 = 50% swing (leveraged/high-beta, -15% stop) + 50% day-trade sleeve.
Day-trade rule: at ~10:00 ET buy the watchlist name with the strongest gain vs prior close (must be > +0.5%),
with a -3% stop checked against real 5-min intraday lows; always flat by ~3:50 ET. 0.05% slippage per fill."""
import json,sys,datetime,urllib.request
from px import hist
L="ledger_b.json"; SLIP=0.0005; SWING_STOP=-0.15; DT_STOP=-0.03
WATCH=["TQQQ","SOXL","NVDA","TSLA","COIN","MSTR","PLTR"]
today=str(datetime.date.today())
def load(): return json.load(open(L))
def save(d): json.dump(d,open(L,"w"),indent=1)
def price(t): return hist(t,"5d")[0]
def intraday(t):
    u=f"https://query1.finance.yahoo.com/v8/finance/chart/{t}?range=1d&interval=5m"
    r=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"}),timeout=15))["chart"]["result"][0]
    return r["meta"],r["timestamp"],r["indicators"]["quote"][0]
def init(swing):
    d={"start":100.0,"cash":100.0,"swing":{},"dt":None,"dt_cash":50.0,"trades":[],"days":[]}
    for t,amt in swing.items():
        p=price(t)*(1+SLIP); d["swing"][t]={"qty":amt/p,"entry":p}; d["cash"]-=amt
        d["trades"].append([today,"BUY",t,round(amt/p,6),round(p,4)])
    d["cash"]-=50.0   # dt_cash is tracked separately
    save(d); report(d,"Day 0")
def dt_open():
    d=load()
    if d["dt"]: print("already in a day trade"); return
    best=None
    for t in WATCH:
        m,_,_=intraday(t); g=m["regularMarketPrice"]/m["chartPreviousClose"]-1
        print(f"  scan {t:5} {g:+.2%}")
        if g>0.005 and (not best or g>best[1]): best=(t,g,m["regularMarketPrice"])
    if not best: print("No name > +0.5% -> sitting in cash today"); d["trades"].append([today,"DT-SKIP","-",0,0]); save(d); return
    t,g,p=best; p*=1+SLIP; q=d["dt_cash"]/p
    d["dt"]={"t":t,"qty":q,"entry":p,"ts":int(datetime.datetime.now().timestamp())}
    d["trades"].append([today,"DT-BUY",t,round(q,6),round(p,4)]); save(d)
    print(f"DAY TRADE: bought {t} (up {g:+.2%} on the day) at {p:.2f} with ${d['dt_cash']:.2f}")
def dt_close():
    d=load(); x=d["dt"]
    if not x: print("no open day trade"); return
    m,ts,q=intraday(x["t"]); stop=x["entry"]*(1+DT_STOP)
    lows=[l for s,l in zip(ts,q["low"]) if l and s>=x["ts"]]
    if lows and min(lows)<=stop: p=stop; how="STOPPED at -3%"
    else: p=m["regularMarketPrice"]; how="closed at end of day"
    p*=1-SLIP; proceeds=x["qty"]*p; pnl=proceeds-d["dt_cash"]
    d["trades"].append([today,"DT-SELL",x["t"],round(x["qty"],6),round(p,4)])
    print(f"DAY TRADE {x['t']}: {how} at {p:.2f} -> {pnl:+.2f} ({proceeds/d['dt_cash']-1:+.2%})")
    d["dt_cash"]=proceeds; d["dt"]=None; save(d)
def report(d=None,label=None):
    d=d or load(); tot=d["cash"]+d["dt_cash"]; rows=[]
    if d["dt"]: tot+=d["dt"]["qty"]*price(d["dt"]["t"])-d["dt_cash"]
    for t,x in list(d["swing"].items()):
        p=price(t); v=x["qty"]*p; chg=p/x["entry"]-1
        if chg<=SWING_STOP:
            proceeds=v*(1-SLIP); del d["swing"][t]; d["cash"]+=proceeds; tot+=proceeds
            d["trades"].append([today,"STOP-SELL",t,round(x["qty"],6),round(p,4)])
            rows.append(f"  {t:8} STOPPED OUT ({chg:+.1%}) -> ${proceeds:.2f} to cash"); continue
        tot+=v; rows.append(f"  {t:8} ${v:7.2f}  ({chg:+.2%} vs entry)")
    rows.append(f"  day-trade sleeve ${d['dt_cash']:.2f}" + ("" if not d["cash"] else f" | idle cash ${d['cash']:.2f}"))
    prev=d["days"][-1]["value"] if d["days"] else d["start"]
    d["days"].append({"date":today,"label":label or f"Day {len(d['days'])}","value":round(tot,2)}); save(d)
    print(f"FUND B {d['days'][-1]['label']} {today} value=${tot:.2f} day={tot-prev:+.2f} ({tot/prev-1:+.2%}) total={tot-d['start']:+.2f} ({tot/d['start']-1:+.2%})")
    print("\n".join(rows))
if __name__=="__main__":
    c=sys.argv[1]
    if c=="init": init({"MSTR":15,"ETH-USD":15,"PLTR":10,"TQQQ":10})
    elif c=="open": dt_open()
    elif c=="close": dt_close()
    else: report(label=sys.argv[2] if len(sys.argv)>2 else None)
