# -*- coding: utf-8 -*-
import os
import sys
import django
import threading
import uuid


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


class CallbackManager(object):
    """
    回调数据链管理
    """

    def __init__(self):
        """
        构造函数
        """
        # 初始化回调数据链
        self.__callbackDict = {}
        self.__callbackUuidDict = {}
        self.__callbackLock = threading.RLock()

    def bind(self, callbackName, funcToCall):
        """
        绑定回调函数
        参数:
        callbackName  回调函数名称
        funcToCall  需要绑定的回调函数，可以是函数也可以是实例方法
        返回值:
        如果绑定成功方法返回一个bindId,这个id可以用于解除绑定(unbind)时使用
        """
        self.__callbackLock.acquire()
        try:
            callbackUuid = uuid.uuid1()
            self.__callbackUuidDict[callbackUuid] = {
                'callbackName': callbackName,
                'funcToCall': funcToCall
            }
            if callbackName in self.__callbackDict.keys():
                self.__callbackDict[callbackName].append(callbackUuid)
            else:
                self.__callbackDict[callbackName] = [callbackUuid]
            return callbackUuid
        finally:
            self.__callbackLock.release()

    def unbind(self, bindId):
        """
        解除回调函数的绑定
        参数:
        bindId 绑定回调函数时的返回值
        返回值:
        成功返回True，失败(或没有找到绑定项)返回False
        """
        self.__callbackLock.acquire()
        try:
            if bindId not in self.__callbackUuidDict.keys():
                return False
            callbackName = self.__callbackUuidDict[bindId]['callbackName']
            self.__callbackDict[callbackName].remove(bindId)
            self.__callbackUuidDict.pop(bindId)
            return True
        finally:
            self.__callbackLock.release()

    def callback(self, callbackName, args):
        """
        根据回调链调用已经绑定的所有回调函数
        参数:
        callbackName  回调函数名称
        args 用于传递给回调函数的参数(字典结构)
        返回值:
        无
        """
        self.__callbackLock.acquire()
        try:
            if callbackName not in self.__callbackDict.keys():
                return
            for callbackUuid in self.__callbackDict[callbackName]:
                funcToCall = self.__callbackUuidDict[callbackUuid]['funcToCall']
                try:
                    funcToCall(**args)
                except Exception as e:
                    print e
        finally:
            self.__callbackLock.release()
