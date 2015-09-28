#!/usr/bin/env python
# encoding: utf-8
from __future__ import division
from database.models import ModelPosition, ModelOrder
from datetime import datetime
from comhelper import CallbackManager
import threading
import error

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
        NOTE: 这里的参数使用的是执行器的数据实体,但是这似乎是有问题,如果获取交易数据流,需要进一步考虑
        """
        self.events = [m for m in dir(self) if callable(getattr(self, m)) and m.startswith('on')]
        self.modelStrategyExecuter = modelStrategyExecuter
        self.__callbackManager = CallbackManager()

    def getClass(self):
        """
        获得当前交易接口的类名
        """
        return self.__class__.__name__

    def bind(self, callbackName, funcToCall):
        """转调回调链管理器"""
        if callbackName not in self.events:
            raise Exception('尝试绑带无效事件')
        return self.__callbackManager.bind(callbackName, funcToCall)

    def unbind(self, bindId):
        """转调回调管理器"""
        return self.__callbackManager.unbind(bindId)

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
            'traderClass': self.getClass(),
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

    def closePosition(self, positionId, closeLimitPrice=0):
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
        order.traderClass = self.getClass()
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
        toOrder = ModelOrder.objects.get(id=orderId)
        order = ModelOrder()
        order.strategyExecuter = self.modelStrategyExecuter
        order.traderClass = self.getClass()
        order.position = toOrder.position
        order.order = toOrder
        order.instrumentId = toOrder.instrumentId
        order.action = 'cancel'
        order.direction = toOrder.direction
        order.volume = toOrder.volume
        order.openLimitPrice = toOrder.openLimitPrice
        order.stopPrice = toOrder.stopPrice
        order.profitPrice = toOrder.profitPrice
        order.state = 'insert'
        order.save()

        return order

    def setStopPrice(self, positionId, stopPrice):
        """
        设置头寸的止损线
        参数:
            positionId 对应头寸的标识
            stopPrice 止损价格
        返回:
            order 止损修改单数据实体
        """
        position = ModelPosition.objects.get(id=positionId, state='open')

        # 创建修改止损订单
        order = ModelOrder()
        order.strategyExecuter = self.modelStrategyExecuter
        order.traderClass = self.getClass()
        order.position = position
        order.instrumentId = position.instrumentId
        order.action = 'setstop'
        order.direction = position.direction
        order.volume = position.volume
        order.openLimitPrice = position.openLimitPrice
        order.openPrice = position.openPrice
        order.closeLimitPrice = position.closeLimitPrice
        order.stopPrice = position.stopPrice
        order.profitPrice = position.profitPrice
        order.stopPrice = stopPrice
        order.state = 'insert'
        order.save()

        return order

    def setProfitPrice(self, positionId, profitPrice):
        """
        设置头寸的止盈线
        参数:
            positionId 对应头寸的标识
            profitPrice 止盈价格
        返回:
            order 止损修改单数据实体
        """
        position = ModelPosition.objects.get(id=positionId, state='open')

        # 创建修改止损订单
        order = ModelOrder()
        order.strategyExecuter = self.modelStrategyExecuter
        order.traderClass = self.getClass()
        order.position = position
        order.instrumentId = position.instrumentId
        order.action = 'setprofit'
        order.direction = position.direction
        order.volume = position.volume
        order.openLimitPrice = position.openLimitPrice
        order.openPrice = position.openPrice
        order.closeLimitPrice = position.closeLimitPrice
        order.stopPrice = position.stopPrice
        order.profitPrice = position.profitPrice
        order.profitPrice = profitPrice
        order.state = 'insert'
        order.save()

        return order

    def getPositionList(self, update=False, **kwargs):
        """
        头寸查询
        参数:
            update 是否使用for update加锁选项
            kwargs 查询条件,django model查询参数格式
        返回:
            positionList 符合查询条件的头寸列表(注意是列表不是生成器)
        """
        query = ModelPosition.objects.filter(strategyExecuter=self.modelStrategyExecuter)
        query = query.filter(**kwargs)
        if update:
            query = query.select_for_update()
        return list(query)

    def getOrderList(self, update=False, **kwargs):
        """
        挂单查询
        参数:
            update 是否使用for update加锁选项
            kwargs 查询条件,django model查询参数格式
        返回:
            orderList 服务查询条件的挂单列表(注意是列表不是生成器)
        """
        query = ModelOrder.objects.filter(strategyExecuter=self.modelStrategyExecuter)
        query = query.filter(**kwargs)
        if update:
            query = query.select_for_update()
        return list(query)

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

        # 将事件传入绑定函数
        parameters = {'order': order, 'position': position}
        self.__callbackManager.callback('onPositionOpened', parameters)

    def onPositionClosed(self, order, position):
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

        # 将事件传入绑定函数
        parameters = {'order': order, 'position': position}
        self.__callbackManager.callback('onPositionClosed', parameters)

    def onOrderCanceled(self, order, toOrder):
        """
        报单取消成功事件
        参数:
            order 发出挂单取消请求的报单数据实体,即cancelOrder的返回值
            toOrder 被取消的挂单的数据实体
        返回:无返回
        """
        # 设置取消单的状态
        order.state = 'finish'
        order.finishTime = datetime.now()
        order.save()

        # 设置报单状态
        toOrder.state = 'cancel'
        toOrder.finishTime = datetime.now()
        toOrder.save()

        # 设置头寸状态
        position = toOrder.position
        position.state = 'cancel'
        position.save()

    def onStopPriceSetted(self, order, position):
        """
        止损设置成功事件
        参数:
            order 发出止损修改的报单数据实体,即setStopPrice的返回值
            position 被操作影响的头寸数据实体
        返回:无返回
        """
        # 设置订单完成状态
        order.state = 'finish'
        order.finishTime = datetime.now()
        order.save()

        # 设置头寸的的止损
        position.stopPrice = order.stopPrice
        position.save()

    def onProfitPriceSetted(self, order, position):
        """
        止盈设置成功事件
        参数:
            order 发出止损修改的报单数据实体,即setProfitPrice的返回值
            position 被操作影响的头寸数据实体
        返回:无返回
        """
        # 设置订单完成状态
        order.state = 'finish'
        order.finishTime = datetime.now()
        order.save()

        # 设置头寸的的止损
        position.profitPrice = order.profitPrice
        position.save()

    def onOpenPositionError(self, order, errorId, errorMsg, position):
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

        # 将事件传入绑定函数
        parameters = {
            'order': order,
            'errorId': errorId,
            'errorMsg': errorMsg,
            'position': position
        }
        self.__callbackManager.callback('onOpenPositionError', parameters)

    def onClosePositionError(self, order, errorId, errorMsg, position=None):
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

        # 将事件传入绑定函数
        parameters = {
            'order': order,
            'errorId': errorId,
            'errorMsg': errorMsg,
            'position': position
        }
        self.__callbackManager.callback('onClosePositionError', parameters)

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
        order.errorId = errorId
        order.errorMsg = errorMsg
        order.state = 'error'
        order.finishTime = datetime.now()
        order.save()

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
        order.errorId = errorId
        order.errorMsg = errorMsg
        order.state = 'error'
        order.finishTime = datetime.now()
        order.save()

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
        order.errorId = errorId
        order.errorMsg = errorMsg
        order.state = 'error'
        order.finishTime = datetime.now()
        order.save()


class SimulateTrader(Trader):
    """
    模拟交易类接口
    NOTE: 对象清理的问题需要进一步考虑
    """

    def __init__(self, modelStrategyExecuter=None):
        """
        初始化处理
        """
        # 调用父类构造函数
        super(SimulateTrader, self).__init__(modelStrategyExecuter)

    def working(self):
        """
        工作线程方法
        """
        while True:
            # 更新报价数据
            pass
            # 处理报单数据

    def start(self):
        """
        启动工作线程
        """
        # 创建工作线程
        self.thread = threading.Thread(target=self.working)
        self.thread.start()

    def processOpenOrder(self, instrumentId, ask, bid):
        """
        处理开仓报单
        NOTE: 这里可能和取消订单操作出现资源争用问题
        """
        def _openPosition(order, price):
            # 设置成交报价
            position = order.position
            order.openPrice = price
            position.openPrice = price
            # 触发成交事件
            self.onPositionOpened(order, position)

        # 尝试处理所有开仓报单
        openOrderList = self.getOrderList(action='open', state='insert')
        for order in openOrderList:
            if order.instrumentId == instrumentId:
                direction = order.direction
                limitPrice = order.openLimitPrice
                price = {'buy': bid, 'sell': ask}[direction]
                la = {'buy': lambda x: x>=price, 'sell': lambda x: x<=price}[direction]
                if limitPrice == 0:
                    _openPosition(order, price)
                else:
                    if la(limitPrice):
                        _openPosition(order, (price + limitPrice) / 2)

    def processCloseOrder(self, instrumentId, ask, bid):
        """
        平仓订单处理
        """
        def _closePosition(order, price):
            # 设置成交报价
            position = order.position
            order.closePrice = price
            position.closePrice = price
            # 触发成交事件
            self.onPositionClosed(order, position)

        closeOrderList = self.getOrderList(action='close', state='insert')
        for order in closeOrderList:
            if order.instrumentId == instrumentId:
                direction = order.direction
                limitPrice = order.closeLimitPrice
                price = {'buy': ask, 'sell': bid}[direction]
                la = {'buy': lambda x: x<=price, 'sell': lambda x: x>=price}[direction]
                if limitPrice == 0:
                    _closePosition(order, price)
                else:
                    if la(limitPrice):
                        _closePosition(order, (price + limitPrice) / 2)

    def processCancelOrder(self):
        """
        取消订单操作
        """
        cancelOrderList = self.getOrderList(action='cancel', state='insert')
        for order in cancelOrderList:
            toOrder = order.order
            if len(self.getOrderList(id=toOrder.id, state='insert')) >= 1:
                self.onOrderCanceled(order, toOrder)
            else:
                errorId, errorMsg = error.OrderNoActive
                self.onCancelOrderError(order, errorId, errorMsg, toOrder)

    def processStopPrice(self):
        """
        处理止损
        """
        pass

    def onDataArrived(self, instrumentId, ask, bid):
        """
        品种的最近报价到达
        """
        # 处理开仓报单
        self.processOpenOrder(instrumentId, ask, bid)
        # 处理平仓报单
        self.processCloseOrder(instrumentId, ask, bid)
        # 处理撤单
        self.processCancelOrder()

    def openPosition(self, *args, **kwargs):
        """
        打开头寸的处理
        """
        order = super(SimulateTrader, self).openPosition(*args, **kwargs)
        return order

    def closePosition(self, *args, **kwargs):
        """
        关闭头寸的处理
        """
        order = super(SimulateTrader, self).closePosition(*args, **kwargs)
        return order

    def cancelOrder(self, *args, **kwargs):
        """
        撤单处理
        """
        order = super(SimulateTrader, self).cancelOrder(*args, **kwargs)
        return order

