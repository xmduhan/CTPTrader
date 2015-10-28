#!/usr/bin/env python
# encoding: utf-8

from trader import Trader
from comhelper import getDefaultInstrumentId
from database.models import ModelOrder, ModelPosition


def setup():
    """
    测试用例初始化
    """
    pass


def test_open_position():
    """
    测试打开头寸
    """
    flag = []

    def onPositionOpened(order, position):
        flag.append([order, position])

    trader = Trader()
    trader.bind('onPositionOpened', onPositionOpened)

    # 尝试进行打开头寸报单
    order = trader.openPosition(getDefaultInstrumentId(), 'buy', 1)
    assert isinstance(order, ModelOrder)
    assert order.id is not None
    assert order.state == 'insert'
    assert order.action == 'open'
    assert order.finishTime is None
    assert order.openLimitPrice == 0
    position = order.position
    assert isinstance(position, ModelPosition)
    assert position.id is not None
    assert position.state == 'preopen'
    assert position.openTime is None
    assert position.openLimitPrice == 0

    # 模拟头寸创建成功事件发生
    trader.onPositionOpened(order, position)
    assert order.state == 'finish'
    assert order.finishTime is not None
    assert position.state == 'open'
    assert position.openTime is not None
    assert order.errorId == 0
    assert order.errorMsg == ""
    # NOTE: 因为trader还为实现议价机制,所以此时价格仍为空
    assert position.openPrice is None
    assert order.openPrice is None

    # 检查绑定事件正常传递
    assert len(flag) == 1
    assert flag[0][0] == order
    assert flag[0][1] == position


def test_open_position_error():
    """
    测试打开头寸出错的情况
    """
    flag = []

    def onOpenPositionError(order, errorId, errorMsg, position):
        flag.append([order, errorId, errorMsg, position])

    trader = Trader()
    trader.bind('onOpenPositionError', onOpenPositionError)
    # 尝试打开头寸的报单
    order = trader.openPosition(getDefaultInstrumentId(), 'buy', 1)
    position = order.position

    # 模拟打开头寸出错的情况
    errorId = -1
    errorMsg = u'测试'
    trader.onOpenPositionError(order, errorId, errorMsg, position)
    assert order.state == 'error'
    assert order.errorId == errorId
    assert order.errorMsg == errorMsg
    assert position.state == 'error'

    # 检查事件正常传递
    assert len(flag) == 1
    assert flag[0][0] == order
    assert flag[0][1] == errorId
    assert flag[0][2] == errorMsg
    assert flag[0][3] == position


def test_close_position():
    """
    测试关闭头寸
    """
    flag = []

    def onPositionClosed(order, position):
        flag.append([order, position])

    trader = Trader()
    trader.bind('onPositionClosed', onPositionClosed)
    # 创建一个头寸供关闭使用
    openOrder = trader.openPosition(getDefaultInstrumentId(), 'buy', 1)
    position = openOrder.position
    trader.onPositionOpened(openOrder, position)
    assert position.state == 'open'

    # 测试头寸关闭操作
    closeOrder = trader.closePosition(position.id)
    assert isinstance(closeOrder, ModelOrder)
    assert closeOrder.id is not None
    assert closeOrder.position == position
    assert closeOrder.action == 'close'
    assert closeOrder.state == 'insert'
    assert closeOrder.finishTime is None
    assert closeOrder.closeLimitPrice == 0
    position = ModelPosition.objects.get(id=position.id)
    assert closeOrder.position == position
    assert position.state == 'preclose'
    assert position.closeTime is None
    assert position.closeLimitPrice == 0

    # 模拟头寸正常关闭事件
    trader.onPositionClosed(closeOrder, position)
    assert closeOrder.state == 'finish'
    assert closeOrder.finishTime is not None
    assert position.state == 'close'
    assert position.closeTime is not None

    # NOTE: 因为trader还为实现议价机制,所以此时价格仍为空
    assert position.closePrice is None
    assert closeOrder.closePrice is None

    # 检查事件正常传递
    assert len(flag) == 1
    assert flag[0][0] == closeOrder
    assert flag[0][1] == position


