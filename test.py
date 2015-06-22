# -*- coding: utf-8 -*-

from comhelper import setDjangoEnvironment
setDjangoEnvironment()

import os
from pyctp.CTPChannel import MdChannel
from datetime import datetime
from database.models import DepthMarketData
from dateutil.relativedelta import relativedelta


# 读取环境变量
frontAddress = os.environ.get('CTP_FRONT_ADDRESS')
mdFrontAddress = os.environ.get('CTP_MD_FRONT_ADDRESS')
brokerID = os.environ.get('CTP_BROKER_ID')
userID = os.environ.get('CTP_USER_ID')
password = os.environ.get('CTP_PASSWORD')
instrumentID = datetime.strftime(datetime.now() + relativedelta(months=1),"IF%y%m")
#frontAddress,mdFrontAddress,brokerID,userID,password,instrumentID

#
mdChannel = MdChannel(mdFrontAddress,brokerID,userID,password,\
    ['IF1506','IF1507','IF1508','IF1509','IF1510','IF1511','IF1512'])
i = 0
while True:
    result = mdChannel.readMarketData(1000)
    if result:
        DepthMarketData(**result.toDict()).save()
        i += 1
        print u'成功第%d条数据' % i
    else:
        print u'跳过...'
