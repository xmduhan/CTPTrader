#!/usr/bin/env python
# encoding: utf-8


from database.models import *
from datetime import datetime
from pyctp.CTPChannel import CThostFtdcInputOrderField

class Trader(object):
    '''
    交易处理类
    '''

    def __init__(traderChannel,task=None,strategyExecuter=None,simulate=False):
        '''
        构造函数
        traderChannel CTP Trader 交易通道的实例
        task 对应的任务数据对象(database.models.ModelTask)
        strategyExecuter 策略执行器数据对象(database.models.ModelStrategyExecuter)
        '''
        self.task = task
        self.strategy = strategyExecuter
        self.simulate = simulate
        self.brokerID = traderChannel.brokerID
        self.userID = traderChannel.userID


    def orderInsert(orderRef,instrumentId,orderPriceType = '1',direction = '0',combOffsetFlag = '0',
            combHedgeFlag = '1',limitPrice = 0,volumeTotalOriginal = 1,timeCondition = '1',gTDDate = '',
            volumeCondition = '1',minVolume = None,contingentCondition = '1',stopPrice = 0,forceCloseReason = '0',
            isAutoSuspend = 0,businessUnit = '',requestID = 1,userForceClose = 0,isSwapOrder = 0):
        '''
        orderRef 报单序列号实际就是数据对象ModelTradingRecord的id转化为字符串
        instrumentId 交易品种代码
        orderPriceType 报单价格条件 char
        //// THOST_FTDC_OPT_AnyPrice '1' 任意价
        //// THOST_FTDC_OPT_LimitPrice '2' 限价
        //// THOST_FTDC_OPT_BestPrice '3' 最优价
        //// THOST_FTDC_OPT_LastPrice '4' 最新价
        //// THOST_FTDC_OPT_LastPricePlusOneTicks '5' 最新价浮动上浮1个ticks
        //// THOST_FTDC_OPT_LastPricePlusTwoTicks '6' 最新价浮动上浮2个ticks
        //// THOST_FTDC_OPT_LastPricePlusThreeTicks '7' 最新价浮动上浮3个ticks
        //// THOST_FTDC_OPT_AskPrice1 '8' 卖一价
        //// THOST_FTDC_OPT_AskPrice1PlusOneTicks '9' 卖一价浮动上浮1个ticks
        //// THOST_FTDC_OPT_AskPrice1PlusTwoTicks 'A' 卖一价浮动上浮2个ticks
        //// THOST_FTDC_OPT_AskPrice1PlusThreeTicks 'B' 卖一价浮动上浮3个ticks
        //// THOST_FTDC_OPT_BidPrice1 'C' 买一价
        //// THOST_FTDC_OPT_BidPrice1PlusOneTicks 'D' 买一价浮动上浮1个ticks
        //// THOST_FTDC_OPT_BidPrice1PlusTwoTicks 'E' 买一价浮动上浮2个ticks
        //// THOST_FTDC_OPT_BidPrice1PlusThreeTicks 'F' 买一价浮动上浮3个ticks
        direction 买卖方向 char
        //// THOST_FTDC_D_Buy '0' 买
        //// THOST_FTDC_D_Sell '1' 卖
        combOffsetFlag 组合开平标志 char[5]
        //// THOST_FTDC_OF_Open '0' 开仓
        //// THOST_FTDC_OF_Close '1' 平仓
        //// THOST_FTDC_OF_ForceClose '2' 强平
        //// THOST_FTDC_OF_CloseToday '3' 平今
        //// THOST_FTDC_OF_CloseYesterday '4' 平昨
        //// THOST_FTDC_OF_ForceOff '5' 强减
        //// THOST_FTDC_OF_LocalForceClose '6' 本地强平
        combHedgeFlag 组合投机套保标志 char[5]
        //// THOST_FTDC_HF_Speculation '1' 投机
        //// THOST_FTDC_HF_Arbitrage '2' 套利
        //// THOST_FTDC_HF_Hedge '3' 套保
        limitPrice 价格 double
        volumeTotalOriginal 数量 int
        timeCondition 有效期类型 char
        //// THOST_FTDC_TC_IOC '1' 立即完成，否则撤销
        //// THOST_FTDC_TC_GFS '2' 本节有效
        //// THOST_FTDC_TC_GFD '3' 当日有效
        //// THOST_FTDC_TC_GTD '4' 指定日期前有效
        //// THOST_FTDC_TC_GTC '5' 撤销前有效
        //// THOST_FTDC_TC_GFA '6' 集合竞价有效
        gTDDate GTD日期 char[9]
        volumeCondition 成交量类型 char
        //// THOST_FTDC_VC_AV '1' 任何数量
        //// THOST_FTDC_VC_MV '2' 最小数量
        //// THOST_FTDC_VC_CV '3' 全部数量
        minVolume 最小成交量 int
        contingentCondition 触发条件 char
        //// THOST_FTDC_CC_Immediately '1' 立即
        //// THOST_FTDC_CC_Touch '2' 止损
        //// THOST_FTDC_CC_TouchProfit '3' 止赢
        //// THOST_FTDC_CC_ParkedOrder '4' 预埋单
        //// THOST_FTDC_CC_LastPriceGreaterThanStopPrice '5' 最新价大于条件价
        //// THOST_FTDC_CC_LastPriceGreaterEqualStopPrice '6' 最新价大于等于条件价
        //// THOST_FTDC_CC_LastPriceLesserThanStopPrice '7' 最新价小于条件价
        //// THOST_FTDC_CC_LastPriceLesserEqualStopPrice '8' 最新价小于等于条件价
        //// THOST_FTDC_CC_AskPriceGreaterThanStopPrice '9' 卖一价大于条件价
        //// THOST_FTDC_CC_AskPriceGreaterEqualStopPrice 'A' 卖一价大于等于条件价
        //// THOST_FTDC_CC_AskPriceLesserThanStopPrice 'B' 卖一价小于条件价
        //// THOST_FTDC_CC_AskPriceLesserEqualStopPrice 'C' 卖一价小于等于条件价
        //// THOST_FTDC_CC_BidPriceGreaterThanStopPrice 'D' 买一价大于条件价
        //// THOST_FTDC_CC_BidPriceGreaterEqualStopPrice 'E' 买一价大于等于条件价
        //// THOST_FTDC_CC_BidPriceLesserThanStopPrice 'F' 买一价小于条件价
        //// THOST_FTDC_CC_BidPriceLesserEqualStopPrice 'H' 买一价小于等于条件价
        stopPrice 止损价 double
        forceCloseReason 强平原因 char
        //// THOST_FTDC_CC_Immediately '1' 立即
        //// THOST_FTDC_CC_Touch '2' 止损
        //// THOST_FTDC_CC_TouchProfit '3' 止赢
        //// THOST_FTDC_CC_ParkedOrder '4' 预埋单
        //// THOST_FTDC_CC_LastPriceGreaterThanStopPrice '5' 最新价大于条件价
        //// THOST_FTDC_CC_LastPriceGreaterEqualStopPrice '6' 最新价大于等于条件价
        //// THOST_FTDC_CC_LastPriceLesserThanStopPrice '7' 最新价小于条件价
        //// THOST_FTDC_CC_LastPriceLesserEqualStopPrice '8' 最新价小于等于条件价
        //// THOST_FTDC_CC_AskPriceGreaterThanStopPrice '9' 卖一价大于条件价
        //// THOST_FTDC_CC_AskPriceGreaterEqualStopPrice 'A' 卖一价大于等于条件价
        //// THOST_FTDC_CC_AskPriceLesserThanStopPrice 'B' 卖一价小于条件价
        //// THOST_FTDC_CC_AskPriceLesserEqualStopPrice 'C' 卖一价小于等于条件价
        //// THOST_FTDC_CC_BidPriceGreaterThanStopPrice 'D' 买一价大于条件价
        //// THOST_FTDC_CC_BidPriceGreaterEqualStopPrice 'E' 买一价大于等于条件价
        //// THOST_FTDC_CC_BidPriceLesserThanStopPrice 'F' 买一价小于条件价
        //// THOST_FTDC_CC_BidPriceLesserEqualStopPrice 'H' 买一价小于等于条件价
        isAutoSuspend 自动挂起标志 int
        businessUnit 业务单元 char[21]
        requestID 请求编号 int
        userForceClose 用户强评标志 int
        isSwapOrder 互换单标志 int
        '''
        requestData = CThostFtdcInputOrderField()
        requestData.BrokerID = self.brokerID
        requestData.InvestorID = self.userID
        requestData.InstrumentID = instrumentId
        requestData.OrderRef = orderRef
        requestData.UserID = self.userID
        requestData.OrderPriceType = orderPriceType
        requestData.Direction = direction
        requestData.CombOffsetFlag = combOffsetFlag
        requestData.CombHedgeFlag = combHedgeFlag
        requestData.LimitPrice = limitPrice
        requestData.VolumeTotalOriginal = volumeTotalOriginal
        requestData.TimeCondition = timeCondition
        requestData.GTDDate = gTDDate
        requestData.VolumeCondition = volumeCondition
        requestData.MinVolume = minVolume or volumeTotalOriginal
        requestData.ContingentCondition = contingentCondition
        requestData.StopPrice = stopPrice
        requestData.ForceCloseReason = forceCloseReason
        requestData.IsAutoSuspend = isAutoSuspend
        requestData.BusinessUnit = businessUnit
        requestData.RequestID = requestID
        requestData.UserForceClose = userForceClose
        requestData.IsSwapOrder = isSwapOrder

        result = traderChannel.OrderInsert(requestData)
        return result


    def openPosition(instrumentId,direction,volume):
        '''
        创建头寸
        '''
        # 创建一条预开单记录
        tradingRecord = ModelTradingRecord()
        tradingRecord.task = self.task
        tradingRecord.strategyExecuter = self.strategyExecuter
        tradingRecord.simulate = self.simulate
        tradingRecord.instrumentID = instrumentId
        tradingRecord.direction = direction
        tradingRecord.volume = volume
        tradingRecord.openTime = datetime.now()
        tradingRecord.state =  'preopen'
        tradingRecord.save()


        # 创建头寸



    def listPosition(state):
        '''
        查看头寸
        '''
        pass


    def closePostion(tradingRecordId):
        '''
        关闭头寸
        '''
        pass











