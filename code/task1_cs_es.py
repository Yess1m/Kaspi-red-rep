import sys; from common import *
import contextlib, io, json
from csdid.att_gt import ATTgt
from csdid.utils.mboot import mboot
SEED=20260924
d=panel('lending_full.csv',NEW,'2018-07')
ids={u:i+1 for i,u in enumerate(sorted(d.region.unique()))}
x=d.assign(_id=d.region.map(ids)).reset_index(drop=True)
np.random.seed(SEED)
with contextlib.redirect_stdout(io.StringIO()):
    m=ATTgt(yname='y',tname='t',idname='_id',gname='g',data=x,control_group='notyettreated',anticipation=0,biters=20000).fit(est_method='reg',base_period='universal',bstrap=True)
    m.aggte(typec='dynamic')
A=m.atte; e=np.array(A['egt']); att=np.array(A['att_egt'],float); se=np.ravel(A['se_egt']).astype(float)
IF=np.asarray(A['inf_function']['dynamic_inf_func_e'],float); n=IF.shape[0]
print('n units',n,'IF shape',IF.shape,'e range',e.min(),e.max())
# group-time table for cohort counts
res=m.results if hasattr(m,'results') else None
print(type(res), (list(res.keys()) if isinstance(res,dict) else None))
pd.DataFrame({'e':e,'att':att,'se_boot':se,'se_an':np.sqrt((IF**2).sum(0))/n}).to_csv('cs_universal_monthly.csv',index=False)
np.save('cs_universal_IF.npy',IF); json.dump({'e':e.tolist()},open('cs_universal_e.json','w'))
print(pd.read_csv('cs_universal_monthly.csv').round(4).to_string())
