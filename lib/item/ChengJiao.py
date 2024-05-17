#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：lianjia-beike-spider-master 
@File    ：ChengJiao.py
@Author  ：王金鹏
@Date    ：2024/3/28 15:48 
"""

class ChengJiao(object):
    def __init__(self, district,area, title, deal_date, total_price, unit_price, list_price,list_unit_price,house_info):
        self.area = area
        self.list_price = list_price
        self.unit_price = unit_price
        self.total_price = total_price
        self.deal_date = deal_date
        self.title = title
        self.district = district
        self.list_unit_price = list_unit_price
        self.house_info = house_info

    def text(self):
        return str(self.district) + "," + \
            str(self.area) + "," + \
            self.title + "," + \
            self.house_info + "," + \
            self.deal_date + "," + \
            self.total_price + "," + \
            self.unit_price + "," + \
            str(self.list_price) + "," + \
            str(self.list_unit_price)
