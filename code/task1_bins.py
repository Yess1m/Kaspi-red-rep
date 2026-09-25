import sys; from common import *
import contextlib, io, json
from csdid.att_gt import ATTgt
from csdid.utils.mboot import mboot
from scipy import stats
SEED=20260924
d=panel('lending_full.csv',NEW,'2018-07')
ids={u:i+1 for i,u in enumerate(sorted(d.region.unique()))}
x=d.assign(_id=d.region.map(ids)).reset_index(drop=True)
np.random.seed(SEED)
with contextlib.redirect_stdout(io.StringIO()):
    m=ATTgt(yname='y',tname='t',idname='_id',gname='g',data=x,control_group='notyettreated',anticipation=0,biters=20000).fit(est_method='reg',base_period='universal',bstrap=True)
    m.aggte(typec='dynamic')
A=m.atte; e=np.array(A['egt']); att=np.array(A['att_egt'],float)
IF=np.asarray(A['inf_function']['dynamic_inf_func_e'],float); n=IF.shape[0]
bins=[(-15,-13),(-12,-10),(-9,-7),(-6,-4),(0,2),(3,5),(6,8),(9,11),(12,14)]; ref=(-3,-1)
def col(a,b): return np.isin(e,np.arange(a,b+1))
wref=col(*ref)/col(*ref).sum()
rows=[];IFB=[]
R=pd.DataFrame(m.results); R['e']=R['year']-R['group']
gsize=d.groupby('g').region.nunique().to_dict()
for a,b in bins:
    w=col(a,b)/col(a,b).sum()-wref
    th=float(w@att); ifb=IF@w; IFB.append(ifb)
    sub=R[(R.e>=a)&(R.e<=b)&R.att.notna()]; cg=sorted(sub.group.unique())
    rows.append(dict(bin=f'{a} to {b}',coef=th,se_an=np.sqrt((ifb**2).sum())/n,cohorts=len(cg),regions=int(sum(gsize[g] for g in cg)),months_in_bin=int(col(a,b).sum())))
IFB=np.column_stack(IFB)
dp=m.dp if hasattr(m,'dp') else None
np.random.seed(SEED)
with contextlib.redirect_stdout(io.StringIO()):
    bo=mboot(IFB,dp)
seb=np.ravel(bo['se']).astype(float)
out=pd.DataFrame(rows); out['se_boot']=seb
out['z']=out.coef/out.se_boot; out['p']=2*stats.norm.sf(out.z.abs()); out['lo']=out.coef-1.96*out.se_boot; out['hi']=out.coef+1.96*out.se_boot
out.to_csv('cs_universal_bins.csv',index=False)
V=IFB.T@IFB/n**2; np.save('cs_universal_bins_V.npy',V)
pre=out.iloc[:4]; Vp=V[:4,:4]; b=pre.coef.values
W=float(b@np.linalg.solve(Vp,b)); print('Wald chi2(4) analytic',W,'p',stats.chi2.sf(W,4))
# bootstrap-based covariance for Wald: use analytic V scaled? report analytic only
pd.set_option('display.width',200); print(out.round(4).to_string())
print('ref cohorts', sorted(R[(R.e>=-3)&(R.e<=-1)&R.att.notna()].group.unique()))
