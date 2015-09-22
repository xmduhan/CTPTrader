#!/usr/bin/env python
# encoding: utf-8

from database.models import ModelPosition, ModelOrder
from datetime import datetime


class Trader(object):

    """
    交易接口类,主要实现以下功能:
    1.定义接口类的方法框架
    2.交易数据存储的处理
    3.回调事件的绑定
    NOTE:
    1.Trader已经定义了接口方法,单仅实现了数据存储部分,实际的交易触发动作没有实现.
    2.Trader已经详细定义回调事件的结构和触发后要进行的处理,但是事件如何触发并没有实现.
    TODO:
    对于Trader的子类来说,需要做的事情就是:
    1. 重载接口方法(如:openPosition)，增加实际交易动作的触发操作(实际是发信号到工作线程)
    2. 编写工作线程,让它一方面和接口函数通讯,一方面和"服务器"(不一定时真的服务器)通讯,并回调方式触发事件.
    3. 子类甚至可以不需要重载回调方法,除非子类有特殊的数据存储需要
    """

    def __init__(self, modelStrategyExecuter=None):
        """
        相关的初始化操作
        modelStrategyExecuter
        """
        self.modelStrategyExecuter = modelStrategyExecuter

    def openPosition(self, instrumentId, direction, volume=1, openLimitPrice=0, stopPrice=0, profitPrice=0):
        """
        开仓操作
        参数:
            instrumentId 要建仓的交易品种标识
            direction 头寸方向,'buy' 做多,'sell' 做空
            volume 交易数量,默认为1手
            openLimitPrice 限价单价格,默认为0,表示不限价
            stopPrice 头寸止损价格,默认为0,表示不设置止损
            profitPrice 头寸止盈价格,默认为0,表示不设置止盈
        返回:
            order 开仓报单数据实体
        """
        data = {
            'strategyExecuter': self.modelStrategyExecuter,
            'traderClass': self.__class__.__name__,
            'instrumentId': instrumentId,
            'direction': direction,
            'volume': volume,
            'openLimitPrice': openLimitPrice,
            'stopPrice': stopPrice,
            'profitPrice': profitPrice,
        }

        # 创建头寸数据
        position = ModelPosition(**data)
        position.state = 'preopen'
        position.save()

        # 创建报单数据
        order = ModelOrder(**data)
        order.position = position
        order.action = 'open'
        order.state = 'insert'
        order.errorId = 0
        order.errorMsg = ""
        order.save()

        return order

    def closePostion(self, positionId, closeLimitPrice=0):
        """
        平仓操作
        参数:
            positionId 要平仓的头寸的标识
            closeLimitPrice 平仓限价
        返回:
            order 平仓报单数据实体
        TODO: closeLimitPrice 要如何处理还没考虑清楚
        """
        # 读取头寸信息
        position = ModelPosition.objects.get(id=positionId, state='open')
        position.state = 'preclose'
        position.closeLimitPrice = closeLimitPrice
        position.save()

        # 创建平仓订单
        order = ModelOrder()
        order.strategyExecuter = self.modelStrategyExecuter
        order.traderClass = self.__class__.__name__
        order.position = position
        order.instrumentId = position.instrumentId
        order.action = 'close'
        order.direction = position.direction
        order.volume = position.volume
        order.openLimitPrice = position.openLimitPrice
        order.openPrice = position.openPrice
        order.closeLimitPrice = closeLimitPrice
        order.stopPrice = position.stopPrice
        order.profitPrice = position.profitPrice
        order.state = 'insert'
        order.save()

        return order

    def cancelOrder(self, orderId):
        """
        取消挂单
        参数:
            orderId 原始挂单报单单号
        返回:
            cancelOrder 取消单数据实体
        """
        pass

    def setStopPrice(self, positionId, stopPrice):
        """
        设置头寸的止损线
        参数:
            positionId 对应头寸的标识
            stopPrice 止损价格
        返回:
            order 止损修改单数据实体
        """
        pass

    def setProfitPrice(self, positionId, ProfitPrice):
        """
        设置头寸的止盈线
        参数:
            positionId 对应头寸的标识
            ProfitPrice 止盈价格
        返回:
            order 止损修改单数据实体
        """
        pass

    def listPosition(self, state='open', **kwargs):
        """
        NOTE: 这里的state默认参数似乎完全没有必要
        头寸查询
        参数:
            state 头寸状态,默认为'open',默认仅查询目前处于打开状态的头寸
            kwargs 查询条件,django model查询参数格式
        返回:
            positionList 符合查询条件的头寸列表(注意是列表不是生成器)
        """
        pass

    def listOrder(self, state='insert', **kwargs):
        """
        NOTE: 这里的state默认参数似乎完全没有必要
        挂单查询
        参数:
            state 报单状态,默认为'insert',默认仅查询哪些处理中的报单
            kwargs 查询条件,django model查询参数格式
        返回:
            orderList 服务查询条件的挂单列表(注意是列表不是生成器)
        """
        pass

    def onPositionOpened(self, order, position):
        """
        头寸建立事件
        参数:
            order 创建头寸的原始报单数据实体,即openPosition的返回值
            position 新创建的头寸的数据实体
        返回:无返回
        """
        # 保存order状态
        order.state = 'finish'
        order.finishTime = datetime.now()
        order.save()
        # 保存position状态
        position.state = 'open'
        position.openTime = datetime.now()
        position.save()

    def onPostionClosed(self, order, position):
        """
        头寸平仓事件
        参数:
            order 头寸平仓的原始报单数据实体,即closePosition的返回值
            position 被平仓的头寸的数据实体
        返回:无返回
        """
        position.state = 'close'
        position.closeTime = datetime.now()
        position.save()

        order.state = 'finish'
        order.finishTime = datetime.now()
        order.save()

    def onOrderCanceled(self, order, toOrder):
        """
        报单取消成功事件
        参数:
            order 发出挂单取消请求的报单数据实体,即cancelOrder的返回值
            toOrder 被取消的挂单的数据实体
        返回:无返回
        """
        pass

    def onStopPriceSetted(self, order, position):
        """
        止损设置成功事件
        参数:
            order 发出止损修改的报单数据实体,即setStopPrice的返回值
            position 被操作影响的头寸数据实体
        返回:无返回
        """
        pass

    def onProfitPriceSetted(self, order, position):
        """
        止盈设置成功事件
        参数:
            order 发出止损修改的报单数据实体,即setProfitPrice的返回值
            position 被操作影响的头寸数据实体
        返回:无返回
        """
        pass

    def onOpenError(self, order, errorId, errorMsg, position):
        """
        头寸打开出错事件
        参数:
            order 创建头寸的原始报单数据实体,即openPosition的返回值
            errorId 出错代码
            errorMsg 出错提示信息
            position 打开失败的头寸数据实体(即便打开失败，在头寸表中也会有一条记录)
        返回:无返回
        """
        # 保存order状态信息
        order.state = 'error'
        order.errorId = errorId
        order.errorMsg = errorMsg
        order.save()
        # 保存position状态信息
        position.state = 'error'
        position.save()

    def onCloseError(self, order, errorId, errorMsg, position=None):
        """
        头寸平仓出错事件
        参数:
            order 头寸平仓的原始报单数据实体,即closePosition的返回值
            errorId 出错代码
            errorMsg 出错提示信息
            position 尝试影响的头寸数据实体
        返回:无返回
        """
        # 保存order状态信息
        order.state = 'error'
        order.finishTime = datetime.now()
        order.errorId = errorId
        order.errorMsg = errorMsg
        order.save()
        # 保存头寸状态信息(还原头寸的状态)
        position.state = 'open'
        position.closeLimitPrice = 0
        order.save()

    def onSetStopPriceError(self, order, errorId, errorMsg, position=None):
        """
        设置止损出错
        参数:
            order 发出止损修改的报单数据实体,即setStopPrice的返回值
            errorId 出错代码
            errorMsg 出错提示信息
            position 尝试影响的头寸数据实体
        返回:无返回
        """
        pass

    def onSetProfitPriceError(self, order, errorId, errorMsg, position=None):
        """
        设置止盈出错
        参数:
            order 发出止损修改的报单数据实体,即setProfitPrice的返回值
            errorId 出错代码
            errorMsg 出错提示信息
            position 尝试影响的头寸数据实体
        返回:无返回
        """
        pass

    def onCancelOrderError(self, order, errorId, errorMsg, toOrder=None):
        """
        取消挂单出错
        参数:
            order 发出挂单取消请求的报单数据实体,即cancelOrder的返回值
            errorId 出错代码
            errorMsg 出错提示信息
            toOrder 尝试影响的挂单的数据实体
        返回:无返回
        """
        pass
