# -*- coding: utf-8 -*-

from django.contrib import admin
from models import *


class AccountAdmin(admin.ModelAdmin):
    ''' '''

    fields = ['name','remarks','frontAddress','mdFrontAddress','brokerID','userID','password']

    list_display = ['id','name','frontAddress','brokerID','userID']

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

    fields = ['id','name','account','strategyDir','strategyProgram','strategyConfig',\
    'receiveAddress',    'instrumentIdList','volume','maxBuyPosition',\
    'maxSellPosition','simulate']

    list_display = ['name','account','receiveAddress','instrumentIdList','simulate']

    #list_filter = []

admin.site.register(ModelStrategyExecuter,StrategyExecuterAdmin)


class TradingRecordAdmin(admin.ModelAdmin):
    ''' '''

    fields = ['task','strategyExecuter','instrumentID','tradingDirection','volume',\
    'openPrice','closePrice','state','simulate']

    list_display = ['task','strategyExecuter','instrumentID','tradingDirection',\
        'openPrice','closePrice','volume','state','simulate']

    list_filter = ['state','tradingDirection','instrumentID','strategyExecuter','simulate']

admin.site.register(ModelTradingRecord,TradingRecordAdmin)
