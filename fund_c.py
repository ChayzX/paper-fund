"""Fund C (high-risk day trading): $1000 cash account (no margin -> PDT rule doesn't apply; T+1 settles overnight).
~10:00 ET: buy the TOP 2 watchlist gainers vs prior close (each must be > +1%), half the cash each.
Each position: -4% stop / +6% take-profit, simulated bar-by-bar on real 5-min highs/lows (stop wins ties = conservative).
Always flat by ~3:50 ET. 0.05% slippage per fill."""
import json,sys,datetime,urllib.request
L="ledger_c.json"; SLIP=0.0005; STOP=-0.04; TAKE=0.06; MIN_GAIN=0.01
WATCH=["SOXL","TQQQ","FNGU","NVDL","TSLL","MSTU","CONL","LABU"]
today=str(datetime.date.today())
def load(): return json.load(open(L))
def save(d): json.dump(d,open(L,"w"),indent=1)
def intraday(t):
    u=f"https://query1.finance.yahoo.com/v8/finance/chart/{t}?range=1d&interval=5m"
    r=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"}),timeout=15))["chart"]["result"][0]
    return r["meta"],r["timestamp"],r["indicators"]["quote"][0]
def init():
    save({"start":1000.0,"cash":1000.0,"open":[],"trades":[],"days":[],"wins":0,"losses":0}); print("Fund C: $1000.00 cash, ready")
def dt_open():
    d=load()
    if d["open"]: print("positions already open"); return
    scan=[]
    for t in WATCH:
        try: m,_,_=intraday(t); g=m["regularMarketPrice"]/m["chartPreviousClose"]-1; scan.append((g,t,m["regularMarketPrice"]))
        except Exception as e: print(f"  {t} data error {e}")
    scan.sort(reverse=True)
    for g,t,_ in scan: print(f"  scan {t:5} {g:+.2%}")
    picks=[s for s in scan if s[0]>MIN_GAIN][:2]
    if not picks: print("Nothing up > +1% -> Fund C sits in cash today"); d["trades"].append([today,"SKIP","-",0,0]); save(d); return
    alloc=d["cash"]/len(picks)
    for g,t,p in picks:
        p*=1+SLIP; q=alloc/p
        d["open"].append({"t":t,"qty":q,"entry":p,"cost":alloc,"ts":int(datetime.datetime.now().timestamp())})
        d["trades"].append([today,"BUY",t,round(q,4),round(p,4)]); print(f"BUY {t} (up {g:+.2%}) ${alloc:.2f} @ {p:.2f}")
    d["cash"]-=alloc*len(picks); save(d)
def dt_close():
    d=load()
    for x in d["open"]:
        m,ts,q=intraday(x["t"]); stop=x["entry"]*(1+STOP); take=x["entry"]*(1+TAKE); exitp=None
        for s,lo,hi in zip(ts,q["low"],q["high"]):
            if s<x["ts"] or lo is None: continue
            if lo<=stop: exitp,how=stop,"STOP -4%"; break
            if hi>=take: exitp,how=take,"TAKE-PROFIT +6%"; break
        if exitp is None: exitp,how=m["regularMarketPrice"],"closed at end of day"
        exitp*=1-SLIP; proceeds=x["qty"]*exitp; pnl=proceeds-x["cost"]
        d["cash"]+=proceeds; d["wins" if pnl>0 else "losses"]+=1
        d["trades"].append([today,"SELL",x["t"],round(x["qty"],4),round(exitp,4)])
        print(f"SELL {x['t']}: {how} @ {exitp:.2f} -> {pnl:+.2f} ({pnl/x['cost']:+.2%})")
    d["open"]=[]; save(d)
def report(label=None):
    d=load(); tot=d["cash"]+sum(x["cost"] for x in d["open"])
    prev=d["days"][-1]["value"] if d["days"] else d["start"]
    d["days"].append({"date":today,"label":label or f"Day {len(d['days'])}","value":round(tot,2)}); save(d)
    print(f"FUND C {d['days'][-1]['label']} {today} value=${tot:.2f} day={tot-prev:+.2f} ({tot/prev-1:+.2%}) total={tot-d['start']:+.2f} ({tot/d['start']-1:+.2%}) | record {d['wins']}W-{d['losses']}L")
if __name__=="__main__":
    c=sys.argv[1]
    {"init":init,"open":dt_open,"close":dt_close}.get(c,lambda:report(sys.argv[2] if len(sys.argv)>2 else None))()
