# -*- coding: utf-8 -*-
import os
import sys
import django
from datetime import datetime
from dateutil.relativedelta import relativedelta


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
