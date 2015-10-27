#!/usr/bin/env python
# encoding: utf-8

import os
from trader import CTPTrader
from comhelper import getDefaultInstrumentID
from comhelper import getInstrumentLimitPrice
from comhelper import waitForResponse
from nose.plugins.attrib import attr
from database.models import ModelOrder, ModelPosition

frontAddress = None
brokerID = None
userID = None
password = None

instrumentId = None
buyLimitPrice = 0
sellLimitPrice = 0


def setup():
    """
    测试初始化操作
    """
    global frontAddress, brokerID, userID, password
    frontAddress = os.environ.get('CTP_FRONT_ADDRESS')
    brokerID = os.environ.get('CTP_BROKER_ID')
    userID = os.environ.get('CTP_USER_ID')
    password = os.environ.get('CTP_PASSWORD')
    assert frontAddress and brokerID and userID and password

    global instrumentId, buyLimitPrice, sellLimitPrice
    instrumentId = getDefaultInstrumentID()
    buyLimitPrice, sellLimitPrice = getInstrumentLimitPrice()


@attr('ctp')
def test_ctp_trader_clean_self():
    """
    测试CTPTrader可以进行对象清理
    """
    trader = CTPTrader(frontAddress, brokerID, userID, password)
    assert trader
    trader = None
    assert False


@attr('ctp')
def test_open_position_and_close():
    """
    测试打开头寸打开头寸并且立马将其关闭
    """
    def onPositionOpened(order, position):
        flag.append([order, position])

    def onPositionClosed(order, position):
        flag.append([order, position])

    trader = CTPTrader(frontAddress, brokerID, userID, password)
    trader.bind('onPositionOpened', onPositionOpened)
    trader.bind('onPositionClosed', onPositionClosed)

    # 尝试打开头寸
    flag = []
    order = trader.openPosition(instrumentId, 'buy', 1)
    position = order.position
    assert order.state == 'insert'
    assert position.state == 'preopen'
    waitForResponse(flag, 5)
    order = ModelOrder.objects.get(id=order.id)
    position = ModelPosition.objects.get(id=position.id)
    assert order.state == 'finish'
    assert position.state == 'open'
    assert position.openPrice
    assert order.openPrice
    print 'position.openPrice =', position.openPrice
    print 'order.openPrice =', order.openPrice

    # 尝试关闭头寸
    flag = []
    order = trader.closePosition(position.id)
    position = ModelPosition.objects.get(id=position.id)
    assert order.state == 'insert'
    assert position.state == 'preclose'
    waitForResponse(flag, 5)
    order = ModelOrder.objects.get(id=order.id)
    position = ModelPosition.objects.get(id=position.id)
    assert order.state == 'finish'
    assert position.state == 'close'
    print 'position.closePrice =', position.closePrice
    print 'order.closePrice =', order.closePrice
    assert position.closePrice
    assert order.closePrice


@attr('ctp')
def test_open_limit_and_cancel():
    """
    测试使用限价单打开头寸并且将其取消
    NOTE: 限价单的成交无法在测试用例中测试,而且实际也没有必要
    """
    assert False


@attr('ctp')
def test_open_position_with_stop_price():
    """
    打开头寸的同时使用止损价格,并触发止损价格使头寸关闭
    NOTE: CTP似乎不支持止损价格,这里是CTPTrader接口模拟的
    """
    assert False


@attr('ctp')
def test_open_posotion_with_profit_price():
    """
    打开头寸的同时使用止盈价,并触发止盈使头寸关闭
    """
    assert False


@attr('ctp')
def test_set_stop_price():
    """
    测试设置止损价格,并且使器触发
    """
    assert False


@attr('ctp')
def test_set_profit_price():
    """
    测试设置止盈价格并使其触发
    """
    assert False
