#!/usr/bin/env python
# encoding: utf-8

from database.models import ModelTest
from threading import Thread


def test_use_model_in_thread():
    """
    测试在线程中访问django的数据模型
    """
    def thread_function():
        ModelTest(a=1).save()

    thread = Thread(target=thread_function)
    thread.start()
    thread.join()


def test_use_model_in_parallel_busy_thread():
    """
    测试在两个线程中频繁的使用数据库操作
    """
    count = ModelTest.objects.count()

    def thread_function():
        for i in range(100):
            ModelTest(a=1).save()

    thread1 = Thread(target=thread_function)
    thread2 = Thread(target=thread_function)
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    assert ModelTest.objects.count() - count ==200
