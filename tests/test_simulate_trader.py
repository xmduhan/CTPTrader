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

    # 尝试创建头(buy)寸并塞入模拟数据
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
    assert position.openPrice == (100+99) / 2
