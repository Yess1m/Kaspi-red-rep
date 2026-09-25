from decimal import Decimal, ROUND_HALF_UP
import math
def r(x, nd):
    q=Decimal(1).scaleb(-nd); return Decimal(repr(float(x))).quantize(q, rounding=ROUND_HALF_UP)
def c(x, nd=4, sign=True):
    v=r(x,nd); s=f'{v:.{nd}f}'
    if v==0: s=f'{abs(v):.{nd}f}'
    if sign and v>0: s='+'+s
    return s
def p(x, nd=3): return f'{r(x,nd):.{nd}f}'
def ci(lo,hi): return f'[{c(lo)}, {c(hi)}]'
def lv(x): return 100*(math.exp(x)-1)
def pct(x, nd=1): return f'{r(x,nd):.{nd}f}%'
