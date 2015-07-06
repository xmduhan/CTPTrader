# -*- coding: utf-8 -*-
from comhelper import setDjangoEnvironment
setDjangoEnvironment()
from database.models import *

import sys
import json
import zmq
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


    def dataIterator():
        '''
        生成数据迭代器
        '''
        raise Exception(u'方法未实现')


    def sendMessage(message):
        '''
        发送消息
        '''
        self.socket.send_multipart(message)


    def frameProcess(rawMarketData):
        '''
        处理一帧数据
        '''
        # 读取交易品种标识
        instrumentId = rawMarketData['InstrumentId']

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
        timeString = "%s %s %6id" % (tradingDay,updateTime,int(updateMillisec)*1000)
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


    def generate():
        '''
        循环生成数据
        '''
        for rawMarketData in dataIterator():
            self.frameProcess(rawMarketData)




class CTPChannelGenerator(DataGenerator):
    '''
    从CTP接口读取行情数据并转换成交易信号
    '''

    def dataIterator():
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
            yield rawMarketData


class DatabaseGenerator(DataGenerator):
    '''
    从数据库读取数据并转换成交易信号
    '''

    def __init__(self,modelDataGenerator):
        '''
        构造函数
        '''
        super(DataGenerator,self).__init__()
        self.datetimeBegin = modelDataGenerator.datetimeBegin
        self.datatimeEnd = modelDataGenerator.datetimeEnd

    def dataIterator():
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

        for rawMarketData in querySet:
            yield rawMarketData.__dict__




def generateFromCTPChannel(dataGenerator):
    '''
    从CTP接口读取行情数据并转换成交易信号

    '''

    #读取账户信息
    account = dataGenerator.account
    saveRawData = dataGenerator.saveRawData
    dataCatalog = dataGenerator.dataCatalog

    # 读取要订阅的品种列表
    instrumentIdList = json.loads(dataGenerator.instrumentIdList)

    print '-----1--------'
    print 'account.mdFrontAddress =',account.mdFrontAddress
    print 'account.brokerID =',account.brokerID
    print 'account.userID =',account.userID
    print 'account.password =',account.password
    print 'instrumentIdList =',instrumentIdList

    # 创建一个CTP MD通道
    mdChannel = MdChannel(
        frontAddress = account.mdFrontAddress,
        brokerID = account.brokerID,
        userID = account.userID,
        password = account.password,
        instrumentIdList = instrumentIdList
    )

    print '------2------'

    # 创建zmq行情发布管道
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind(dataGenerator.broadcastAddress)


    # 循环读取报价信息
    while True:
        rawMarketData = mdChannel.readMarketData()
        #print data

        # 读取交易品种标识
        instrumentId = rawMarketData['InstrumentId']

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
        timeString = "%s %s %6id" % (tradingDay,updateTime,int(updateMillisec)*1000)
        timeFormat = u'%Y%m%d %H:%M:%S %f'
        marketData['timeString'] = timeString
        marketData['timeFormat'] = timeFormat

        # 发送行情广播消息
        # 消息格式:[品种编号(InstrumentID),报价数据(MarketData),棒线数据(BarData),指标数据(IndexData)]
        marketDataJson = json.dumps(marketData)
        message = [instrumentId,marketDataJson,'','']
        socket.send_multipart(message)

        # 保存原始行情数据到数据库
        if saveRawData == True:
            depthMarketData.dataCatalog = dataCatalog
            depthMarketData.dataTime = datetime.strptime(timeString,timeFormat)
            depthMarketData = ModelDepthMarketData(**rawMarketData)
            depthMarketData.save()



def generateFromDatabase(dataGenerator):
    '''
    从数据读取原始行情数据并转换成交易信号
    '''

    # 创建zmq行情发布管道
    context = zmq.Context()
    socket = context.socket(zmq.PUB)
    socket.bind(dataGenerator.broadcastAddress)

    # 设定数据查询条件
    instrumentIdList = dataGenerator.instrumentIdList
    datetimeBegin = dataGenerator.datetimeBegin
    datetimeEnd = dataGenerator.datetimeEnd
    dataCatalog = dataGenerator.dataCatalog
    querySet = ModelDepthMarketData.objects.filter(dataCatalog=dataCatalog)
    querySet = querySet.filter(InstrumentID__in=instrumentIdList)
    if datetimeBegin :
        querySet = querySet.filter(dataTime__gte=datetimeBegin)
    if datetimeEnd :
        querySet = querySet.filter(dataTime__lt=datetimeEnd)

    # 循环读取并处理数据库数据
    for rawMarketData in querySet:
        pass






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
        generateFromCTPChannel(dataGenerator)

    elif dataSource == 'Database':
        generateFromDatabase(dataGenerator)

    else:
        raise Exception(u'未知数据源类型')




if __name__ == '__main__':
    main()
