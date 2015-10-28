# -*- coding: utf-8 -*-

from comhelper import setDjangoEnvironment
setDjangoEnvironment()
from database.models import *
from trader import Trader


account = None
trader = None

def setup():
    '''
    测试用例的环境初始化
    '''
    global account,trader
    account = ModelAccount.objects.get(id=1)
    trader = Trader(account)

def getDefaultInstrumentId():
    '''
    获得一个保证可以使用的合同代码
    '''
    return datetime.strftime(datetime.now() + relativedelta(months=1),"IF%y%m")


def test01():
    '''
    '''
    trader.openPosition()
