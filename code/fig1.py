import pandas as pd, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
e=pd.read_csv('es_twfe_window.csv',index_col=0)
order=['lowEP','b_-15_-13','b_-12_-10','b_-9_-7','b_-6_-4','REF','b_0_2','b_3_5','b_6_8','b_9_11','b_12_14','highEP']
labels=['≤ −16\n(endpoint)','−15\nto −13','−12\nto −10','−9\nto −7','−6\nto −4','−3 to −1\n(ref.)','0\nto +2','+3\nto +5','+6\nto +8','+9\nto +11','+12\nto +14','≥ +15\n(endpoint)']
ink='#1f2933'; muted='#6b7785'
fig,ax=plt.subplots(figsize=(7.2,3.9),dpi=200)
ax.axhline(0,color=muted,lw=0.8)
ax.axvline(5.5,color=muted,lw=1,ls=(0,(4,3)))
for i,k in enumerate(order):
    if k=='REF':
        ax.plot(i,0,'o',ms=6,mfc='white',mec=ink,mew=1.2,zorder=3); continue
    r=e.loc[k]; ep=k in ('lowEP','highEP')
    ax.plot([i,i],[r.lo,r.hi],color=muted if ep else ink,lw=1.4,solid_capstyle='round')
    ax.plot(i,r.coef,'s' if ep else 'o',ms=6 if ep else 5.5,color=muted if ep else ink,mec='white',mew=1,zorder=3)
    ax.text(i,r.hi+0.008,str(int(r.units)),ha='center',va='bottom',fontsize=6.8,color=muted)
ax.set_xticks(range(len(order))); ax.set_xticklabels(labels,fontsize=7.2)
ax.set_xlabel('Months relative to launch month (three-month bins)',fontsize=8.5,color=ink)
ax.set_ylabel('Log issuance, relative to months −3 to −1',fontsize=8.5,color=ink)
ax.tick_params(axis='y',labelsize=8,colors=ink); ax.tick_params(axis='x',colors=ink,length=0)
for s in ['top','right']: ax.spines[s].set_visible(False)
for s in ['left','bottom']: ax.spines[s].set_color(muted); ax.spines[s].set_linewidth(0.8)
ax.grid(axis='y',color='#e3e7eb',lw=0.6); ax.set_axisbelow(True)
ax.text(5.6,0.205,'Launch',fontsize=7.5,color=muted,va='top')
ax.set_ylim(-0.2,0.215)
plt.tight_layout(); plt.savefig('fig1_event_study_v6.png',dpi=200)
