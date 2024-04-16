#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
爬虫基类
爬虫名常量，用来设置爬取哪个站点

@Project ：lianjia-beike-spider-master 
@File    ：wjp_base_spider.py
@Author  ：王金鹏
@Date    ：2024/1/12 10:48 
"""
import random
import threading
import time

from lib.utility.date import get_date_string
from lib.zone.city import lianjia_cities, beike_cities


THREAD_POOL_SIZE = 50  # 线程数

# 防止爬虫被禁，随机延迟设定
# 如果不想delay，就设定False，
# 具体时间可以修改random_delay()，由于多线程，建议数值大于10
RANDOM_DELAY = False
LIANJIA_SPIDER = "lianjia"
BK_SPIDER = "ke"
SPIDER_NAME = BK_SPIDER  # 默认爬虫选择贝壳

class WjpBaseSpider(object):
    @staticmethod
    def rand_delay():
        if RANDOM_DELAY:
            time.sleep(random.randint(0, 16))


    def __init__(self, name):
        """
        根据爬虫名称和日期初始化类
        @param name: 爬虫名称
        @param date: 爬取日期
        """
        # 爬虫名称（贝壳 or 链家）
        self.name = name
        if self.name == LIANJIA_SPIDER:
            self.cities = lianjia_cities
        elif self.name == BK_SPIDER:
            self.cities = beike_cities
        else:
            self.cities = None
        # 准备日期信息，爬到的数据存放在日期相关的文件夹下面
        # self.date_string = date
        self.date_string = get_date_string()
        print('当前爬取的日期为: {0}'.format(self.date_string))
        # 小区总数，用于统计
        self.total_neighborhood_num = 0
        print('爬取的小区总数为: %s', self.total_neighborhood_num)
        # 创建互斥锁
        self.mutex = threading.Lock()

    def create_prompt_text(self):
        """
        根据已有城市中英文对照表拼接选择提示信息
        @return: 拼接好的字符串
        """
        city_info = list()
        count = 0
        for en_name, ch_name in self.cities.items():
            count += 1
            city_info.append(en_name)
            city_info.append(": ")
            city_info.append(ch_name)
            if count % 4 == 0:
                city_info.append("\n")
            else:
                city_info.append(", ")
        return "你想要爬取哪个城市的房价呢？\n" + city_info

    def get_chinese_city(self, en):
        """
        拼音名转中文城市名
        @param en: 拼音
        @return: 中文
        """
        return self.cities.get(en, None)





