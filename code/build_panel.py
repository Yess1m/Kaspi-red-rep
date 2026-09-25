import xlrd, glob, re, numpy as np, pandas as pd
SRC='../raw/'
MON=['Январь','Февраль','Март','Апрель','Май','Июнь','Июль','Август','Сентябрь','Октябрь','Ноябрь','Декабрь']
MAP={'Акмолинская':'Akmola','Актюбинская':'Aktobe','Алматинская':'Almaty oblast','Атырауская':'Atyrau',
 'Восточно-Казахстанская':'East Kazakhstan','Жамбылская':'Zhambyl','Западно-Казахстанская':'West Kazakhstan',
 'Карагандинская':'Karaganda','Костанайская':'Kostanay','Кызылординская':'Kyzylorda','Мангистауская':'Mangistau',
 'Павлодарская':'Pavlodar','Северо-Казахстанская':'North Kazakhstan','г. Алматы':'Almaty city','г. Астана':'Astana','г. Нур-Султан':'Astana'}
def build(prefix):
    rows=[]
    for f in sorted(glob.glob(SRC+prefix+'*.xls')):
        yr=int(re.search(r'(20\d\d)',f.split('/')[-1]).group(1))
        b=xlrd.open_workbook(f)
        for mi,mn in enumerate(MON):
            s=b.sheet_by_name(mn)
            unit=' '.join(str(s.cell_value(r,c)) for r in range(6) for c in range(s.ncols))
            scale=1000.0 if 'млн' in unit else 1.0
            for r in range(s.nrows):
                lab=str(s.cell_value(r,0)).strip().rstrip(':').strip()
                lab=re.sub(r'\s+',' ',lab)
                key=next((k for k in MAP if lab.startswith(k)),None)
                if key:
                    v=s.cell_value(r,1)
                    rows.append(dict(region=MAP[key],month=f'{yr}-{mi+1:02d}',level=float(v)*scale,raw=lab))
    df=pd.DataFrame(rows)
    return df
if __name__=='__main__':
    for p,o in [('потребрегионывыдача','lending_full.csv'),('остаткипотребрегионы','balances_full.csv')]:
        d=build(p); print(p,d.shape, d.groupby('region').size().to_dict()); print(d.raw.unique())
        assert (d.level>0).all()
        d['y']=np.log(d.level); d[['region','month','y','level']].to_csv(o,index=False)
    # Spec A sample: fifteen regions plus South Kazakhstan (single oblast series through July 2018;
    # Turkestan oblast and Shymkent city summed from August 2018, outside the estimation window)
    MAP.update({'Южно-Казахстанская':'South','Туркестанская':'South','г. Шымкент':'South'})
    d=build('потребрегионывыдача').groupby(['region','month'],as_index=False)['level'].sum()
    assert (d.level>0).all()
    d['y']=np.log(d.level); d[['region','month','level','y']].to_csv('lending_specA.csv',index=False)
