from common import *
d=panel('lending_full.csv',NEW,'2018-07')
out,ft,r=event_study(d,lo=-15,hi=14)
out.to_csv('es_twfe_window.csv')
pd.set_option('display.width',200); print(out.round(4).to_string())
pre=[c for c in out.index if c.startswith('b_-')]
print('pre bins',pre, ft(pre)); print('pre+lowEP', ft(pre+['lowEP']))
# window facts
tr=d[d.d==1]; print('treated obs',len(tr),'treated regions',tr.region.nunique())
e=tr.t-tr.g; print('mean e',e.mean(),'median',e.median())
print(tr.assign(e=e).groupby('region').e.max().sort_values(ascending=False).to_dict())
for m in range(1,20):
    ym=f'2017-{m:02d}' if m<=12 else f'2018-{m-12:02d}'
for ym in ['2017-12','2018-01','2018-02','2018-03','2018-04','2018-05','2018-06','2018-07']:
    t=mi(ym); print(ym,'not yet treated',sum(1 for r_,v in NEW.items() if mi(v)>t))
import json
json.dump({'F4':ft(pre),'F5':ft(pre+['lowEP']),'treated_obs':int(len(tr)),'mean_e':float(e.mean()),'median_e':float(e.median())},open('es_ftests.json','w'))
