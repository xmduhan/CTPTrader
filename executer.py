#!/usr/bin/env python
# encoding: utf-8

from database.models import ModelStrategyExecuter
from trader import Trader


def bind(event):
    """
    事件绑定的修饰器
    使用场景: 在策略文件中使用
    例子:
    @bind('onPositionOpened')
    def onPositionOpened(...):
        ... ...
    """
    def func_maker(fun):
        if hasattr(fun, 'bindTo'):
            fun.bindTo.append(event)
        else:
            fun.bindTo = [event]
        return fun
    return func_maker


class StrategyExecuter(object):
    """
    策略执行器
    """

    def __init__(self, code):
        """
        初始化操作
        """
        # 读取策略执行器的实体信息
        self.modelStrategyExecuter = ModelStrategyExecuter.objects.get(code=code)
        # 初始化交易接口
        # TODO: 要使用对应的交易结果配置,而不是使用Trader
        self.trader = Trader(self.modelStrategyExecuter)

    def run(self):
        """
        执行器开始执行
        """
        pass

    def step(self):
        """
        执行器单步执行
        NOTE: 目前还不知到这个方法是否有意义，或者是否能实现，暂时先放在这里，之后再考虑
        """
        pass
