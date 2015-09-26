#!/usr/bin/env python
# encoding: utf-8
from __future__ import division
from trader import SimulateTrader
from comhelper import getDefaultInstrumentID
from database.models import ModelOrder, ModelPosition


def setup():
    """
    """
    pass


def test_open_position():
    """
    测试打开头寸
    """
    trader = SimulateTrader()
    instrumentId = getDefaultInstrumentID()
    ask = 100
    bid = 101

    # 尝试创建头(buy)寸并塞入模拟数据
    order = trader.openPosition(instrumentId, 'buy', 1)
    assert len(trader.openOrderList) == 1
    trader.onDataArrived(instrumentId, ask, bid)
    assert len(trader.openOrderList) == 0

    # 检查头寸是否成功建立
    order = ModelOrder.objects.get(id=order.id)
    position = order.position
    assert order.state == 'finish'
    assert position.state == 'open'
    assert position.openPrice == bid

    # 尝试创建头寸(sell)并塞入模拟数据
    order = trader.openPosition(instrumentId, 'sell', 1)
    assert len(trader.openOrderList) == 1
    trader.onDataArrived(instrumentId, ask, bid)
    assert len(trader.openOrderList) == 0

    # 检查头寸是否成功建立
    order = ModelOrder.objects.get(id=order.id)
    position = order.position
    assert order.state == 'finish'
    assert position.state == 'open'
    assert position.openPrice == ask


def test_open_position_with_limit_price():
    """
    测试使用限价打开头寸
    """
    trader = SimulateTrader()
    instrumentId = getDefaultInstrumentID()

    # 尝试创建头(buy)寸
    order = trader.openPosition(instrumentId, 'buy', 1, openLimitPrice=100)
    # 放入一个不会成交的数据
    assert len(trader.openOrderList) == 1
    trader.onDataArrived(instrumentId, ask=90, bid=105)
    assert len(trader.openOrderList) == 1
    # 确定并没有成交
    order = ModelOrder.objects.get(id=order.id)
    position = order.position
    assert order.state == 'insert'
    assert position.state == 'preopen'
    assert position.openPrice is None

    # 放入一个可以成交的数据
    trader.onDataArrived(instrumentId, ask=90, bid=99)
    # 检查成交情况
    order = ModelOrder.objects.get(id=order.id)
    position = order.position
    assert order.state == 'finish'
    assert position.state == 'open'
    assert position.openPrice == (100 + 99) / 2


def test_close_position():
    """
    测试关闭头寸
    """
    trader = SimulateTrader()
    instrumentId = getDefaultInstrumentID()
    ask = 90
    bid = 95

    # 打开一个头寸以供关闭使用
    order = trader.openPosition(instrumentId, 'buy')
    trader.onDataArrived(instrumentId, ask, bid)
    position = order.position
    assert order.state == 'finish'
    assert position.state == 'open'

    # 尝试关闭头寸
    order = trader.closePosition(position.id)
    assert len(trader.closeOrderList) == 1
    trader.onDataArrived(instrumentId, ask, bid)
    assert len(trader.closeOrderList) == 0
    order = ModelOrder.objects.get(id=order.id)
    position = ModelPosition.objects.get(id=position.id)
    assert order.state=='finish'
    assert position.state == 'close'
    assert position.closePrice == ask


def test_close_position_with_limit_price():
    """
    测试使用限价关闭头寸
    """
    trader = SimulateTrader()
    instrumentId = getDefaultInstrumentID()
    ask = 90
    bid = 95

    # 打开一个头寸以供关闭使用
    order = trader.openPosition(instrumentId, 'buy')
    trader.onDataArrived(instrumentId, ask, bid)
    position = order.position
    assert order.state == 'finish'
    assert position.state == 'open'

    # 尝试使用限价关闭头寸
    order = trader.closePosition(position.id, closeLimitPrice=100)

    # 发出一个不会成交的数据
    trader.onDataArrived(instrumentId, ask=95, bid=105)
    order = ModelOrder.objects.get(id=order.id)
    position = ModelPosition.objects.get(id=position.id)
    assert order.state == 'insert'
    assert position.state == 'preclose'

    # 发出一个可以成交的数据
    trader.onDataArrived(instrumentId, ask=105, bid=110)
    order = ModelOrder.objects.get(id=order.id)
    position = ModelPosition.objects.get(id=position.id)
    assert order.state == 'finish'
    assert position.state == 'close'
    print position.closePrice
    assert position.closePrice == (105 + 100) / 2


def test_cancel_order():
    """
    测试取消挂单
    """
    pass


def test_set_stop_price():
    """
    测试设置止损
    """
    pass


def test_set_profit_price():
    """
    测试设置止盈
    """
    pass


def test_working_thread_running():
    """
    测试工作线程可以正常运行
    """
    pass


