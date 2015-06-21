# -*- coding: utf-8 -*-

1、为DepthMarketData增加admin修改界面
2、思考目前都需要那些config数据,并初步将模型设计
3、编写脚本讲ctp数据流保存到数据库



#%%
# 导入环境变量
import sys, os
path = r'/home/duhan/github/CTPTrader'  # 项目位置
#path = r'/home/wx/pitchersite'  # 项目位置
settings = "CTPTrader.settings"
sys.path.append(path)
os.chdir(path)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings)

#%% 
from django_pandas.io import read_frame
from data.models import DepthMarketData
from pandas.io.excel import ExcelWriter
qs = DepthMarketData.objects.all()
df = read_frame(qs)
df = df[['InstrumentID', 'AskPrice1','AskVolume1','BidPrice1','BidVolume1','TradingDay','UpdateTime','UpdateMillisec','Volume','Turnover']]
writer = ExcelWriter('/tmp/output.xls')
df.to_excel(writer)
writer.save()
#%%
InstrumentIDList = list(df.groupby('InstrumentID').count().index)
InstrumentIDList.sort()
InstrumentIDList
#%%
InstrumentData = {}
for i in InstrumentIDList:
    InstrumentData[i] = df[df.InstrumentID==i].reset_index()
    InstrumentData[i][i] = InstrumentData[i].BidPrice1
    InstrumentData[i]= InstrumentData[i][[i,'TradingDay','UpdateTime','UpdateMillisec']]    


InstrumentData[InstrumentData.keys()[0]].head()

#%%
for i,data in enumerate(InstrumentData.itervalues()):
    if i == 0 :
        resultData = data
    else:
        resultData = resultData.merge(data)
columns = ['TradingDay','UpdateTime','UpdateMillisec']
columns.extend(InstrumentIDList)
resultData = resultData[columns]
resultData = resultData.sort_index(by=['TradingDay','UpdateTime','UpdateMillisec']).reset_index(drop=True)
resultData.head(5)
writer = ExcelWriter('/tmp/output.xls')
resultData.to_excel(writer)
writer.save()
