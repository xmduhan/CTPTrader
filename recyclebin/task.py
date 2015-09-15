# -*- coding: utf-8 -*-
from comhelper import setDjangoEnvironment
setDjangoEnvironment()
from database.models import *

import os
import sys


def printHelp():
    '''
    在目录上打印帮助信息
    '''
    print u'请使用:python task.py 命令 [参数...] 来启动程序,目前可用命令有:'
    print u'list [DataGenerator|StrategyExecuter|all]: 查看执行中的任务信息'
    print u'... list DataGenerator : 查看所有执行中的数据生成器'
    print u'... list StrategyExecuter : 查看所有执行执行中的策略执器'
    print u'... list all : 查看所有执行执行中的数据生成器和策略执器(注意不含daemon任务)'
    print u'... list : 不加参数是同all参数'
    print u'daemon [start|stop|status] : 守护进程管理'
    print u'... daemon start : 启动守护进程'
    print u'... daemon stop : 停止守护进程'
    print u'... daemon status : 查看守护进程状态'
    print u'... daemon : 不加参数时同status参数'
    print u'DataGenerator [start|stop|list] [id] : 数据生成器进程管理'
    print u'... DataGenerator start id : 启动数据生成器进程(其中id为数据生成器的系统编号,下同)'
    print u'... DataGenerator stop id : 停止数据生成器进程'
    print u'... DataGenerator list : 列出所有可用的数据生成器配置'
    print u'... DataGenerator : 不加参数是同list参数'
    print u'StrategyExecuter [start|stop|list] [id] : 策略执行器进程管理'
    print u'... StrategyExecuter start id : 启动策略执行器进程(其中id为策略执行器的系统编号,下同)'
    print u'... StrategyExecuter stop id : 停止策略执行器进程'
    print u'... StrategyExecuter list : 列出所有可用的策略执行器配置'
    print u'... StrategyExecuter : 不加参数是同list参数'






def main():
    '''  '''
    if len(sys.argv) < 2:
        printHelp()







if __name__ == '__main__' :
    main()
