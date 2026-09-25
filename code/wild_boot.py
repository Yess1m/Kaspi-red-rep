from common import *
def wcr(d, B=99999, seed=20260924):
    """Restricted wild cluster bootstrap-t (WCR), Webb six-point weights, H0: beta=0, two-way FE by demeaning (balanced panel)."""
    Y=d.pivot(index='region',columns='t',values='y').values; D=d.pivot(index='region',columns='t',values='d').values.astype(float)
    assert not np.isnan(Y).any()
    dm=lambda x: x-x.mean(1,keepdims=True)-x.mean(0,keepdims=True)+x.mean()
    yt,dt=dm(Y),dm(D); DD=(dt**2).sum(); C=(dt**2).sum(1)
    b=(dt*yt).sum()/DD; s=(dt*(yt-b*dt)).sum(1); t0=b/np.sqrt((s**2).sum()/DD**2)
    A=(dt*yt).sum(1)  # under H0 the restricted residual is the two-way demeaned y
    rng=np.random.default_rng(seed); webb=np.array([-np.sqrt(1.5),-1,-np.sqrt(.5),np.sqrt(.5),1,np.sqrt(1.5)])
    W=rng.choice(webb,size=(B,len(A))); bs=(W*A).sum(1)/DD; ss=W*A-bs[:,None]*C; ts=bs/np.sqrt((ss**2).sum(1)/DD**2)
    return dict(b=b,t=t0,p=float(np.mean(np.abs(ts)>=abs(t0))),B=B,G=len(A))
if __name__=='__main__':
    specs=[('Lending TWFE to Jul 2018',panel('lending_full.csv',NEW,'2018-07')),
           ('Lending TWFE to Dec 2017',panel('lending_full.csv',NEW,'2017-12')),
           ('Proxy-only TWFE to Jul 2018',panel('lending_full.csv',NEW,'2018-07',drop=('Almaty city','Astana'))),
           ('Spec A TWFE to Jul 2018',panel('lending_specA.csv',dict(NEW,South='2017-05'),'2018-07')),
           ('Balances TWFE to Jul 2018',panel('balances_full.csv',NEW,'2018-07')),
           ('HH all TWFE to 2018Q2',hh_panel('all',NEW,'2018Q2')),
           ('HH ex-Mangistau TWFE to 2018Q2',hh_panel('all',NEW,'2018Q2',drop=('Mangistau',)))]
    out=[]
    for lab,d in specs:
        r=wcr(d); lm=twfe(d); out.append(dict(spec=lab,coef=lm['coef'],param_p=lm['p'],wcr_p=r['p'],B=r['B'],G=r['G'],coef_check=r['b']))
    o=pd.DataFrame(out); o.to_csv('wild_bootstrap.csv',index=False); pd.set_option('display.width',200); print(o.round(4).to_string(index=False))
