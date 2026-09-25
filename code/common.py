import numpy as np, pandas as pd, warnings
from scipy import stats
from scipy.optimize import brentq
warnings.filterwarnings('ignore')
OLD={'Almaty city':'2016-08','Astana':'2017-02','Karaganda':'2017-06','East Kazakhstan':'2017-06','Kostanay':'2017-07',
     'Aktobe':'2017-08','Atyrau':'2017-09','Pavlodar':'2017-10','Mangistau':'2017-10'}
NEW=dict(OLD, **{'West Kazakhstan':'2018-02','Kyzylorda':'2018-04','Zhambyl':'2018-05','North Kazakhstan':'2018-07',
     'Akmola':'2018-07','Almaty oblast':'2018-08'})
def mi(s): y,m=map(int,s.split('-')); return (y-2015)*12+m
def mde_t(se,df,alpha=.05,power=.8):
    c=stats.t.ppf(1-alpha/2,df); f=lambda d: stats.nct.sf(c,df,d)+stats.nct.cdf(-c,df,d)-power
    return 100*(np.exp(brentq(f,.5,8)*se)-1)
def mde_z(se): return 100*(np.exp((stats.norm.ppf(.975)+stats.norm.ppf(.8))*se)-1)
def panel(path, launch, end, start='2015-01', drop=()):
    d=pd.read_csv(path,dtype={'month':str})
    d=d[(d.month>=start)&(d.month<=end)&(~d.region.isin(drop))].copy()
    d['t']=d.month.map(mi); e=mi(end)
    g={r:mi(launch[r]) if r in launch and mi(launch[r])<=e else 0 for r in d.region.unique()}
    d['g']=d.region.map(g); d['d']=((d.g>0)&(d.t>=d.g)).astype(int); return d
def twfe(d, extra=None):
    from linearmodels.panel import PanelOLS
    p=d.set_index(['region','t']); X=p[['d']] if extra is None else p[['d']+extra]
    r=PanelOLS(p['y'],X,entity_effects=True,time_effects=True).fit(cov_type='clustered',cluster_entity=True)
    b,se=float(r.params['d']),float(r.std_errors['d']); G=d.region.nunique(); df=G-1
    t=b/se; c=stats.t.ppf(.975,df)
    return dict(coef=b,se=se,t=t,df=df,p=2*stats.t.sf(abs(t),df),lo=b-c*se,hi=b+c*se,mde=mde_t(se,df),
                N=len(d),G=G,Gt=int((d.groupby('region').d.max()>0).sum()),treated_obs=int(d.d.sum()))
def cs(d, control='notyettreated', est='reg', anticipation=0, bstrap=True, seed=None, biters=20000):
    import contextlib, io
    from csdid.att_gt import ATTgt
    ids={u:i+1 for i,u in enumerate(sorted(d.region.unique()))}
    x=d.assign(_id=d.region.map(ids)).reset_index(drop=True)
    if seed is not None: np.random.seed(seed)
    with contextlib.redirect_stdout(io.StringIO()):
        m=ATTgt(yname='y',tname='t',idname='_id',gname='g',data=x,control_group=control,anticipation=anticipation,biters=biters).fit(est_method=est,bstrap=bstrap)
        m.aggte(typec='simple'); s=dict(m.atte)
        m.aggte(typec='dynamic'); dy=dict(m.atte)
    b=float(s['overall_att']); se=float(np.ravel(s['overall_se'])[0])
    es=pd.DataFrame({'e':dy['egt'],'att':dy['att_egt'],'se':np.ravel(dy['se_egt'])})
    return dict(coef=b,se=se,lo=b-1.96*se,hi=b+1.96*se,z=b/se,p=2*stats.norm.sf(abs(b/se)),mde=mde_z(se),N=len(d),G=d.region.nunique()),es,m
def event_study(d, lo=-15, hi=26, width=3, ref=(-3,-1)):
    from linearmodels.panel import PanelOLS
    d=d.copy(); e=np.where(d.g>0, d.t-d.g, np.nan); d['e']=e
    bins=[]; 
    b0=lo
    while b0<=hi:
        bins.append((b0,b0+width-1)); b0+=width
    cols=[]
    d['lowEP']=((d.g>0)&(d.e<lo)).astype(int); cols.append('lowEP')
    for a,b in bins:
        if (a,b)==ref: continue
        c=f'b_{a}_{b}'; d[c]=((d.g>0)&(d.e>=a)&(d.e<=b)).astype(int)
        if d[c].sum()>0: cols.append(c)
    d['highEP']=((d.g>0)&(d.e>hi)).astype(int)
    if d.highEP.sum()>0: cols.append('highEP')
    p=d.set_index(['region','t'])
    r=PanelOLS(p['y'],p[cols],entity_effects=True,time_effects=True,drop_absorbed=True).fit(cov_type='clustered',cluster_entity=True)
    G=d.region.nunique(); df=G-1; cv=stats.t.ppf(.975,df)
    out=pd.DataFrame({'coef':r.params,'se':r.std_errors}); out['t']=out.coef/out.se
    out['p']=2*stats.t.sf(out.t.abs(),df); out['lo']=out.coef-cv*out.se; out['hi']=out.coef+cv*out.se
    out['obs']=[int(d[c].sum()) for c in out.index]; out['units']=[int(d[d[c]==1].region.nunique()) for c in out.index]
    def ftest(names):
        b=r.params[names].values; V=r.cov.loc[names,names].values; q=len(names)
        F=float(b@np.linalg.solve(V,b))/q; return F, q, df, float(stats.f.sf(F,q,df))
    return out, ftest, r
def qi(s): return (int(s[:4])-2015)*4+int(s[-1])
def q_of_m(s): y,m=map(int,s.split('-')); return f'{y}Q{(m-1)//3+1}'
def hh_panel(series, launch, end='2019Q4', drop=(), first_full=False):
    d=pd.read_csv('hh_repayment_panel.csv')
    d=d[d.series==series].copy(); d['value']=pd.to_numeric(d.value,errors='coerce'); d=d.dropna(subset=['value'])
    d=d[(d.quarter.map(qi)<=qi(end))&(~d.region.isin(drop))].copy()
    d['t']=d.quarter.map(qi); d['y']=np.log(d.value); e=qi(end)
    def gq(m):
        q=qi(q_of_m(m))
        if first_full:
            y,mm=map(int,m.split('-'))
            q+=1   # no launch falls on day 1 of a quarter, so first full quarter is always the next one
        return q
    g={r:(gq(launch[r]) if r in launch and gq(launch[r])<=e else 0) for r in d.region.unique()}
    d['g']=d.region.map(g); d['d']=((d.g>0)&(d.t>=d.g)).astype(int); return d
