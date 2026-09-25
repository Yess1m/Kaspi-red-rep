import sys; import pandas as pd, numpy as np, matplotlib; matplotlib.use('Agg'); import matplotlib.pyplot as plt, matplotlib.dates as mdates
from common import NEW
ink,muted,grid='#1f2933','#6b7785','#e3e7eb'
# Figure 1: rollout timeline
order=sorted(NEW,key=lambda k:(NEW[k],k))
fig,ax=plt.subplots(figsize=(6.6,3.9),dpi=200)
ys=list(range(len(order)))[::-1]
for y,reg in zip(ys,order):
    d=pd.to_datetime(NEW[reg]+'-01'); ax.plot([pd.to_datetime('2016-06-01'),d],[y,y],color=grid,lw=1,zorder=0)
    ax.plot(d,y,'o',ms=5.5,color=ink if NEW[reg]<='2018-07' else muted,zorder=3)
    ax.text(d+pd.Timedelta(days=12),y,pd.to_datetime(NEW[reg]+'-01').strftime('%b %Y'),va='center',fontsize=6.8,color=muted)
ax.set_yticks(ys); ax.set_yticklabels(order,fontsize=7.5,color=ink)
for x,t in [('2017-12-31','End of December 2017 window'),('2018-07-31','End of lending window')]:
    ax.axvline(pd.to_datetime(x),color=muted,lw=0.8,ls=(0,(3,2))); ax.text(pd.to_datetime(x)-pd.Timedelta(days=8),len(order)-0.4,t,fontsize=6.5,color=muted,ha='right',va='bottom')
ax.set_xlim(pd.to_datetime('2016-06-01'),pd.to_datetime('2019-02-01')); ax.set_ylim(-0.8,len(order)+0.2)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y')); ax.xaxis.set_major_locator(mdates.YearLocator())
ax.tick_params(axis='x',colors=ink,labelsize=7.5); [ax.spines[s].set_visible(False) for s in ['top','right','left']]; ax.spines['bottom'].set_color(muted); ax.tick_params(axis='y',length=0)
ax.set_xlabel('Coded launch month',fontsize=8,color=ink)
plt.tight_layout(); plt.savefig('fig_rollout.png'); plt.close()
# Figure 2: raw mean log issuance, early vs late cohorts, relative to own 2015 mean
L=pd.read_csv('lending_full.csv'); L=L[(L.month>='2015-01')&(L.month<='2018-07')].copy()
L['dev']=L.y-L.groupby('region').y.transform(lambda s: s[L.loc[s.index,'month'].str.startswith('2015')].mean())
early=[k for k,v in NEW.items() if v<='2017-10']; late=[k for k,v in NEW.items() if v>'2017-10']
G=L.assign(grp=np.where(L.region.isin(early),'early','late')).groupby(['month','grp']).dev.mean().unstack()
G.to_csv('raw_group_means.csv')
x=pd.to_datetime(G.index+'-01')
fig,ax=plt.subplots(figsize=(6.6,3.3),dpi=200)
ax.plot(x,G.early,color=ink,lw=1.6,label='9 regions launched Aug 2016 to Oct 2017'); ax.plot(x,G.late,color=muted,lw=1.6,ls=(0,(4,2)),label='6 regions launched Feb to Aug 2018')
ax.legend(loc='upper left',fontsize=7,frameon=False)
ax.axvspan(pd.to_datetime('2016-08-01'),pd.to_datetime('2017-10-31'),color='#f1f3f5',zorder=0); ax.text(pd.to_datetime('2016-08-15'),-0.45,'first nine launches',fontsize=6.5,color=muted,va='bottom')
ax.axvline(pd.to_datetime('2015-08-20'),color=muted,lw=0.8); ax.text(pd.to_datetime('2015-09-01'),ax.get_ylim()[0]+0.03,'tenge float',fontsize=6.5,color=muted)
ax.axhline(0,color=grid,lw=0.8,zorder=0)
ax.set_ylabel('Log issuance relative to\nregion’s 2015 mean',fontsize=8,color=ink)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y')); ax.xaxis.set_major_locator(mdates.YearLocator())
ax.tick_params(colors=ink,labelsize=7.5); [ax.spines[s].set_visible(False) for s in ['top','right']]; [ax.spines[s].set_color(muted) for s in ['left','bottom']]
ax.set_xlim(pd.to_datetime('2014-12-01'),pd.to_datetime('2018-09-01'))
plt.tight_layout(); plt.savefig('fig_raw.png'); plt.close()
print(G.round(3).iloc[[0,7,11,19,23,33,42]])
