import sys; from common import *
import contextlib, io
from csdid.att_gt import ATTgt
SEED=20260924
d=panel('lending_full.csv',NEW,'2018-07')
ids={u:i+1 for i,u in enumerate(sorted(d.region.unique()))}
x=d.assign(_id=d.region.map(ids)).reset_index(drop=True)
np.random.seed(SEED)
with contextlib.redirect_stdout(io.StringIO()):
    m=ATTgt(yname='y',tname='t',idname='_id',gname='g',data=x,control_group='notyettreated',anticipation=0,biters=20000).fit(est_method='reg',base_period='universal',bstrap=False)
    m.aggte(typec='dynamic')
R=pd.DataFrame(m.results)[['group','year','att']]; R['e']=R.year-R.group
size=d[d.g>0].groupby('g').region.nunique(); regs=d[d.g>0].groupby('g').region.apply(lambda s: ', '.join(sorted(s.unique())))
def ym(t): y=2015+(t-1)//12; mth=(t-1)%12+1; return f'{["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"][mth-1]} {y}'
rows=[]
E=np.array(m.atte['egt']); A=np.array(m.atte['att_egt'],float)
for g in sorted(size.index):
    s=R[R.group==g].set_index('e').att
    early=s.reindex([-12,-11,-10]); late=s.reindex([-9,-8,-7])
    if early.isna().any() or late.isna().any(): rows.append(dict(cohort=ym(g),regions=regs[g],n=size[g],months_early='',months_late='',step=np.nan)); continue
    rows.append(dict(cohort=ym(g),regions=regs[g],n=int(size[g]),months_early=f'{ym(g-12)} to {ym(g-10)}',months_late=f'{ym(g-9)} to {ym(g-7)}',step=late.mean()-early.mean()))
T=pd.DataFrame(rows); v=T.dropna(subset=['step'])
# dynamic weights: cohort size share among cohorts present at each e; check constant across the six e
w=v.n/v.n.sum(); T.loc[v.index,'weight']=w; T.loc[v.index,'contribution']=w*v.step
cs_bins=pd.read_csv('cs_universal_bins.csv').set_index('bin').coef
target=cs_bins['-9 to -7']-cs_bins['-12 to -10']
agg=A[np.isin(E,[-9,-8,-7])].mean()-A[np.isin(E,[-12,-11,-10])].mean()
print('sum of contributions',T.contribution.sum(),'CS binned step',target,'from aggregated ATT(e)',agg)
T['share_of_step']=T.contribution/T.contribution.sum()
T.to_csv('step_decomposition.csv',index=False)
pd.set_option('display.width',250); pd.set_option('display.max_colwidth',60); print(T.round(4).to_string())
# which cohorts' early/late windows straddle Aug 2015 (t=8) to Jan 2016 (t=13)?
for g in sorted(size.index): print(ym(g), 'window', ym(g-12),'-',ym(g-7))
