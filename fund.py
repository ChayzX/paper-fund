"""Paper-trading ledger: $100 start, real Yahoo prices, 0.05% slippage per fill, 8% per-position stop -> SHV."""
import json,sys,os,datetime
from px import hist
L="ledger.json"; SLIP=0.0005; STOP=-0.08
def load(): return json.load(open(L))
def save(d): json.dump(d,open(L,"w"),indent=1)
def price(t): return hist(t,"5d")[0]
def init(alloc):
    d={"start":100.0,"cash":100.0,"pos":{},"trades":[],"days":[]}
    for t,w in alloc.items():
        p=price(t)*(1+SLIP); amt=100*w; q=amt/p
        d["pos"][t]={"qty":q,"entry":p}; d["cash"]-=amt
        d["trades"].append([str(datetime.date.today()),"BUY",t,round(q,6),round(p,4)])
    save(d); report(d,"Day 0")
def report(d=None,label=None):
    d=d or load(); tot=d["cash"]; rows=[]
    for t,x in list(d["pos"].items()):
        p=price(t); v=x["qty"]*p; chg=p/x["entry"]-1
        if chg<=STOP and t!="SHV":                       # risk rule: stop-loss into T-bills
            proceeds=v*(1-SLIP); del d["pos"][t]
            s=price("SHV")*(1+SLIP); sh=d["pos"].setdefault("SHV",{"qty":0,"entry":s})
            sh["entry"]=(sh["entry"]*sh["qty"]+proceeds)/(sh["qty"]+proceeds/s); sh["qty"]+=proceeds/s
            d["trades"].append([str(datetime.date.today()),"STOP-SELL",t,round(x["qty"],6),round(p,4)])
            rows.append(f"  {t:8} STOPPED OUT at {p:.2f} ({chg:+.1%}) -> moved ${proceeds:.2f} to SHV"); tot+=proceeds; continue
        tot+=v; rows.append(f"  {t:8} ${v:7.2f}  ({chg:+.2%} vs entry)")
    prev=d["days"][-1]["value"] if d["days"] else d["start"]
    d["days"].append({"date":str(datetime.date.today()),"label":label or f"Day {len(d['days'])}","value":round(tot,2)})
    save(d)
    print(f"{d['days'][-1]['label']}  {datetime.date.today()}  value=${tot:.2f}  day={tot-prev:+.2f} ({tot/prev-1:+.2%})  total={tot-d['start']:+.2f} ({tot/d['start']-1:+.2%})")
    print("\n".join(rows))
if __name__=="__main__":
    if sys.argv[1]=="init": init({"SPY":.40,"XLK":.20,"XLV":.10,"BTC-USD":.15,"SHV":.15})
    else: report(label=sys.argv[2] if len(sys.argv)>2 else None)
