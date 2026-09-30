import json,urllib.request,sys
def hist(t,rng="3mo"):
    u=f"https://query1.finance.yahoo.com/v8/finance/chart/{t}?range={rng}&interval=1d"
    r=json.load(urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":"Mozilla/5.0"}),timeout=15))["chart"]["result"][0]
    c=[x for x in r["indicators"]["quote"][0]["close"] if x]
    return r["meta"]["regularMarketPrice"],c
if __name__=="__main__":
    for t in sys.argv[1:]:
        try:
            p,c=hist(t); import statistics as s
            rets=[c[i]/c[i-1]-1 for i in range(1,len(c))]
            print(f"{t:10} px={p:10.2f} 1m={p/c[-22]-1:+.1%} 3m={p/c[0]-1:+.1%} dailyvol={s.pstdev(rets):.2%}")
        except Exception as e: print(t,"ERR",e)