def test_close_position_error():
    """
    测试关闭头寸出错的情况
    """
    flag = []

    def onClosePositionError(order, errorId, errorMsg, position=None):
        flag.append([order, errorId, errorMsg, position])

    trader = Trader()
    trader.bind('onClosePositionError', onClosePositionError)
    # 创建一个头寸并关闭它
    openOrder = trader.openPosition(getDefaultInstrumentId(), 'buy', 1)
    position = openOrder.position
    trader.onPositionOpened(openOrder, position)
    assert position.state == 'open'
    closeOrder = trader.closePosition(position.id)
    position = ModelPosition.objects.get(id=position.id)
    # 模拟头寸创建失败事件
    errorId = -1
    errorMsg = u'测试'
    trader.onClosePositionError(closeOrder, errorId, errorMsg, position)
    assert closeOrder.state == 'error'
    assert closeOrder.finishTime is not None
    assert closeOrder.errorId == errorId
    assert closeOrder.errorMsg == errorMsg
    assert position.state == 'open'
    assert position.closeTime is None

    # 检查事件正常传递
    assert len(flag) == 1
    assert flag[0][0] == closeOrder
    assert flag[0][1] == errorId
    assert flag[0][2] == errorMsg
    assert flag[0][3] == position


def test_open_and_close_position_with_limit_price():
    """
    测试使用限价打开和关闭头寸
    """
    openLimitPrice = 1000
    closeLimitPrice = 2000
    trader = Trader()

    # 打开头寸
    order = trader.openPosition(
        instrumentId=getDefaultInstrumentId(),
        direction='buy',
        volume=1,
        openLimitPrice=openLimitPrice
    )
    position = order.position
    assert order.openLimitPrice == openLimitPrice
    assert position.openLimitPrice == openLimitPrice

    # 打开头寸成功
    trader.onPositionOpened(order, position)
    order = ModelOrder.objects.get(id=order.id)
    position = ModelPosition.objects.get(id=position.id)
    assert order.openLimitPrice == openLimitPrice
    assert position.openLimitPrice == openLimitPrice

    # 关闭头寸
    order = trader.closePosition(position.id, closeLimitPrice=closeLimitPrice)
    position = ModelPosition.objects.get(id=position.id)
    assert order.closeLimitPrice == closeLimitPrice
    assert position.closeLimitPrice == closeLimitPrice

    # 关闭头寸成功
    trader.onPositionClosed(order, position)
    order = ModelOrder.objects.get(id=order.id)
    position = ModelPosition.objects.get(id=position.id)
    assert order.closeLimitPrice == closeLimitPrice
    assert position.closeLimitPrice == closeLimitPrice


def test_set_stop_and_profit_price_success():
    """
    测试设置止损价格和止盈价格并成功
    """
    stopPrice0 = 1000
    stopPrice1 = stopPrice0 + 10
    profitPrice0 = 2000
    profitPrice1 = profitPrice0 - 10

    trader = Trader()

    # 打开头寸
    order0 = trader.openPosition(
        instrumentId=getDefaultInstrumentId(),
        direction='buy',
        volume=1,
        stopPrice=stopPrice0,
        profitPrice=profitPrice0
    )
    position = order0.position
    assert order0.stopPrice == stopPrice0
    assert order0.profitPrice == profitPrice0
    assert position.stopPrice == stopPrice0
    assert position.profitPrice == profitPrice0

    # 打开头寸成功
    trader.onPositionOpened(order0, position)

    # 设置止损
    order1 = trader.setStopPrice(position.id, stopPrice=stopPrice1)
    position = ModelPosition.objects.get(id=position.id)
    assert order1 != order0
    assert order1.position == position
    assert order1.action == 'setstop'
    assert order1.state == 'insert'
    assert order1.finishTime is None
    assert order1.stopPrice == stopPrice1
    assert position.stopPrice == stopPrice0   # 修改成功前应保持旧值

    # 设置止损成功
    trader.onStopPriceSetted(order1, position)
    order1 = ModelOrder.objects.get(id=order1.id)
    position = ModelPosition.objects.get(id=position.id)
    assert order1.state == 'finish'
    assert order1.finishTime is not None
    assert position.stopPrice == stopPrice1  # 修改成功后为新值

    # 设置止盈
    order2 = trader.setProfitPrice(position.id, profitPrice=profitPrice1)
    position = ModelPosition.objects.get(id=position.id)
    assert order2.position == position
    assert order2.action == 'setprofit'
    assert order2.state == 'insert'
    assert order2.finishTime is None
    assert order2.profitPrice == profitPrice1
    assert position.profitPrice == profitPrice0

    # 设置止盈成功
    trader.onProfitPriceSetted(order2, position)
    order2 = ModelOrder.objects.get(id=order2.id)
    position = ModelPosition.objects.get(id=position.id)
    assert order2.state == 'finish'
    assert order2.finishTime is not None
    assert position.profitPrice == profitPrice1


