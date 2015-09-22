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
    trader = Trader()

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


def test_open_position_error():
    """
    测试打开头寸出错的情况
    """
    trader = Trader()
    # 尝试打开头寸的报单
    order = trader.openPosition(getDefaultInstrumentID(), 'buy', 1)
    position = order.position

    # 模拟打开头寸出错的情况
    errorId = -1
    errorMsg = u'测试'
    trader.onOpenError(order, errorId, errorMsg, position)
    assert order.state == 'error'
    assert order.errorId == errorId
    assert order.errorMsg == errorMsg
    assert position.state == 'error'


def test_close_position():
    """
    测试关闭头寸
    """
    trader = Trader()
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
    assert closeOrder.closeLimitPrice is None
    assert position.state == 'preclose'
    assert position.closeTime is None
    assert position.closeLimitPrice == 0

    # 模拟头寸正常关闭事件
    trader.onPostionClosed(closeOrder, position)
    assert closeOrder.state == 'finish'
    assert closeOrder.finishTime is not None
    assert position.state == 'close'
    assert position.closeTime is None

    # NOTE: 因为trader还为实现议价机制,所以此时价格仍为空
    assert position.closePrice is None
    assert closeOrder.closePrice is None

