#!/usr/bin/env python
# encoding: utf-8

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

