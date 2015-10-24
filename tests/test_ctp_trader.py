#!/usr/bin/env python
# encoding: utf-8

import os

frontAddress = None
brokerID = None
userID = None
password = None


def setup():
    """
    测试初始化操作
    """
    global frontAddress, brokerID, userID, password
    frontAddress = os.environ.get('CTP_FRONT_ADDRESS')
    brokerID = os.environ.get('CTP_BROKER_ID')
    userID = os.environ.get('CTP_USER_ID')
    password = os.environ.get('CTP_PASSWORD')
