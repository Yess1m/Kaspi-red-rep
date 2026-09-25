import sys; import pandas as pd, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt
from common import NEW
A=pd.read_csv('lending_specA.csv'); A=A[(A.month>='2015-01')&(A.month<='2018-07')]
tot=A.groupby('month')['level'].sum(); alm=A[A.region=='Almaty city'].set_index('month')['level']
S=pd.DataFrame({'almaty_thousand_tenge':alm,'national_16_units_thousand_tenge':tot}); S['almaty_share']=S.almaty_thousand_tenge/S.national_16_units_thousand_tenge
S.index.name='month'; S.to_csv('almaty_share_monthly.csv')
q=S.copy(); q.index=pd.PeriodIndex(q.index,freq='M'); Q=q.groupby(q.index.asfreq('Q')).almaty_share.agg(['mean','min','max','count'])
Q.to_csv('almaty_share_quarterly.csv'); print(Q.round(4).to_string())
ink,muted,grid='#1f2933','#6b7785','#e3e7eb'
fig,ax=plt.subplots(figsize=(7.2,3.4),dpi=200)
x=pd.to_datetime(S.index); ax.plot(x,S.almaty_share*100,color=ink,lw=1.6)
ax.set_ylabel('Almaty city share of national\nconsumer issuance (%)',color=ink,fontsize=8.5)
launch={}
for r,m in NEW.items():
    if m<='2018-07' and r!='Almaty city': launch.setdefault(m,[]).append(r)
for m,rs in launch.items():
    ax.axvline(pd.to_datetime(m+'-01'),color=muted,lw=0.7,ls=(0,(2,2)),zorder=0)
ax.axvline(pd.to_datetime('2016-08-01'),color=ink,lw=0.9,ls='--',zorder=0); ax.text(pd.to_datetime('2016-08-15'),S.almaty_share.max()*100+0.3,'Almaty launch',fontsize=7,color=ink)
ax.text(pd.to_datetime('2017-02-10'),53.5,'dotted lines: other regions’ launch months',fontsize=7,color=muted,va='top')
ax.axvline(pd.to_datetime('2015-08-20'),color=muted,lw=0.7,zorder=0); ax.text(pd.to_datetime('2015-09-01'),S.almaty_share.max()*100+0.3,'tenge float',fontsize=7,color=muted)
ax.grid(axis='y',color=grid,lw=0.6); [ax.spines[s].set_visible(False) for s in ['top','right']]
for s in ['left','bottom']: ax.spines[s].set_color(muted)
ax.tick_params(colors=ink,labelsize=7.5); ax.set_ylim(S.almaty_share.min()*100-1.2,S.almaty_share.max()*100+1.2)
ax.set_title('Descriptive: Almaty city share of national consumer loan issuance, Jan 2015 to Jul 2018',fontsize=8.5,color=ink,loc='left')
plt.tight_layout(); plt.savefig('fig_almaty_share.png'); print('saved')
