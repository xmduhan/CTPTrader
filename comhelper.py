# -*- coding: utf-8 -*-
import os
import sys
import django
from datetime import datetime
from dateutil.relativedelta import relativedelta
from time import sleep


def getProjectPath():
    """
    获取目的根目录
    """
    fullpath = os.path.abspath(__file__)
    return os.path.split(fullpath)[0]


def setDjangoEnvironment():
    '''
    为非web程序设置django的执行环境
    '''
    version = float(django.get_version()[:3])

    sys.path.append(getProjectPath())
    os.chdir(getProjectPath())
    settings = "CTPTrader.settings"
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings)
    if version >= 1.7:
        django.setup()


def getDefaultInstrumentID(months=1):
    """
    获取一个可用的交易品种ID
    """
    return datetime.strftime(datetime.now() + relativedelta(months=months), "IF%y%m")


def getInstrumentLimitPrice():
    """
    获取品种的最高和最低限价
    """
    return 0, 0


def orderId2Ref(orderId):
    """
    将orderId转化为CTP接口的orderRef
    orderId
    返回 CTP接口要求的orderRef
    """
    return ('%12d' % orderId).replace(' ', '0')


def wait(expr, second=5):
    """
    等待服务器响应
    expr 一个lambda表达式，如果表达式执行返回True则退出循环
    second 等待的时间，单位:秒
    """
    t0 = datetime.now()
    t1 = t0
    toWaitOnce = .01
    while (t1 - t0).total_seconds() < second:
        if expr():
            break
        sleep(toWaitOnce)
        t1 = datetime.now()
    else:
        raise Exception('等待超时')
