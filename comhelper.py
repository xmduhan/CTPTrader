# -*- coding: utf-8 -*-
import os
import sys


def getProjectPath():
    fullpath = os.path.abspath(__file__)
    return os.path.split(fullpath)[0]

def setDjangoEnvironment():
    sys.path.append(getProjectPath())
    os.chdir(getProjectPath())
    settings = "CTPTrader.settings"
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", settings)
