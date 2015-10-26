#!/usr/bin/env python
# encoding: utf-8

from database.models import ModelTest
from threading import Thread


def test_use_model_in_thread():
    """
    测试在线程中访问django的数据模型
    """
    def thread_function():
        mt = ModelTest()
        mt.a = 1
        mt.save()

    thread = Thread(target=thread_function)
    thread.start()
    thread.join()
