from common import *
du=hh_panel('urban',NEW,'2018Q2',drop=('Mangistau',),first_full=True)
out=[]
for s in [20260924,1,2,3,4,5,6,7,8,9]:
    r,_,_=cs(du,'notyettreated',seed=s); out.append((s,r['se'],r['p']))
ra,_,_=cs(du,'notyettreated',bstrap=False)
print(out); print('analytic',ra['coef'],ra['se'],ra['p'])
