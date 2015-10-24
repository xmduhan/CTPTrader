#!/usr/bin/env python
# encoding: utf-8

import os
from trader import CTPTrader
from comhelper import getDefaultInstrumentID
from comhelper import getInstrumentLimitPrice
from time import sleep
from nose.plugins.attrib import attr

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

    global instrumentId, buyLimitPrice, sellLimitPrice
    instrumentId = getDefaultInstrumentID()
    buyLimitPrice, sellLimitPrice = getInstrumentLimitPrice()


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
    trader.openPosition(instrumentId, 'buy', 1)
    for i in range(10):
        if flag:
            break
        sleep(1)
    else:
        assert False
    position = flag[1]

    # 尝试关闭头寸
    flag = []
    trader.closePosition(position.id)
    for i in range(10):
        if flag:
            break
        sleep(1)
    else:
        assert False


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
