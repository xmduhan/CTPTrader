#!/usr/bin/env python
# encoding: utf-8

# 初始化django运行环境
from comhelper import setDjangoEnvironment
setDjangoEnvironment()
from database.models import ModelDepthMarketData
import argparse


def readArgments():
    """
    读取命令行参数
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("cmd")


def main():
    """
    """
    # 读取命令行参数
    args = readArgments()
    print args
    print "count=%d" % ModelDepthMarketData.objects.count()


if __name__ == '__main__':
    main()
