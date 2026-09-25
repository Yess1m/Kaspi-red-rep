import sys; import pandas as pd, numpy as np
from common import NEW
from fmt import r
L=pd.read_csv('lending_full.csv'); L=L[(L.month>='2015-01')&(L.month<='2018-07')].copy()
L['launch']=L.region.map(NEW)
mon=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
lab=lambda m: f"{mon[int(m[5:])-1]} {m[:4]}"
y15=L[L.month.str.startswith('2015')]; tot15=y15['level'].sum()
a=L[(L.month>='2015-01')&(L.month<='2015-07')].groupby('region')['level'].sum(); b=L[(L.month>='2016-01')&(L.month<='2016-07')].groupby('region')['level'].sum()
g=np.log(b/a)
rows=[]
for m,regs in sorted(pd.Series(NEW).groupby(pd.Series(NEW)).groups.items()):
    regs=sorted(regs); lv=y15[y15.region.isin(regs)]
    rows.append(dict(cohort=lab(m),regions=', '.join(regs),n=len(regs),mean_monthly_bn=lv['level'].sum()/12/len(regs)/1e6,share_2015=lv['level'].sum()/tot15,growth=g[regs].mean()))
D=pd.DataFrame(rows); D.to_csv('desc_cohorts.csv',index=False)
pd.set_option('display.width',200); print(D.round(4).to_string())
print('15-region 2015 monthly mean (bn)',tot15/12/1e6, 'unweighted mean growth', g.mean(), 'early vs late growth', g[[k for k,v in NEW.items() if v<='2017-10']].mean(), g[[k for k,v in NEW.items() if v>'2017-10']].mean())
