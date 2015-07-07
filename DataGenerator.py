# -*- coding: utf-8 -*-
from __future__ import division
from comhelper import setDjangoEnvironment
setDjangoEnvironment()
from database.models import *

import sys
import json
import zmq
import time
from pyctp.CTPChannel import MdChannel


class DataGenerator(object):
    '''
    数据生成器的基类
    '''

    def  __init__(self,modelDataGenerator):
        '''
        构造函数
        '''
        # 导入数据库配置
        self.modelDataGenerator = modelDataGenerator
        self.broadcastAddress = modelDataGenerator.broadcastAddress
        self.saveRawData = modelDataGenerator.saveRawData
        self.dataCatalog = modelDataGenerator.dataCatalog
        self.instrumentIdList = json.loads(modelDataGenerator.instrumentIdList)
        self.account = modelDataGenerator.account

        # 创建zmq行情发布管道
        context = zmq.Context()
        socket = context.socket(zmq.PUB)
        socket.bind(self.broadcastAddress)
        self.socket = socket

        #
        self.sendMessageCount = 0


    def dataIterator(self):
        '''
        生成数据迭代器
        '''
        raise Exception(u'方法未实现')


    def sendMessage(self,message):
        '''
        发送消息
        '''
        message = [ p.encode('utf-8') if type(p) == unicode else p  for p in message ]
        self.socket.send_multipart(message)
        self.sendMessageCount += 1


    def frameProcess(self,rawMarketData):
        '''
        处理一帧数据
        '''
        # 读取交易品种标识
        instrumentId = rawMarketData['InstrumentID']

        # 读取关键信息报价
        marketData = {}
        marketData['ask'] = rawMarketData['AskPrice1']
        marketData['bid'] = rawMarketData['BidPrice1']
        marketData['askVolume'] = rawMarketData['AskVolume1']
        marketData['bidVolume'] = rawMarketData['BidVolume1']

        # 处理交易时间
        tradingDay = rawMarketData['TradingDay']
        updateTime = rawMarketData['UpdateTime']
        updateMillisec = rawMarketData['UpdateMillisec']
        timeString = "%s %s %6d" % (tradingDay,updateTime,int(updateMillisec)*1000)
        timeFormat = u'%Y%m%d %H:%M:%S %f'
        marketData['timeString'] = timeString
        marketData['timeFormat'] = timeFormat

        # 发送行情广播消息
        # 消息格式:[品种编号(InstrumentID),报价数据(MarketData),棒线数据(BarData),指标数据(IndexData)]
        marketDataJson = json.dumps(marketData)
        message = [instrumentId,marketDataJson,'','']
        self.sendMessage(message)

        # 保存原始行情数据到数据库
        if self.saveRawData == True:
            depthMarketData = ModelDepthMarketData(**rawMarketData)
            depthMarketData.dataCatalog = self.dataCatalog
            depthMarketData.dataTime = datetime.strptime(timeString,timeFormat)
            depthMarketData.save()


    def generate(self):
        '''
        循环生成数据
        '''
        print u'开始生成交易信号...'
        lastSendMessageCount = 0
        t0 = datetime.now()
        for rawMarketData in self.dataIterator():
            self.frameProcess(rawMarketData)
            t1 = datetime.now()
            dt = t1 - t0
            dts = dt.total_seconds()
            if dts >= 1:
                thisSendMessageCount = self.sendMessageCount - lastSendMessageCount
                print u'发送%d条交易信号.' % thisSendMessageCount
                t0 = t1
                lastSendMessageCount = self.sendMessageCount



class CTPChannelGenerator(DataGenerator):
    '''
    从CTP接口读取行情数据并转换成交易信号
    '''

    def dataIterator(self):
        '''
        从CTP接口读取数据
        '''
        # 创建一个CTP MD通道
        mdChannel = MdChannel(
            frontAddress = self.account.mdFrontAddress,
            brokerID = self.account.brokerID,
            userID = self.account.userID,
            password = self.account.password,
            instrumentIdList = self.instrumentIdList
        )

        # 从CTP接口读取数据
        while True:
            rawMarketData = mdChannel.readMarketData()
            if rawMarketData == None:
                continue
            yield rawMarketData.__dict__


class DatabaseGenerator(DataGenerator):
    '''
    从数据库读取数据并转换成交易信号
    '''

    def __init__(self,modelDataGenerator):
        '''
        构造函数
        '''
        super(DatabaseGenerator,self).__init__(modelDataGenerator)
        self.datetimeBegin = modelDataGenerator.datetimeBegin
        self.datetimeEnd = modelDataGenerator.datetimeEnd
        self.interval = modelDataGenerator.interval

    def waitInterval(self):
        '''
        等待时间间隔
        '''
        if self.interval:
            interval = self.interval
        else:
            interval = .5 / len(self.instrumentIdList)
        time.sleep(interval)


    def dataIterator(self):
        '''
        从数据库读取行情数据
        '''
        # 设定数据查询条件
        querySet = ModelDepthMarketData.objects.filter(dataCatalog=self.dataCatalog)
        querySet = querySet.filter(InstrumentID__in=self.instrumentIdList)
        if self.datetimeBegin :
            querySet = querySet.filter(dataTime__gte=self.datetimeBegin)
        if self.datetimeEnd :
            querySet = querySet.filter(dataTime__lt=self.datetimeEnd)
        querySet = querySet.order_by('dataTime')

        for rawMarketData in querySet:
            yield rawMarketData.__dict__
            self.waitInterval()



def main():
    '''
    数据生成器主过程
    参数:
    生成器的id
    '''
    #print sys.argv
    if len(sys.argv) != 2 :
        print '请使用DataGenerator.py <DataGeneratorId> 来启动程序'
        return

    try:
        dataGeneratorId = sys.argv[1]
        dataGenerator = ModelDataGenerator.objects.get(id=dataGeneratorId)
    except:
        print u'所指定的数据生成在不存在'
        return

    dataSource = dataGenerator.dataSource

    if dataSource == 'Channel':
        generator = CTPChannelGenerator(dataGenerator)
        generator.generate()
        return

    if dataSource == 'Database':
        generator = DatabaseGenerator(dataGenerator)
        generator.generate()
        return


if __name__ == '__main__':
    main()
