# -*- coding: utf-8 -*-
from django.db import models

# Create your models here.


class DepthMarketData(models.Model):
    '''
    深度行情数据存储(对应CTP数据结构CThostFtdcDepthMarketDataField)
    '''
    TradingDay = models.CharField(u'交易日', max_length=9, default='')
    InstrumentID = models.CharField(u'合约代码', max_length=31, default='')
    ExchangeID = models.CharField(u'交易所代码', max_length=9, default='')
    ExchangeInstID = models.CharField(u'合约在交易所的代码', max_length=31, default='')
    LastPrice = models.FloatField(u'最新价', default=0)
    PreSettlementPrice = models.FloatField(u'上次结算价', default=0)
    PreClosePrice = models.FloatField(u'昨收盘', default=0)
    PreOpenInterest = models.FloatField(u'昨持仓量', default=0)
    OpenPrice = models.FloatField(u'今开盘', default=0)
    HighestPrice = models.FloatField(u'最高价', default=0)
    LowestPrice = models.FloatField(u'最低价', default=0)
    Volume = models.IntegerField(u'数量', default=0)
    Turnover = models.FloatField(u'成交金额', default=0)
    OpenInterest = models.FloatField(u'持仓量', default=0)
    ClosePrice = models.FloatField(u'今收盘', default=0)
    SettlementPrice = models.FloatField(u'本次结算价', default=0)
    UpperLimitPrice = models.FloatField(u'涨停板价', default=0)
    LowerLimitPrice = models.FloatField(u'跌停板价', default=0)
    PreDelta = models.FloatField(u'昨虚实度', default=0)
    CurrDelta = models.FloatField(u'今虚实度', default=0)
    UpdateTime = models.CharField(u'最后修改时间', max_length=9, default='')
    UpdateMillisec = models.IntegerField(u'最后修改毫秒', default=0)
    BidPrice1 = models.FloatField(u'申买价一', default=0)
    BidVolume1 = models.IntegerField(u'申买量一', default=0)
    AskPrice1 = models.FloatField(u'申卖价一', default=0)
    AskVolume1 = models.IntegerField(u'申卖量一', default=0)
    BidPrice2 = models.FloatField(u'申买价二', default=0)
    BidVolume2 = models.IntegerField(u'申买量二', default=0)
    AskPrice2 = models.FloatField(u'申卖价二', default=0)
    AskVolume2 = models.IntegerField(u'申卖量二', default=0)
    BidPrice3 = models.FloatField(u'申买价三', default=0)
    BidVolume3 = models.IntegerField(u'申买量三', default=0)
    AskPrice3 = models.FloatField(u'申卖价三', default=0)
    AskVolume3 = models.IntegerField(u'申卖量三', default=0)
    BidPrice4 = models.FloatField(u'申买价四', default=0)
    BidVolume4 = models.IntegerField(u'申买量四', default=0)
    AskPrice4 = models.FloatField(u'申卖价四', default=0)
    AskVolume4 = models.IntegerField(u'申卖量四', default=0)
    BidPrice5 = models.FloatField(u'申买价五', default=0)
    BidVolume5 = models.IntegerField(u'申买量五', default=0)
    AskPrice5 = models.FloatField(u'申卖价五', default=0)
    AskVolume5 = models.IntegerField(u'申卖量五', default=0)
    AveragePrice = models.FloatField(u'当日均价', default=0)
    ActionDay = models.CharField(u'业务日期', max_length=9, default='')

    class Meta:
        ordering = ['-TradingDay','-UpdateTime','-UpdateMillisec']
