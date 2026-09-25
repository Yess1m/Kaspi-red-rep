from common import *
def fast_t(Y, D):
    dm=lambda x: x-x.mean(1,keepdims=True)-x.mean(0,keepdims=True)+x.mean()
    yt,dt=dm(Y),dm(D); Dd=(dt**2).sum()
    if Dd==0: return np.nan, np.nan
    b=(dt*yt).sum()/Dd; s=(dt*(yt-b*dt)).sum(1); return b, b/np.sqrt((s**2).sum()/Dd**2)
def ri(d, launch_of, regs, dates, tindex, end_i, n=20000, seed=20260924, quarterly=False):
    W=d.pivot(index='region',columns='t',values='y').loc[regs]; Y=W.values; T=W.columns.values
    def Dmat(assign):
        g=np.array([assign[r] for r in regs]); g=np.where(g<=end_i,g,10**6)
        return (T[None,:]>=g[:,None]).astype(float)
    obs_g={r:launch_of[r] for r in regs}
    b0,t0=fast_t(Y,Dmat(obs_g)); rng=np.random.default_rng(seed); bs=[];ts=[]
    for i in range(n):
        perm=dict(zip(regs, rng.permutation([obs_g[r] for r in regs]))); b,t=fast_t(Y,Dmat(perm)); bs.append(b); ts.append(t)
    bs,ts=np.array(bs),np.array(ts); ok=~np.isnan(ts)
    return dict(b=b0,t=t0,p_t=np.mean(np.abs(ts[ok])>=abs(t0)),p_b=np.mean(np.abs(bs[ok])>=abs(b0)),sd=bs[ok].std(ddof=1),n=int(ok.sum()))
if __name__=='__main__':
    out=[]
    # lending
    for lab,end,launch,drop,path in [('Lending TWFE to Jul 2018','2018-07',NEW,(),'lending_full.csv'),
                                     ('Lending TWFE to Dec 2017','2017-12',NEW,(),'lending_full.csv'),
                                     ('Proxy-only TWFE to Jul 2018','2018-07',NEW,('Almaty city','Astana'),'lending_full.csv')]:
        d=panel(path,launch,end,drop=drop); regs=sorted(d.region.unique()); lo={r:mi(launch[r]) for r in regs}
        chk=twfe(d); r=ri(d,lo,regs,None,None,mi(end))
        out.append(dict(spec=lab,clustered_se=chk['se'],placebo_sd=r['sd'],ratio=r['sd']/chk['se'],param_p=chk['p'],RI_t=r['p_t'],RI_b=r['p_b'],draws=r['n'],fast_b=r['b'],lm_b=chk['coef'],fast_t=r['t'],lm_t=chk['t']))
    for lab,end,drop in [('HH all TWFE to 2018Q2','2018Q2',()),('HH ex-Mangistau TWFE to 2018Q2','2018Q2',('Mangistau',))]:
        d=hh_panel('all',NEW,end,drop=drop); regs=sorted(d.region.unique()); lo={r:qi(q_of_m(NEW[r])) for r in regs}
        chk=twfe(d); r=ri(d,lo,regs,None,None,qi(end))
        out.append(dict(spec=lab,clustered_se=chk['se'],placebo_sd=r['sd'],ratio=r['sd']/chk['se'],param_p=chk['p'],RI_t=r['p_t'],RI_b=r['p_b'],draws=r['n'],fast_b=r['b'],lm_b=chk['coef'],fast_t=r['t'],lm_t=chk['t']))
    o=pd.DataFrame(out); o.to_csv('ri_twfe.csv',index=False); pd.set_option('display.width',250); print(o.round(4).to_string(index=False))
