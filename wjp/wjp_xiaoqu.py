#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：lianjia-beike-spider-master 
@File    ：wjp_xiaoqu.py.py
@Author  ：王金鹏
@Date    ：2024/2/4 16:03 
"""
import datetime

from lib.spider.xiaoqu_spider import *
from wjp.wjp_neighborhood_spider import WjpNeighborhoodSpider


def get_custom_date_string(year, month, day):
    """
    获取自定义日期字符串
    :param year: 年份
    :param month: 月份
    :param day: 日期
    :return: 返回日期字符串，格式为"%Y%m%d"
    """
    custom_date = datetime.datetime(year, month, day)

    return custom_date.strftime("%Y%m%d")


if __name__ == "__main__":
    # spider = XiaoQuBaseSpider(SPIDER_NAME)
    # date = get_custom_date_string(2024, 3, 27)
    spider = WjpNeighborhoodSpider(SPIDER_NAME)
    spider.start()
