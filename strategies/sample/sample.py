# -*- coding: utf-8 -*-



def onInit(config):
    '''
    执行器初始化时调用
    '''
    print config



def onDataArrived(data,trader):
    '''
    执行数据每次接受到数据
    '''
    print data,trader



def onExit(trader):
    '''
    执行器即将退出
    '''
    pass
