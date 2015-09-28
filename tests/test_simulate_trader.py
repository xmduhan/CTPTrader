#!/usr/bin/env python
# encoding: utf-8
from __future__ import division
from trader import SimulateTrader
from comhelper import getDefaultInstrumentID
from database.models import ModelOrder, ModelPosition, ModelStrategyExecuter, ModelDataGenerator
import error


modelStrategyExecuter = ModelStrategyExecuter()
modelDataGenerator = ModelDataGenerator()

def setup():
    """
    创建测试需要的数据
    """
    global modelStrategyExecuter, modelDataGenerator
    # 创建一个测试使用的数据生成器
    modelDataGenerator.code = 'TestGenerator1'
    modelDataGenerator.name = u'测试数据生成器1'
    modelDataGenerator.dataSource = 'database'
    modelDataGenerator.instrumentIdList = '["%s"]' % getDefaultInstrumentID()
    modelDataGenerator.save()

    # 创建一个测试使用的策略执行器
    modelStrategyExecuter.code = 'TestExecuter1'
    modelStrategyExecuter.name = u'测试执行器1'
    modelStrategyExecuter.dataGenerator = modelDataGenerator
    modelStrategyExecuter.instrumentIdList = '["%s"]' % getDefaultInstrumentID()
    modelStrategyExecuter.traderClass = 'SimulateTrader'
    modelStrategyExecuter.save()


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
    assert len(trader.getOrderList(action='open', state='insert')) == 1
    trader.onDataArrived(instrumentId, ask, bid)
    assert len(trader.getOrderList(action='open', state='insert')) == 0

    # 检查头寸是否成功建立
    order = ModelOrder.objects.get(id=order.id)
    position = order.position
    assert order.state == 'finish'
    assert position.state == 'open'
    assert position.openPrice == bid

    # 尝试创建头寸(sell)并塞入模拟数据
    order = trader.openPosition(instrumentId, 'sell', 1)
    assert len(trader.getOrderList(action='open', state='insert')) == 1
    trader.onDataArrived(instrumentId, ask, bid)
    assert len(trader.getOrderList(action='open', state='insert')) == 0

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
    assert len(trader.getOrderList(action='open', state='insert')) == 1
    trader.onDataArrived(instrumentId, ask=90, bid=105)
    assert len(trader.getOrderList(action='open', state='insert')) == 1
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
    order = ModelOrder.objects.get(id=order.id)
    position = order.position
    assert order.state == 'finish'
    assert position.state == 'open'

    # 尝试关闭头寸
    order = trader.closePosition(position.id)
    assert len(trader.getOrderList(action='close', state='insert')) == 1
    trader.onDataArrived(instrumentId, ask, bid)
    assert len(trader.getOrderList(action='clsoe', state='insert')) == 0
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
    order = ModelOrder.objects.get(id=order.id)
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
    assert position.closePrice == (105 + 100) / 2


def test_cancel_order():
    """
    测试取消挂单
    """
    trader = SimulateTrader()
    instrumentId = getDefaultInstrumentID()

    # 创建一个挂单供撤单使用
    order = trader.openPosition(instrumentId, 'buy', openLimitPrice=100)
    position = order.position
    assert order.state == 'insert'
    assert position.state == 'preopen'
    assert len(trader.getOrderList(action='open', state='insert')) == 1

    # 发出一个不会成交的价格
    trader.onDataArrived(instrumentId, ask=105, bid=110)
    order = ModelOrder.objects.get(id=order.id)
    position = ModelPosition.objects.get(id=position.id)
    assert order.state == 'insert'
    assert position.state == 'preopen'

    # 发出撤单请求
    cancelOrder = trader.cancelOrder(order.id)
    assert len(trader.getOrderList(action='cancel', state='insert')) == 1
    trader.onDataArrived(instrumentId, ask=105, bid=110)
    order = ModelOrder.objects.get(id=order.id)
    position = ModelPosition.objects.get(id=position.id)
    cancelOrder = ModelOrder.objects.get(id=cancelOrder.id)
    assert len(trader.getOrderList(action='open', state='insert')) == 0
    assert len(trader.getOrderList(action='cancel', state='insert')) == 0
    assert order.state == 'cancel'
    assert position.state == 'cancel'
    assert cancelOrder.state == 'finish'

    # 发出一个原本可以成交的价格
    trader.onDataArrived(instrumentId, ask=90, bid=95)
    order = ModelOrder.objects.get(id=order.id)
    position = ModelPosition.objects.get(id=position.id)
    assert order.state == 'cancel'
    assert position.state == 'cancel'
    assert cancelOrder.state == 'finish'

    # 再次尝试对已完成的单进行撤单
    cancelOrder = trader.cancelOrder(order.id)
    assert len(trader.getOrderList(action='cancel', state='insert')) == 1
    trader.onDataArrived(instrumentId, ask=105, bid=110)
    cancelOrder = ModelOrder.objects.get(id=cancelOrder.id)
    order = ModelOrder.objects.get(id=order.id)
    position = ModelPosition.objects.get(id=position.id)
    assert len(trader.getOrderList(action='cancel', state='insert')) == 0
    assert cancelOrder.state == 'error'
    errorId, errorMsg = error.OrderNoActive
    assert cancelOrder.errorId == errorId
    assert cancelOrder.errorMsg == errorMsg


