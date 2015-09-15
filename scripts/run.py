#!/usr/bin/env python
# encoding: utf-8


from database.models import ModelDepthMarketData

def run():
    """TODO: Docstring for run.
    :returns: TODO

    """
    count = ModelDepthMarketData.objects.count()
    print "count=%d" % count

