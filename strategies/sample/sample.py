# -*- coding: utf-8 -*-

from collections import deque
from pandas import Series

def onInit(config):
    '''
    执行器初始化时调用
    '''
    print config


count = 0
bid0 = 0
bid1 = 0
diffs = deque(maxlen=300)
lastDirection = 0
instrumentID0 = 'IF1508'
instrumentID1 = 'IF1509'


def openPair(trader,instrumentID0,instrumentID1,direction,volume=1):
    '''
    创建对冲头寸
    '''
    if direction not in (1,-1):
        raise Exception(u'无效头寸方向')

    if direction == 1:

        errorId,errorMsg,data = trader.open(instrumentID=instrumentID0,directionCode = 'buy',volume=volume)
        if errorId != 0 :
            print errorId,errorMsg
            raise Exception(u'头寸创建失败')
        print 'openPrice =',data.openPrice

        errorId,errorMsg,data = trader.open(instrumentID=instrumentID1,directionCode = 'sell',volume=volume)
        if errorId != 0 :
            print errorId,errorMsg
            raise Exception(u'头寸创建失败')
        print 'openPrice =',data.openPrice

    if direction == -1:

        errorId,errorMsg,data = trader.open(instrumentID=instrumentID0,directionCode = 'sell',volume=volume)
        if errorId != 0 :
            print errorId,errorMsg
            raise Exception(u'头寸创建失败')
        print 'openPrice =',data.openPrice

        errorId,errorMsg,data = trader.open(instrumentID=instrumentID1,directionCode = 'buy',volume=volume)
        if errorId != 0 :
            print errorId,errorMsg
            raise Exception(u'头寸创建失败')
        print 'openPrice =',data.openPrice



def onDataArrived(data,trader):
    '''
    执行数据每次接受到数据
    '''
    global count,bid0,bid1,diffs,lastDirection

    #count += 1
    #print 'instrumentID =',data['instrumentID'],'count=',count
    #if count == 10:
    #    print 'bid =',data['bid'],'ask =',data['ask']
    #    result = trader.open(instrumentID=data['instrumentID'],directionCode = 'buy',volume=1)
    #    print result
    #    print result[2].openPrice

    #if count in (15,25):
    #    print 'total volume=',trader.getTotalVolume()

    #if count == 20:
    #    trader.closeAll()


    if data['instrumentID'] == instrumentID0:
        bid0 = data['bid']
    if data['instrumentID'] == instrumentID1:
        bid1 = data['bid']

    if bid0 != 0 and bid1 !=0:
        diff = bid1 - bid0
        diffs.append(diff)
        if len(diffs) > 50:
            s = Series(diffs)
            pts = diff - s.mean()
            if abs(pts) > 3 :
                if pts > 0 and lastDirection <= 0:
                    lastDirection = 1
                    print '开仓条件触发,头寸方向:',lastDirection
                    print 'bid0 =',bid0,'bid1 =',bid1,'diff =',diff,'偏离值 =',pts
                    trader.closeAll()
                    openPair(trader,instrumentID0,instrumentID1,lastDirection)
                if pts < 0 and lastDirection >= 0:
                    lastDirection = -1
                    print '开仓条件触发,头寸方向:',lastDirection
                    print 'bid0 =',bid0,'bid1 =',bid1,'diff =',diff,'偏离值 =',pts
                    trader.closeAll()
                    openPair(trader,instrumentID0,instrumentID1,lastDirection)


def onExit(trader):
    '''
    执行器即将退出
    '''
    pass
