#!/usr/bin/env python
# encoding: utf-8


class Trader(object):

    """
    交易接口类
    """

    def __init__(self):
        """
        TODO: to be defined1.
        """
        pass

    def openPosition(self, instrumentId, direction, volume=1, limitPrice=0, stopPrice=0, profitPrice=0):
        """
        开仓操作
        参数:
            instrumentId 要建仓的交易品种标识
            direction 头寸方向,'buy' 做多,'sell' 做空
            volume 交易数量,默认为1手
            limitPrice 限价单价格,默认为0,表示不限价
            stopPrice 头寸止损价格,默认为0,表示不设置止损
            profitPrice 头寸止盈价格,默认为0,表示不设置止盈
        返回:
            orderId 开仓报单单号
        """
        pass

    def closePostion(self, positionId, limitPrice=0):
        """
        平仓操作
        参数:
            positionId 要平仓的头寸的标识
            limitPrice 平仓限价
        返回:
            orderId 平仓报单单号
        """
        pass

    def cancelPendingOrder(self, orderId):
        """
        取消挂单
        参数:
            orderId 原始挂单报单单号
        返回:
            cancelOrderId 取消单单号
        """
        pass

    def setStopPrice(self, positionId, stopPrice):
        """
        设置头寸的止损线
        参数:
            positionId 对应头寸的标识
            stopPrice 止损价格
        返回:
            orderId 止损修改单单号
        """
        pass

    def listPosition(self, state='open', **kwargs):
        """
        头寸查询
        参数:
            state 头寸状态,默认为'open',默认仅查询目前处于打开状态的头寸
            kwargs 查询条件,django model查询参数格式
        返回:
            positionList 符合查询条件的头寸列表
        """
        pass

    def listPendingOrder(self, state='insert', **kwargs):
        """
        挂单查询
        参数:
            state 报单状态,默认为'insert',默认仅查询哪些处理中的报单
            kwargs 查询条件,django model查询参数格式
        返回:
            pendingOrderList 服务查询条件的挂单列表
        """
        pass

    def onPositionOpened(self, orderId, position):
        """
        头寸建立事件
        参数:
            orderId 创建头寸的原始报单单号,即openPosition的返回值
            position 新创建的头寸的数据实体
        返回:无返回
        """
        pass

    def onPendingOrderCreated(self, orderId, order):
        """
        挂单创建事件
        参数:
            orderId 创建挂单的原始报单单号,即openPosition或closePosition返回值
            order 挂单的数据实体
        返回:无返回
        """
        pass

    def onPostionClosed(self, orderId, position):
        """
        头寸平仓事件
        参数:
            orderId 头寸平仓的原始报单单号,即closePosition的返回值
            position 被平仓的头寸的数据实体
        返回:无返回
        """
        pass

    def onPendingOrderCanceled(self, orderId, order):
        """
        挂单取消成功事件
        参数:
            orderId 发出挂单取消请求的报单单号,即cancelPendingOrder的返回值
            order 被取消的挂单的数据实体
        返回:无返回
        """
        pass

    def onStopPriceSetted(self, orderId, position):
        """
        止损设置成功事件
        参数:
            orderId 发出止损修改的报单单号,即setStopPrice的返回值
            position 被操作影响的头寸数据实体
        返回:无返回
        """
        pass

    def onOpenError(self, orderId, errorId, errorMsg):
        """
        头寸打开出错事件
        参数:
            orderId 创建头寸的原始报单单号,即openPosition的返回值
            errorId 出错代码
            errorMsg 出错提示信息
        返回:无返回
        """
        pass

    def onCloseError(self, orderId, errorId, errorMsg, position=None):
        """
        头寸平仓出错事件
        参数:
            orderId 头寸平仓的原始报单单号,即closePosition的返回值
            errorId 出错代码
            errorMsg 出错提示信息
            position 尝试影响的头寸数据实体
        返回:无返回
        """
        pass

    def onSetStopPriceError(self, orderId, errorId, errorMsg, position=None):
        """
        设置止损出错
        参数:
            orderId 发出止损修改的报单单号,即setStopPrice的返回值
            errorId 出错代码
            errorMsg 出错提示信息
            position 尝试影响的头寸数据实体
        返回:无返回
        """
        pass

    def onCancelPendingOrderError(self, orderId, errorId, errorMsg, order=None):
        """
        取消挂单出错
        参数:
            orderId 发出挂单取消请求的报单单号,即cancelPendingOrder的返回值
            errorId 出错代码
            errorMsg 出错提示信息
            order 尝试影响的挂单的数据实体
        返回:无返回
        """
        pass
