#!/usr/bin/env python
# encoding: utf-8

from trader import Trader
from comhelper import getDefaultInstrumentID
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
    order = trader.openPosition(getDefaultInstrumentID(), 'buy', 1)
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
    order = trader.openPosition(getDefaultInstrumentID(), 'buy', 1)
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
    openOrder = trader.openPosition(getDefaultInstrumentID(), 'buy', 1)
    position = openOrder.position
    trader.onPositionOpened(openOrder, position)
    assert position.state == 'open'

    # 测试头寸关闭操作
    closeOrder = trader.closePostion(position.id)
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
    openOrder = trader.openPosition(getDefaultInstrumentID(), 'buy', 1)
    position = openOrder.position
    trader.onPositionOpened(openOrder, position)
    assert position.state == 'open'
    closeOrder = trader.closePostion(position.id)
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
