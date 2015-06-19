# -*- coding: utf-8 -*-

from django.contrib import admin
from models import *
# Register your models here.


class DepthMarketDataAdmin(admin.ModelAdmin):
    fields = ['TradingDay', 'InstrumentID', 'ExchangeID', 'ExchangeInstID',\
        'LastPrice', 'PreSettlementPrice', 'PreClosePrice', 'PreOpenInterest',\
        'OpenPrice', 'HighestPrice', 'LowestPrice', 'Volume', 'Turnover',\
        'OpenInterest', 'ClosePrice', 'SettlementPrice', 'UpperLimitPrice',\
        'LowerLimitPrice', 'PreDelta', 'CurrDelta', 'UpdateTime',\
        'UpdateMillisec', 'BidPrice1', 'BidVolume1', 'AskPrice1','AskVolume1',\
        'BidPrice2', 'BidVolume2', 'AskPrice2', 'AskVolume2', 'BidPrice3',\
        'BidVolume3', 'AskPrice3', 'AskVolume3', 'BidPrice4', 'BidVolume4',\
        'AskPrice4', 'AskVolume4', 'BidPrice5', 'BidVolume5', 'AskPrice5',\
        'AskVolume5', 'AveragePrice', 'ActionDay']
    list_display = ('InstrumentID', 'AskPrice1','AskVolume1','BidPrice1','BidVolume1', \
        'TradingDay','UpdateTime','UpdateMillisec','Volume','Turnover')

    list_filter = ('InstrumentID','TradingDay')

    #date_hierarchy = 'TradingDay'

admin.site.register(DepthMarketData,DepthMarketDataAdmin)