def test_set_stop_and_profit_price_fail():
    """
    测试设置止损价格和止盈价格但失败
    """
    stopPrice0 = 1000
    stopPrice1 = stopPrice0 + 10
    profitPrice0 = 2000
    profitPrice1 = profitPrice0 - 10

    trader = Trader()

    # 打开头寸
    order0 = trader.openPosition(
        instrumentId=getDefaultInstrumentId(),
        direction='buy',
        volume=1,
        stopPrice=stopPrice0,
        profitPrice=profitPrice0
    )
    position = order0.position
    assert order0.stopPrice == stopPrice0
    assert order0.profitPrice == profitPrice0
    assert position.stopPrice == stopPrice0
    assert position.profitPrice == profitPrice0

    # 打开头寸成功
    trader.onPositionOpened(order0, position)

    # 设置止损
    order1 = trader.setStopPrice(position.id, stopPrice=stopPrice1)
    position = ModelPosition.objects.get(id=position.id)
    assert order1 != order0
    assert order1.position == position
    assert order1.action == 'setstop'
    assert order1.state == 'insert'
    assert order1.finishTime is None
    assert order1.stopPrice == stopPrice1
    assert position.stopPrice == stopPrice0   # 修改成功前应保持旧值

    # 设置止损失败
    errorId = -1
    errorMsg = u'测试'
    trader.onSetStopPriceError(order1, errorId, errorMsg, position)
    order1 = ModelOrder.objects.get(id=order1.id)
    position = ModelPosition.objects.get(id=position.id)
    assert order1.state == 'error'
    assert order1.errorId == errorId
    assert order1.errorMsg == errorMsg
    assert order1.finishTime is not None
    assert position.stopPrice == stopPrice0  # 修改成功后为新值

    # 设置止盈
    order2 = trader.setProfitPrice(position.id, profitPrice=profitPrice1)
    position = ModelPosition.objects.get(id=position.id)
    assert order2.position == position
    assert order2.action == 'setprofit'
    assert order2.state == 'insert'
    assert order2.finishTime is None
    assert order2.profitPrice == profitPrice1
    assert position.profitPrice == profitPrice0

    # 设置止盈失败
    errorId = -1
    errorMsg = u'测试'
    trader.onSetProfitPriceError(order2, errorId, errorMsg, position)
    order2 = ModelOrder.objects.get(id=order2.id)
    position = ModelPosition.objects.get(id=position.id)
    assert order2.state == 'error'
    assert order2.errorId == errorId
    assert order2.errorMsg == errorMsg
    assert order2.finishTime is not None
    assert position.profitPrice == profitPrice0


def test_cancel_order_success():
    """
    测试取消报单并成功
    """
    openLimitPrice = 1000
    trader = Trader()

    # 尝试创建头寸
    toOrder = trader.openPosition(
        instrumentId=getDefaultInstrumentId(),
        direction='buy',
        volume=1,
        openLimitPrice=openLimitPrice
    )

    # 发起撤单请求
    order = trader.cancelOrder(toOrder.id)
    assert order.order == toOrder
    assert order.action == 'cancel'
    assert order.state == 'insert'
    assert order.finishTime is None

    # 发起撤单成功
    trader.onOrderCanceled(order, toOrder)
    toOrder = ModelOrder.objects.get(id=toOrder.id)
    order = ModelOrder.objects.get(id=order.id)
    position = toOrder.position
    assert order.state == 'finish'
    assert order.finishTime is not None
    assert toOrder.state == 'cancel'
    assert toOrder.finishTime is not None
    assert position.state == 'cancel'


def test_cancel_order_fail():
    """
    测试取消报单但失败
    """
    openLimitPrice = 1000
    trader = Trader()

    # 尝试创建头寸
    toOrder = trader.openPosition(
        instrumentId=getDefaultInstrumentId(),
        direction='buy',
        volume=1,
        openLimitPrice=openLimitPrice
    )

    # 发起撤单请求
    order = trader.cancelOrder(toOrder.id)
    assert order.order == toOrder
    assert order.action == 'cancel'
    assert order.state == 'insert'
    assert order.finishTime is None

    # 发起撤单失败
    errorId = -1
    errorMsg = u'测试'
    trader.onCancelOrderError(order, errorId, errorMsg, toOrder)
    toOrder = ModelOrder.objects.get(id=toOrder.id)
    order = ModelOrder.objects.get(id=order.id)
    position = toOrder.position
    assert order.state == 'error'
    assert order.finishTime is not None
    assert order.errorId == errorId
    assert order.errorMsg == errorMsg
    assert toOrder.state in ('insert', 'finish')
    assert position.state in ('preopen', 'open')
