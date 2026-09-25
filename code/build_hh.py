import xlrd, os, csv, re
RAW='../raw/'
Q={'2015Q1':('01кв_2015_Б_25_10_К/1.1_01_15_Б_25_10_К.xls','01кв_2015_Б_25_10_К/1.2_01_15_Б_25_10_К.xls'),
 '2015Q2':('02_2015_Б-11-10К/01_02_15_Б_11_10_К.xls','02_2015_Б-11-10К/02_02_15_Б_11_10_К.xls'),
 '2015Q3':('03_15_Б_25_10_К/01_03_15_Б_25_10_К.xls','03_15_Б_25_10_К/02_03_15_Б_25_10_К.xls'),
 '2015Q4':('04_15_Б_27_08_К/01_04_15_Б_27_08_К.xls','04_15_Б_27_08_К/02_04_15_Б_27_08_К.xls'),
 '2016Q1':('01_2016_Б_27_08_К/1.1_01_2016_Б_27_04_К.xls','01_2016_Б_27_08_К/1.2_01_2016_Б_27_04_К.xls'),
 '2016Q2':('02_2016_Б_27_08_К/1.1_02_2016_Б_27_08_К.xls','02_2016_Б_27_08_К/1.2_02_2016_Б_27_08_К.xls'),
 '2016Q3':('03_2016_Б_27_08_К/1.1_03_2016_Б_27_08_К.xls','03_2016_Б_27_08_К/1.2_03_2016_Б_27_08_К.xls'),
 '2016Q4':('04_2016_Б_25_09_К/1.1_04_2016_Б_25_09_К.xls','04_2016_Б_25_09_К/1.2_04_2016_Б_25_09_К.xls'),
 '2017Q1':('01_2017_Б-25-09-К/1.1_01_2017_Б_25_09_К.xls','01_2017_Б-25-09-К/1.2_01_2017_Б_25_09_К.xls'),
 '2017Q2':'02_2017_Б-25-10-К/1.1_02_2017_Б_25_10_К.xls','2017Q3':'03_2017_Б-25-10-К/1.1_02_2017_Б_25_10_К.xls',
 '2017Q4':'04_2017_Б-25-10-К/1.1_02_2017_Б_25_10_К.xls','2018Q1':'1_2018_Б-25-10-К/1.1_02_2018_Б_25_10_К.xls',
 '2018Q2':'2_2018_Б-25-10-К/1.1_02_2018_Б_25_10_К.xls','2018Q3':'3_2018_Б-25-10-К/1.1_02_2017_Б_25_10_К.xls',
 '2018Q4':'04_2018-Б-25-10-К/1.1_04_2018_Б_25_10_К.xls','2019Q1':('01_2019-25-10-К/01_2019-Б_25_10_К.xls',),
 '2019Q2':('02_2019-Б_25_10_К.xls',),'2019Q3':('02_2019-Б_25_10_К/02_2019-Б_25_10_К.xls',),'2019Q4':('04_2019-Б_25_10_К/04_2019-Б_25_10_К.xls',)}
KZ={'Ақмола':'Akmola','Ақтөбе':'Aktobe','Алматы':'Almaty oblast','Атырау':'Atyrau','Батыс Қазақстан':'West Kazakhstan',
 'Жамбыл':'Zhambyl','Қарағанды':'Karaganda','Қостанай':'Kostanay','Қызылорда':'Kyzylorda','Маңғыстау':'Mangistau',
 'Павлодар':'Pavlodar','Солтүстік Қазақстан':'North Kazakhstan','Шығыс Қазақстан':'East Kazakhstan',
 'Астана қаласы':'Astana','Нұр-Сұлтан қаласы':'Astana','Алматы қаласы':'Almaty city'}
def sheets(q,v):
    ld=lambda f: xlrd.open_workbook(os.path.join(RAW,f), logfile=open(os.devnull,'w'))
    if isinstance(v,str): b=ld(v); return b.sheet_by_name('всего'), b.sheet_by_name('город')
    if len(v)==2: return ld(v[0]).sheet_by_index(0), ld(v[1]).sheet_by_index(0)
    b=ld(v[0]); return b.sheet_by_name('1.1 всего'), b.sheet_by_name('1.1 город')
out=[]
for q,v in Q.items():
    for kind,s in zip(['all','urban'],sheets(q,v)):
        seen=set()
        for r in range(s.nrows):
            lab=re.sub(r'\s+',' ',str(s.cell_value(r,0))).strip()
            if lab in KZ:
                val=s.cell_value(r,8); out.append((q,kind,KZ[lab],lab,val)); seen.add(KZ[lab])
        if len(seen)!=15: print('MISSING',q,kind,set(KZ.values())-seen)
with open('hh_repayment_panel.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['quarter','series','region','label','value']); w.writerows(out)
print(len(out))
bad=[o for o in out if not isinstance(o[4],float) or o[4]<=0]; print('nonpositive/nonnumeric',bad)
