# -*- coding: utf-8 -*-
import os
import sys
import django


def getProjectPath():
    fullpath = os.path.abspath(__file__)
    return os.path.split(fullpath)[0]


def setDjangoEnvironment():
    '''
    为非django web程序设置执行环境
    '''
    version = float(django.get_version()[:3])

    sys.path.append(getProjectPath())
    os.chdir(getProjectPath())
    settings = "CTPTrader.settings"
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings)
    if version >= 1.7:
        django.setup()
