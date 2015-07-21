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
ask0 = 0
ask1 = 0
diffs = deque(maxlen=400)
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
        price0 = data.openPrice
        print 'i0:做多:openPrice =',data.openPrice

        errorId,errorMsg,data = trader.open(instrumentID=instrumentID1,directionCode = 'sell',volume=volume)
        if errorId != 0 :
            print errorId,errorMsg
            raise Exception(u'头寸创建失败')
        print 'i1:做空:openPrice =',data.openPrice
        price1 = data.openPrice

        return price0,price1

    if direction == -1:

        errorId,errorMsg,data = trader.open(instrumentID=instrumentID1,directionCode = 'buy',volume=volume)
        if errorId != 0 :
            print errorId,errorMsg
            raise Exception(u'头寸创建失败')
        print 'i1:做多:openPrice =',data.openPrice
        price1 = data.openPrice

        errorId,errorMsg,data = trader.open(instrumentID=instrumentID0,directionCode = 'sell',volume=volume)
        if errorId != 0 :
            print errorId,errorMsg
            raise Exception(u'头寸创建失败')
        print 'i0:做空:openPrice =',data.openPrice
        price0 = data.openPrice



def onDataArrived(data,trader):
    '''
    执行数据每次接收到数据
    '''
    global count,bid0,bid1,ask0,ask1,diffs,lastDirection

    count += 1
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
        ask0 = data['ask']
    if data['instrumentID'] == instrumentID1:
        bid1 = data['bid']
        ask1 = data['ask']

    if bid0 != 0 and bid1 !=0:
        diff = bid1 - bid0
        diffs.append(diff)
        if len(diffs) > 350:
            s = Series(diffs)
            pts = diff - s.mean()
            if abs(pts) > 3 :
                if pts > 0 and lastDirection <= 0:
                    lastDirection = 1
                    print '开仓条件触发,头寸方向:',lastDirection
                    print 'bid0 =',bid0,'bid1 =',bid1,'ask0 =',ask0,'ask1 =',ask1
                    print 'diff =',diff,'偏离值 =',pts
                    trader.closeAll()
                    price0,price1=openPair(trader,instrumentID0,instrumentID1,lastDirection)
                    print '实际价差 =',price1-price0-s.mean()
                    print '买盘滑点 =',price0-bid0
                    print '卖盘滑点 =',ask1-price1
                if pts < 0 and lastDirection >= 0:
                    lastDirection = -1
                    print '开仓条件触发,头寸方向:',lastDirection
                    print 'bid0 =',bid0,'bid1 =',bid1,'ask0 =',ask0,'ask1 =',ask1
                    print 'diff =',diff,'偏离值 =',pts
                    trader.closeAll()
                    openPair(trader,instrumentID0,instrumentID1,lastDirection)
                    print '实际价差 =',price0-price1-s.mean()
                    print '买盘滑点 =',price1-bid1
                    print '卖盘滑点 =',ask0-price0
            else:
                if count % 30 == 0 :
                    print '平均点差 =',s.mean(),'diff =',diff,'偏离值 =',pts

def onExit(trader):
    '''
    执行器即将退出
    '''
    pass