def test_open_position_with_stop_price():
    """
    测试设置止损
    """
    trader = SimulateTrader()
    instrumentId = getDefaultInstrumentID()
    stopPrice = 90

    # 创建一个头寸并设置了止损
    order = trader.openPosition(instrumentId, 'buy', stopPrice=stopPrice)
    trader.onDataArrived(instrumentId, ask=100, bid=101)
    order = ModelOrder.objects.get(id=order.id)
    position = order.position
    assert order.state == 'finish'
    assert position.state == 'open'
    assert position.stopPrice == stopPrice

    # 发出一个会触发止损的价格
    trader.onDataArrived(instrumentId, ask=80, bid=85)
    position = ModelPosition.objects.get(id=position.id)
    assert position.state == 'close'
    assert position.closePrice == 80


def test_open_position_with_profit_price():
    """
    测试打开头寸的时候同时设置止盈信息
    """
    trader = SimulateTrader()
    instrumentId = getDefaultInstrumentID()
    profitPrice = 110
    # 创建一个头寸并设置了止盈
    order = trader.openPosition(instrumentId, 'buy', profitPrice=profitPrice)
    trader.onDataArrived(instrumentId, ask=100, bid=101)
    order = ModelOrder.objects.get(id=order.id)
    position = order.position
    assert order.state == 'finish'
    assert position.state == 'open'
    assert position.profitPrice == profitPrice

    # 发出一个会触发止盈的价格
    trader.onDataArrived(instrumentId, ask=110, bid=115)
    position = ModelPosition.objects.get(id=position.id)
    assert position.state == 'close'
    assert position.closePrice == 110


def test_set_stop_price():
    """
    测试设置止盈
    """
    trader = SimulateTrader()
    instrumentId = getDefaultInstrumentID()

    # 创建一个头寸
    order = trader.openPosition(instrumentId, 'sell')
    trader.onDataArrived(instrumentId, ask=100, bid=105)
    order = ModelOrder.objects.get(id=order.id)
    position = order.position
    assert order.state == 'finish'
    assert position.state == 'open'
    assert position.profitPrice == 0

    # 发出一个高价,但无设置止损,头寸不会关闭
    trader.onDataArrived(instrumentId, ask=110, bid=115)
    position = ModelPosition.objects.get(id=position.id)
    assert position.state == 'open'

    # 设置止损价格,并触发价格
    trader.setStopPrice(position.id, 115)
    trader.onDataArrived(instrumentId, ask=110, bid=115)
    position = ModelPosition.objects.get(id=position.id)
    assert position.state == 'close'
    assert position.closePrice == 115


def test_set_profit_price():
    """
    测试设置止盈
    """
    trader = SimulateTrader()
    instrumentId = getDefaultInstrumentID()

    # 创建一个头寸
    order = trader.openPosition(instrumentId, 'sell')
    trader.onDataArrived(instrumentId, ask=100, bid=105)
    order = ModelOrder.objects.get(id=order.id)
    position = order.position
    assert order.state == 'finish'
    assert position.state == 'open'
    assert position.profitPrice == 0

    # 发出一个低价,但没有设置止盈,头寸不会关闭
    trader.onDataArrived(instrumentId, ask=80, bid=85)
    position = ModelPosition.objects.get(id=position.id)
    assert position.state == 'open'

    # 设置止盈价格,并触发价格
    trader.setProfitPrice(position.id, 85)
    trader.onDataArrived(instrumentId, ask=80, bid=85)
    position = ModelPosition.objects.get(id=position.id)
    assert position.state == 'close'
    assert position.closePrice == 85


def test_working_thread_running():
    """
    测试工作线程可以正常运行
    """
    global modelStrategyExecuter, modelDataGenerator

    trader = SimulateTrader(modelStrategyExecuter)
    instrumentId = getDefaultInstrumentID()

    # 启动工作线程
    trader.start()
    try:
        pass
    finally:
        # 停止工作线程
        trader.stop()



