from common import *
import json
L='lending_full.csv'; B='balances_full.csv'; SA='lending_specA.csv'
END='2018-07'; C6='2017-12'
rows=[]; SEED=20260924
def add(spec, r, kind, note=''):
    rows.append(dict(spec=spec, kind=kind, coef=r['coef'], se=r['se'], df=r.get('df',np.nan), p=r['p'], lo=r['lo'], hi=r['hi'],
                     mde=r.get('mde',np.nan), N=r['N'], G=r['G'], note=note))
# Gate
r=twfe(panel(L,NEW,C6)); assert abs(r['coef']-0.0056)<5e-5 and abs(r['se']-0.0183)<5e-5, r
add('TWFE, to Dec 2017 (six clean controls) [gate]', r, 'TWFE t(G-1)', 'reproduces locked row')
d=panel(L,NEW,END)
r,es_main,m=cs(d,'notyettreated',seed=SEED); r['mde_t14']=mde_t(r['se'],14)
add('CS not-yet-treated, to Jul 2018 [PRIMARY]', r, 'CS boot', f"MDE on t(14) with boot SE = {r['mde_t14']:.2f}%")
cs_primary=r
r,_,_=cs(d,'notyettreated',bstrap=False); add('CS primary, analytic SE', r, 'CS analytic')
r=twfe(d); add('TWFE, to Jul 2018', r, 'TWFE t(G-1)')
r,es6,_=cs(panel(L,NEW,C6),'nevertreated',seed=SEED); add('CS never-treated-in-window, to Dec 2017', r, 'CS boot')
r,_,_=cs(panel(L,NEW,C6),'notyettreated',seed=SEED); add('CS not-yet-treated, to Dec 2017', r, 'CS boot')
# Date sensitivities
alt=dict(NEW,**{'West Kazakhstan':'2017-10'})
r,_,_=cs(panel(L,alt,END),'notyettreated',seed=SEED); add('CS primary, West Kaz = Oct 2017', r, 'CS boot')
r=twfe(panel(L,alt,C6)); add('TWFE to Dec 2017, West Kaz = Oct 2017', r, 'TWFE t(G-1)')
for dr in ['West Kazakhstan','Kyzylorda']:
    r,_,_=cs(panel(L,NEW,END,drop=(dr,)),'notyettreated',seed=SEED); add(f'CS primary, {dr} dropped', r, 'CS boot')
# leave-one-out over all 15
loo={}
for reg in sorted(NEW):
    r,_,_=cs(panel(L,NEW,END,drop=(reg,)),'notyettreated',bstrap=False); loo[reg]=r['coef']
# Samples
dp=panel(L,NEW,END,drop=('Almaty city','Astana'))
r,_,_=cs(dp,'notyettreated',seed=SEED); add('Proxy-only CS, to Jul 2018', r, 'CS boot')
r=twfe(dp); add('Proxy-only TWFE, to Jul 2018', r, 'TWFE t(G-1)')
A=dict(NEW,South='2017-05'); da=panel(SA,A,END)
r,_,_=cs(da,'notyettreated',seed=SEED); add('Spec A CS (south, single oblast series), to Jul 2018', r, 'CS boot')
r=twfe(da); add('Spec A TWFE, to Jul 2018', r, 'TWFE t(G-1)')
# Region-specific trends (all regions; one normalised by time FE)
dt=d.copy(); tr=[]
for reg in sorted(dt.region.unique())[1:]:
    c='tr_'+reg.replace(' ','_'); dt[c]=(dt.region==reg)*dt.t; tr.append(c)
r=twfe(dt,extra=tr); add('TWFE + region-specific linear trends, to Jul 2018', r, 'TWFE t(G-1)')
# Balances
db=panel(B,NEW,END)
r=twfe(db); add('Balances TWFE, to Jul 2018', r, 'TWFE t(G-1)')
r,_,_=cs(db,'notyettreated',seed=SEED); add('Balances CS, to Jul 2018', r, 'CS boot')
# City-only diagnostics
six=['Akmola','Almaty oblast','Zhambyl','West Kazakhstan','Kyzylorda','North Kazakhstan']
keep=['Almaty city','Astana']+six
dropc=tuple(x for x in NEW if x not in keep)
r=twfe(panel(L,NEW,C6,drop=dropc)); add('City-only TWFE, to Dec 2017 (diagnostic)', r, 'TWFE t(G-1)')
r=twfe(panel(L,NEW,END,drop=dropc)); add('City-only TWFE, to Jul 2018 (diagnostic)', r, 'TWFE t(G-1)')
out=pd.DataFrame(rows); out.to_csv('new_rows_lending.csv',index=False)
es_main.to_csv('cs_event_primary.csv',index=False)
json.dump(loo,open('loo.json','w'),indent=1)
pd.set_option('display.width',250); pd.set_option('display.max_colwidth',60)
print(out.drop(columns='note').round(4).to_string(index=False))
print(out[['spec','note']].to_string(index=False))
print('LOO', {k:round(v,4) for k,v in loo.items()})
print(es_main.round(4).to_string(index=False))
