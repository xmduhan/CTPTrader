# -*- coding: utf-8 -*-

from django.contrib import admin
from models import *


class AccountAdmin(admin.ModelAdmin):
    ''' '''

    fields = ['name','remarks','frontAddress','mdFrontAddress','brokerId','userId','password']

    list_display = ['id','name','frontAddress','brokerId','userId']

admin.site.register(ModelAccount,AccountAdmin)


class TaskAdmin(admin.ModelAdmin):
    ''' '''

    fields = ['type','typeRelaId','name','pid','startTime','endTime','state']

    list_display = ['name','type','pid','startTime','state']

    list_filter = ['state']

admin.site.register(ModelTask,TaskAdmin)


class TaskLogAdmin(admin.ModelAdmin):
    ''' '''
    # TODO 要增加通过DataGenerator或StrategyExecuter配置进行过滤的功能
    fields = ['task','logTime','logMessage']

    list_display = ['task','logTime','logMessage']

    list_filter = ['task']

admin.site.register(ModelTaskLog,TaskLogAdmin)


class DataCatalogAdmin(admin.ModelAdmin):
    ''' '''

    fields = ['name','remarks']

    list_display = ['name','remarks']

    #list_filter = []

admin.site.register(ModelDataCatalog,DataCatalogAdmin)



class DepthMarketDataAdmin(admin.ModelAdmin):
    ''' '''

    fields = ['dataCatalog','dataTime', \
        'TradingDay', 'InstrumentID', 'ExchangeID', 'ExchangeInstID',\
        'LastPrice', 'PreSettlementPrice', 'PreClosePrice', 'PreOpenInterest',\
        'OpenPrice', 'HighestPrice', 'LowestPrice', 'Volume', 'Turnover',\
        'OpenInterest', 'ClosePrice', 'SettlementPrice', 'UpperLimitPrice',\
        'LowerLimitPrice', 'PreDelta', 'CurrDelta', 'UpdateTime',\
        'UpdateMillisec', 'BidPrice1', 'BidVolume1', 'AskPrice1','AskVolume1',\
        'BidPrice2', 'BidVolume2', 'AskPrice2', 'AskVolume2', 'BidPrice3',\
        'BidVolume3', 'AskPrice3', 'AskVolume3', 'BidPrice4', 'BidVolume4',\
        'AskPrice4', 'AskVolume4', 'BidPrice5', 'BidVolume5', 'AskPrice5',\
        'AskVolume5', 'AveragePrice', 'ActionDay']

    list_display = ['dataCatalog','InstrumentID', 'dataTime',
        'AskPrice1','AskVolume1','BidPrice1','BidVolume1','Volume','Turnover']

    list_filter = ['InstrumentID','dataCatalog']

    date_hierarchy = 'dataTime'

admin.site.register(ModelDepthMarketData,DepthMarketDataAdmin)


class DataGeneratorAdmin(admin.ModelAdmin):
    ''' '''

    fields = ['name','account','dataCatalog','dataSource','datetimeBegin','datetimeEnd',\
        'instrumentIdList','saveRawData','saveBarData','saveIndexData','broadcastAddress','interval']

    list_display = ['id','name','account','dataCatalog','dataSource','broadcastAddress']

    list_filter = ['account']

admin.site.register(ModelDataGenerator,DataGeneratorAdmin)


class StrategyExecuterAdmin(admin.ModelAdmin):
    ''' '''

    fields = ['name','account','strategyDir','strategyProgram','strategyConfig',\
    'receiveAddress',    'instrumentIdList','volume','maxBuyPosition',\
    'maxSellPosition','simulate']

    list_display = ['id','name','account','receiveAddress','instrumentIdList','simulate']

    #list_filter = []

admin.site.register(ModelStrategyExecuter,StrategyExecuterAdmin)


class PositionAdmin(admin.ModelAdmin):
    ''' '''

    fields = ['task','strategyExecuter','instrumentId','directionCode','volume',\
    'openPrice','closePrice','state','simulate','lastErrorId','lastErrorMsg']

    list_display = ['id','task','strategyExecuter','instrumentId','directionCode',\
        'openPrice','closePrice','volume','state','simulate','profit']

    list_filter = ['state','directionCode','instrumentId','strategyExecuter','simulate']

admin.site.register(ModelPosition,PositionAdmin)


class OrderAdmin(admin.ModelAdmin):
    ''' '''
    fields = ['task','strategyExecuter','position','simulate','orderRef','instrumentId',\
        'action','directionCode','volume','price','priceCondition','insertTime','finishTime',\
        'state','errorId','errorMsg']

    list_display = ['orderRef','instrumentId','action','directionCode','volume','price',\
            'priceCondition','insertTime','finishTime','state']

    list_filter = ['task','strategyExecuter','simulate']


admin.site.register(ModelOrder,OrderAdmin)



