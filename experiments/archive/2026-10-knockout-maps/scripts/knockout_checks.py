"""Ad hoc checks quoted in notes/knockout-map-results.md (run in WSL from the repo root, after knockout.py and knockout_analyse.py). Three sections: null hot-rate, ring/route profile, refinement tops."""
# ---- section 1: null hot rate and hot tile list
import numpy as np, json
rng=np.random.default_rng(1)
for r in ["RRRRRLLLLLL","RLLLLRRRRLR"]:
    d=f"experiments/archive/2026-10-knockout-maps/knock/{r}/"
    rows=np.genfromtxt(d+"coarse.csv",delimiter=",",names=True,dtype=None,encoding=None)
    B=float(np.genfromtxt(d+"base.csv",delimiter=",",names=True)["near_home"])
    null=B-rows["near_home"][rows["kind"]=="swap"]
    p95=np.quantile(null,.95); m3=np.quantile(rng.choice(null,(20000,3)).mean(1),.95)
    t=rng.choice(null,(200000,3))
    h=(t.mean(1)>m3)&((t>p95).sum(1)>=2)
    print(r,"null hot rate",h.mean())
    print(open(d+"hot.csv").read()[:900])
    T=np.genfromtxt(d+"tiles.csv",delimiter=",",names=True)
    print("loss>0.05:",(T["loss"]>0.05).sum(),"of",len(T)," dist<10:",(T["dist"]<10).sum(), "mean loss dist<10 / 10-25 / >25:",[round(T["loss"][m].mean(),4) for m in (T["dist"]<10,(T["dist"]>=10)&(T["dist"]<25),T["dist"]>=25)])

# ---- section 2: loss and excursion share by radius
import numpy as np
S,C=4096,2048
for r in ["RRRRRLLLLLL","RLLLLRRRRLR"]:
    d=f"experiments/archive/2026-10-knockout-maps/knock/{r}/"
    T=np.genfromtxt(d+"tiles.csv",delimiter=",",names=True)
    occ=np.fromfile(d+"occ.u32",dtype="<u4").reshape(S,S).astype(float)
    route=np.fromfile(d+"route.u32",dtype="<u4").reshape(S,S).astype(float)
    # share of excursion steps by radius ring
    yy,xx=np.mgrid[-C:C,-C:C]; rad=np.hypot(xx,yy)
    tot=route.sum()
    print(r,"excursion steps share by r:",[round(route[(rad>a)&(rad<=b)].sum()/tot,3) for a,b in [(10,15),(15,20),(20,30),(30,60)]])
    print(" mean loss by r ring (tiles):",[ (a,b,round(T["loss"][(T["dist"]>=a)&(T["dist"]<b)].mean(),4),int(((T["dist"]>=a)&(T["dist"]<b)).sum())) for a,b in [(0,10),(10,15),(15,20),(20,30),(30,60)]])
    # within r in 10..30 only: loss vs route density
    from scipy.stats import spearmanr
    m=(T["dist"]>=10)&(T["dist"]<30)
    print(" tiles r10-30: n",m.sum(),"rho(loss,route)",round(spearmanr(T["loss"][m],T["route"][m])[0],3),"rho(loss,dist)",round(spearmanr(T["loss"][m],T["dist"][m])[0],3))

# ---- section 3: refinement tops
import numpy as np
for r in ["RRRRRLLLLLL","RLLLLRRRRLR"]:
    d=f"experiments/archive/2026-10-knockout-maps/knock/{r}/"
    B=float(np.genfromtxt(d+"base.csv",delimiter=",",names=True)["near_home"])
    for nm,w in (("refine5",5),("refine3",3)):
        R=np.genfromtxt(d+nm+".csv",delimiter=",",names=True,dtype=None,encoding=None)
        sw=B-R["near_home"][R["kind"]=="swap"]
        P=R[R["kind"]=="patch"]
        L={}
        for x in P: L.setdefault((int(x["x"]),int(x["y"])),[]).append(B-x["near_home"])
        m={k:np.mean(v) for k,v in L.items()}
        top=sorted(m,key=lambda k:-m[k])[:6]
        print(r,nm,"windows",len(m),"swap p95",round(np.quantile(sw,.95),4) if len(sw) else None,"top:",[(k,round(m[k],3)) for k in top])
        if nm=="refine5":
            # smooth landscape: how many windows exceed 0.05 / p95mean3
            v=np.array(list(m.values())); print("   windows loss>0.05:",(v>0.05).sum(),"max",v.max().round(3),"min",v.min().round(3))
