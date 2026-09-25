import sys
from common import *
from multiprocessing import Pool
L='lending_full.csv'; END='2018-07'
regs=sorted(NEW); dates=[NEW[r] for r in regs]
def one(seed):
    rng=np.random.default_rng(seed); perm=dict(zip(regs, rng.permutation(dates)))
    r,_,_=cs(panel(L,perm,END),'notyettreated',bstrap=False); return r['coef'], r['z']
if __name__=='__main__':
    n=int(sys.argv[1]); base=20260924
    obs,_,_=cs(panel(L,NEW,END),'notyettreated',bstrap=False)
    with Pool(2) as p: res=p.map(one,[base+i for i in range(1,n+1)])
    res=np.array(res); np.save('ri_cs.npy',res)
    pc=np.mean(np.abs(res[:,0])>=abs(obs['coef'])); pz=np.mean(np.abs(res[:,1])>=abs(obs['z']))
    print('obs',obs['coef'],obs['z'],'RI p (coef)',pc,'RI p (z)',pz,'n',n,'placebo SD',res[:,0].std(ddof=1),'analytic SE',obs['se'])
