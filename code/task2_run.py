import sys; import numpy as np, pandas as pd, json, time, warnings
warnings.filterwarnings('ignore')
from scipy import stats
import honestdid as hd
from common import *
key=sys.argv[1]
d=panel('lending_full.csv',NEW,'2018-07'); out,ft,r=event_study(d,lo=-15,hi=14)
pre=['b_-15_-13','b_-12_-10','b_-9_-7','b_-6_-4']; post=['b_0_2','b_3_5','b_6_8','b_9_11','b_12_14']
bT=r.params[pre+post].values; VT=r.cov.loc[pre+post,pre+post].values
C=pd.read_csv('cs_universal_bins.csv'); bC=C.coef.values; VC=np.load('cs_universal_bins_V.npy')
tscale=(stats.t.ppf(.975,14)/stats.norm.ppf(.975))**2
b,V={'TWFE':(bT,VT),'TWFE_t14scaled':(bT,VT*tscale),'CS':(bC,VC)}[key]
L={'theta1':np.array([1,0,0,0,0.]),'theta2':np.ones(5)/5}
lo5,hi5=np.log(0.95),np.log(1.05)
cache={}
def rmci(l,ln,Mb):
    k=(ln,round(Mb,4))
    if k not in cache:
        ci=hd.computeConditionalCS_DeltaRM(b,V,4,5,l_vec=l,Mbar=Mb,alpha=0.05,hybrid_flag='LF',gridPoints=1000,seed=0)
        acc=ci[ci.accept>0]
        cache[k]=(float(acc.grid.min()),float(acc.grid.max()),bool(ci.accept.iloc[0]>0 or ci.accept.iloc[-1]>0)) if len(acc) else (np.nan,np.nan,False)
    return cache[k]
rows=[];bd=[]
for ln,l in L.items():
    oc=hd.constructOriginalCS(b,V,4,5,l_vec=l); rows.append(dict(es=key,target=ln,restriction='original',M=np.nan,lb=oc.lb[0],ub=oc.ub[0],edge=False))
    for Mb in [0,0.25,0.5,0.75,1,1.25,1.5,2]:
        lb,ub,e=rmci(l,ln,Mb); rows.append(dict(es=key,target=ln,restriction='RM',M=Mb,lb=lb,ub=ub,edge=e))
    for M in [0,0.005,0.01,0.02,0.03,0.05]:
        f=hd.find_optimal_flci(b,V,M=M,numPrePeriods=4,numPostPeriods=5,l_vec=l,alpha=0.05)
        lb,ub=(f['FLCI'][0],f['FLCI'][1]) if isinstance(f,dict) and 'FLCI' in f else (np.nan,np.nan)
        rows.append(dict(es=key,target=ln,restriction='SD',M=M,lb=lb,ub=ub,edge=False))
    inc=lambda Mb: (lambda c: c[0]<=lo5 or c[1]>=hi5)(rmci(l,ln,Mb))
    if inc(0): bd.append(dict(es=key,target=ln,breakdown=0.0,note='interval already includes +/-5% at Mbar=0'))
    else:
        grid=[0,0.25,0.5,0.75,1,1.25,1.5,2]; hi_=next((g for g in grid if inc(g)),None)
        if hi_ is None: bd.append(dict(es=key,target=ln,breakdown=np.nan,note='>2'))
        else:
            lo_=max(g for g in grid if g<hi_)
            while hi_-lo_>0.01+1e-9:
                mid=round((lo_+hi_)/2,4)
                if inc(mid): hi_=mid
                else: lo_=mid
            c=rmci(l,ln,hi_); bd.append(dict(es=key,target=ln,breakdown=hi_,note=f'last Mbar not including: {lo_}; CI at breakdown [{c[0]:.4f},{c[1]:.4f}]'))
    print(key,ln,'done',flush=True)
pd.DataFrame(rows).to_csv(f'honest_{key}.csv',index=False); pd.DataFrame(bd).to_csv(f'breakdown_{key}.csv',index=False)
json.dump({f'{k[0]}|{k[1]}':v for k,v in cache.items()},open(f'rmcache_{key}.json','w'),indent=0)
