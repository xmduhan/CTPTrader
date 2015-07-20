# -*- coding: utf-8 -*-

import os
import sys
import imp
import json
import zmq
from datetime import datetime

from trader import Trader
from database.models import *

def main():
    '''
    '''
    #print sys.argv
    if len(sys.argv) != 2 :
        print '请使用StrategyExecuter.py <StrategyExecuterId> 来启动程序'
        return

    try:
        StrategyExecuterId = sys.argv[1]
        strategyExecuter = ModelStrategyExecuter.objects.get(id=StrategyExecuterId)
    except:
        print u'所指定的执行器不存在'
        return

    # 导入交易策略模块文件
    sourceFile = os.path.join(strategyExecuter.strategyDir,strategyExecuter.strategyProgram)
    try:
        strategyModule = imp.load_source(sourceFile.split('.')[:1][0], sourceFile)
    except:
        print u'无法加载交易策略'
        return

    # 检查是否实现了onDataArrived函数
    if not hasattr(strategyModule,'onDataArrived'):
        print u'交易策略必须实现onDataArrived方法'
        return
    onDataArrivedVarNames = strategyModule.onDataArrived.func_code.co_varnames

    # 导入交易策略的配置文件
    configFile = os.path.join(strategyExecuter.strategyDir,strategyExecuter.strategyConfig)
    try:
        with open(configFile) as f:
            config = json.load(f)
    except:
        print u'无法读取配置文件'
        return

    # 调用策略模块的初始化方法
    if hasattr(strategyModule,'onInit'):
        try:
            strategyModule.onInit(config)
        except:
            print u'调用策略的初始化方法失败'
            return

    # 导入订阅品种列表
    instrumentIDList = json.loads(strategyExecuter.instrumentIDList)


    # 初始化交易对象
    account = strategyExecuter.account
    try:
        trader = Trader(account,strategyExecuter=strategyExecuter)
    except:
        print u'无法创建交易对象'
        return

    # 读取信号地址,订阅交易信号
    context = zmq.Context()
    socket = context.socket(zmq.SUB)
    socket.connect(strategyExecuter.receiveAddress)
    for instrumentID in instrumentIDList:
        socket.setsockopt(zmq.SUBSCRIBE, instrumentID.encode('utf-8'))

    while True:
        # 接收消息
        messages = socket.recv_multipart()

        # 对接收的数据做简单的格式转化
        data = json.loads(messages[1])
        data['instrumentID'] = messages[0]
        data['dataTime'] = datetime.strptime(data['timeString'],data['timeFormat'])

        # 生成调用函数的参数
        onDataArrivedArgs = {}
        if 'data' in onDataArrivedVarNames:
            onDataArrivedArgs['data'] = data
        if 'trader' in onDataArrivedVarNames:
            onDataArrivedArgs['trader'] = trader

        # 调用onDataArrived
        try:
            strategyModule.onDataArrived(**onDataArrivedArgs)
        except :
            raise
            print u'出现异常...'



if __name__ == '__main__':
    main()


def onInit(config):
    '''
    执行器初始化时调用
    '''
    pass



def onDataArrived(data,trader):
    '''
    执行数据每次接受到数据
    '''
    pass



def onExit(trader):
    '''
    执行器即将退出
    '''
    pass
