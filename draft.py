# -*- coding: utf-8 -*-

#%% 已完成
1、为ModelDepthMarketData增加admin修改界面(ok)
1、编写脚本讲ctp数据流保存到数据库(ok)
1、删除config app,删除data改为database（ok）
(本质上这个不是一个django应用只是需要用到部分django的功能,所以把数据模块定义割裂开来似乎没有必要)
1、完成所有数据结构的model文件定义（ok）
1、配置初始化数据（ok）
1、增加策略目录并开发1个简单测试策略（ok）
1、数据生成器进程基本代码(ok)
1、关于instrumentID 和 instrumentID 的冲突问题(ok)
1、tradingRecord需要改成Position并增加，增加一个Order实体对象。(ok)
1、修改数据模型设计，去掉Task简化设计(ok)
1、执行器不应该记录的是广播地址，而应该是对应的数据生成器对象(ok)

#%% 待处理

1、绑定时间相关代码
1、order还是orderId时个大问题
1、编写测试用例



1、traderType如何表示是个问题,目前('ctp','simulate'),是否直接存储类名称更好
1、一定需要openlimit和closelimit两种订单类型吗?
1、需要一个模拟的trader
1、需要一些测试用例来保持程序质量
1、trader.orderInsert参数的大小写问题
1、策略执行器进程代码
1、后台守护进程基本代码
1、管理命令
1、日志问题字符串标识来统一(是否把日志拆分成数据生成器和策略执行器)
1、交易策略如何安装退出?如何通讯


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
from data.models import ModelDepthMarketData
from pandas.io.excel import ExcelWriter
qs = ModelDepthMarketData.objects.all()
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


#%%  动态载入模块
import os
os.chdir('/home/duhan/github/CTPTrader')
path = 'strategies/sample'
filename = 'sample.py'
fullFilePath = os.path.join(path,filename)
import imp
strategy = imp.load_source( filename.split('.')[:1][0], fullFilePath)
print hasattr(strategy,'onDataArrived')
print hasattr(strategy,'onDataArrived')
print strategy.onDataArrived.func_code.co_varnames


#%% 导入config.json文件
import os
import json
os.chdir('/home/duhan/github/CTPTrader')
filename = 'strategies/sample/config.json'
with open(filename) as f:
    print json.load(f)


#%% 创建供测试trader
import os
os.chdir('/home/duhan/github/CTPTrader')
from comhelper import setDjangoEnvironment
setDjangoEnvironment()
from database.models import ModelAccount
from trader import Trader
account = ModelAccount.objects.get(id=1)
trader = Trader(account)
#%% 测试开仓
result = trader.open('IF1508','buy',1)
print result[0],result[1],result[2]

#%% 测试列出头寸
print trader.getPositionList()

#%% 仅列出打开的头寸
print trader.getPositionList(state = 'open')



#%% 测试关闭头寸
trader.close(3)


#%%  测试ctp 交易通道是否可以建立
import os
os.chdir('/home/duhan/github/CTPTrader')
from comhelper import setDjangoEnvironment
setDjangoEnvironment()
from database.models import ModelAccount
account = ModelAccount.objects.get(id=1)

from pyctp.CTPChannel import TraderChannel
traderChannel = TraderChannel(
    account.frontAddress,
    account.brokerID,
    account.userID,
    account.password
)
traderChannel


#%% 定长队列
from collections import deque
q = deque(maxlen=10)
for i in range(10):
    q.append(i)

#%%
from pandas import Series
s = Series(range(10))
s.mean()
s.std()


#%% 交易结果导出到excel
import os
os.chdir('/home/duhan/github/CTPTrader')
from comhelper import setDjangoEnvironment
setDjangoEnvironment()
from database.models import *
from django_pandas.io import read_frame
from pandas.io.excel import ExcelWriter
df = read_frame(ModelPosition.objects.filter(state='close'))
writer = ExcelWriter('/tmp/output.xls')
df.to_excel(writer)
writer.save()

#%% 统计交易结果
import os
os.chdir('/home/duhan/github/CTPTrader')
from comhelper import setDjangoEnvironment
setDjangoEnvironment()
from database.models import *
from django_pandas.io import read_frame
df = read_frame(ModelPosition.objects.filter(state='close'))
df['profit'] = df.apply(lambda x: x.closePrice-x.openPrice if x.directionCode==u'做多' else x.openPrice-x.closePrice,axis=1)
c1 = df.id > 340
c2 = df.id < 1000
df[c1&c2]['profit'].cumsum().plot()

