from common import *
from ri_twfe import ri
from wild_boot import wcr
rows=[]; SEED=20260924; E='2018Q2'
def add(spec,r,kind,conv):
    z = kind.startswith('CS')
    rows.append(dict(panel='household',spec=spec,convention=conv,kind=kind,coef=r['coef'],se=r['se'],df=np.nan if z else r['df'],p=r['p'],lo=r['lo'],hi=r['hi'],
                     mde=mde_z(r['se']) if z else mde_t(r['se'],r['df']),N=r['N'],G=r['G'],treated_obs=None))
    return rows[-1]
FF=dict(first_full=True)
d=hh_panel('all',NEW,E,**FF); r,es,_=cs(d,'notyettreated',seed=SEED); x=add('HH all: CS not-yet-treated, to 2018Q2 [PRIMARY HH]',r,'CS boot','first full'); x['treated_obs']=int(d.d.sum())
es.to_csv('cs_event_hh_firstfull.csv',index=False)
r=twfe(d); x=add('HH all: TWFE, to 2018Q2',r,'TWFE t(G-1)','first full'); x['treated_obs']=r['treated_obs']
dq=hh_panel('all',NEW,E); r,_,_=cs(dq,'notyettreated',seed=SEED); x=add('HH all: CS, quarter containing launch (timing robustness)',r,'CS boot','quarter containing'); x['treated_obs']=int(dq.d.sum())
r=twfe(dq); x=add('HH all: TWFE, quarter containing launch (timing robustness)',r,'TWFE t(G-1)','quarter containing'); x['treated_obs']=r['treated_obs']
dt=d.copy(); tr=[]
for reg in sorted(dt.region.unique())[1:]:
    c='tr_'+reg.replace(' ','_'); dt[c]=(dt.region==reg)*dt.t; tr.append(c)
r=twfe(dt,extra=tr); x=add('HH all: TWFE + region-specific trends, to 2018Q2',r,'TWFE t(G-1)','first full'); x['treated_obs']=r['treated_obs']
dm=hh_panel('all',NEW,E,drop=('Mangistau',),**FF)
r,_,_=cs(dm,'notyettreated',seed=SEED); x=add('HH ex-Mangistau: CS, to 2018Q2',r,'CS boot','first full'); x['treated_obs']=int(dm.d.sum())
r=twfe(dm); x=add('HH ex-Mangistau: TWFE, to 2018Q2',r,'TWFE t(G-1)','first full'); x['treated_obs']=r['treated_obs']
r=twfe(hh_panel('urban',NEW,E,**FF)); x=add('HH urban incl. Mangistau (1 missing cell): TWFE, to 2018Q2',r,'TWFE t(G-1)','first full'); x['treated_obs']=r['treated_obs']
du=hh_panel('urban',NEW,E,drop=('Mangistau',),**FF)
r,_,_=cs(du,'notyettreated',seed=SEED); x=add('HH urban ex-Mangistau: CS, to 2018Q2',r,'CS boot','first full'); x['treated_obs']=int(du.d.sum())
r=twfe(du); x=add('HH urban ex-Mangistau: TWFE, to 2018Q2',r,'TWFE t(G-1)','first full'); x['treated_obs']=r['treated_obs']
d7=hh_panel('all',NEW,'2017Q4',**FF)
r=twfe(d7); x=add('HH all: TWFE, to 2017Q4 (companion)',r,'TWFE t(G-1)','first full'); x['treated_obs']=r['treated_obs']
r,_,_=cs(d7,'nevertreated',seed=SEED); x=add('HH all: CS never-treated-in-window, to 2017Q4 (companion)',r,'CS boot','first full'); x['treated_obs']=int(d7.d.sum())
out=pd.DataFrame(rows); out.to_csv('v5_rows_hh.csv',index=False)
pd.set_option('display.width',260); print(out.round(4).to_string(index=False))
print('companion 2017Q4 untreated regions:',sorted(d7[d7.g==0].region.unique()))
# Diagnostics on first-full TWFE rows
diag=[]
for lab,dd in [('HH all TWFE to 2018Q2',d),('HH ex-Mangistau TWFE to 2018Q2',dm)]:
    regs=sorted(dd.region.unique()); lo={r_:qi(q_of_m(NEW[r_]))+1 for r_ in regs}
    chk=twfe(dd); rr=ri(dd,lo,regs,None,None,qi(E)); wb=wcr(dd)
    diag.append(dict(spec=lab,clustered_se=chk['se'],placebo_sd=rr['sd'],ratio=rr['sd']/chk['se'],param_p=chk['p'],RI_t=rr['p_t'],draws=rr['n'],wcr_p=wb['p'],B=wb['B']))
dg=pd.DataFrame(diag); dg.to_csv('v5_hh_diagnostics.csv',index=False); print(dg.round(4).to_string(index=False))
