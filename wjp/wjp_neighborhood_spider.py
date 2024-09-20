#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：lianjia-beike-spider-master
@File    ：wjp_neighborhood_spider.py
@Author  ：王金鹏
@Date    ：2024/1/12 10:26
"""
import re

import threadpool
from bs4 import BeautifulSoup

from lib.item.xiaoqu import XiaoQu
from lib.utility.path import create_date_path
from lib.zone import area
from lib.utility.date import *
from lib.zone.area import get_areas
from lib.zone.city import get_city
from lib.zone.district import *
from wjp.wjp_base_spider import *


class WjpNeighborhoodSpider(WjpBaseSpider):

    def collect_subdistrict_neighborhood_data(self, city_name, subdistrict_name, fmt="csv"):
        """
        对于每个板块,获得这个板块下所有小区的信息
        并且将这些信息写入文件保存
        @param city_name: 城市
        @param subdistrict_name: 板块
        @param fmt: 保存文件格式
        @return: None
        """
        district_name = area_dict.get(subdistrict_name, "") # 根据 街道/镇 获取 行政区名（example: 闵行区）
        csv_file = self.date_path + "/{0}_{1}.csv".format(district_name, subdistrict_name)
        with open(csv_file, "w", encoding='utf-8-sig') as f:
            # 开始获得所选板块的小区数据
            nbs = self.get_neighborhood_info(city_name, subdistrict_name)
            # 锁定
            if self.mutex.acquire(1):
                self.total_neighborhood_num += len(nbs)
                # 释放
                self.mutex.release()
            if fmt == "csv":
                for neighborhood in nbs:
                    f.write(self.date_string + ',' + neighborhood.text() + '\n')
        print("爬取任务完成, 板块名称：" + subdistrict_name, '保存在：' + csv_file)

    @staticmethod
    def get_neighborhood_info(city, subdistrict):
        total_page = 1
        district = area_dict.get(subdistrict, "")
        chinese_district = get_chinese_district(district)
        chinese_subdistrict = chinese_area_dict.get(subdistrict, "")
        neighborhood_list = list()
        page = 'https://{0}.{1}.com/xiaoqu/{2}/'.format(city, SPIDER_NAME, subdistrict)
        print(page)
        # 开始准备网络请求
        headers = create_headers()
        response = requests.get(page, timeout=10, headers=headers)
        html = response.content
        soup = BeautifulSoup(html, "lxml")

        try:
            page_box = soup.find_all('div', class_='page-box')[0]
            matches = re.search('.*"totalPage":(\d+),.*', str(page_box))
            total_page = int(matches.group(1))
        except Exception as e:
            print("\tWarning: only find one page for {0}".format(subdistrict))
            print(e)
        # 从第一页开始,一直遍历到最后一页
        for i in range(1, total_page + 1):
            headers = create_headers()
            page = 'https://{0}.{1}.com/xiaoqu/{2}/pg{3}'.format(city, SPIDER_NAME, subdistrict, i)
            print(page)  # 打印版块页面地址
            WjpBaseSpider.rand_delay()
            response = requests.get(page, timeout=10, headers=headers)
            html = response.content
            soup = BeautifulSoup(html, "lxml")

            # 获得有小区信息的panel
            house_elems = soup.find_all('li', class_="xiaoquListItem")
            for house_elem in house_elems:
                price = house_elem.find('div', class_="totalPrice")
                name = house_elem.find('div', class_='title')
                on_sale = house_elem.find('div', class_="xiaoquListItemSellCount")

                # 继续清理数据
                price = price.text.strip()
                name = name.text.replace("\n", "")
                on_sale = on_sale.text.replace("\n", "").strip()

                # 作为对象保存
                xiaoqu = XiaoQu(chinese_district, chinese_subdistrict, name, price, on_sale)
                neighborhood_list.append(xiaoqu)
        return neighborhood_list
    def start(self):
        city = get_city()
        self.date_path = create_date_path("{0}/xiaoqu".format(SPIDER_NAME), city, self.date_string)
        t1 = time.time()  # 开始计时

        # 获得城市有多少区列表, district: 区县
        districts = get_districts(city)
        print('City: {0}'.format(city))
        print('Districts: {0}'.format(districts))

        # 获得每个区的板块, area: 板块
        areas = list()
        for district in districts:
            WjpBaseSpider.rand_delay()
            areas_of_district = get_areas(city, district)
            print('{0}: Area list:  {1}'.format(district, areas_of_district))
            # 用list的extend方法,L1.extend(L2)，该方法将参数L2的全部元素添加到L1的尾部
            areas.extend(areas_of_district)
            # 使用一个字典来存储区县和板块的对应关系, 例如{'beicai': 'pudongxinqu', }
            for area in areas_of_district:
                area_dict[area] = district
        print("Area:", areas)
        print("District and areas:", area_dict)

        # 准备线程池用到的参数
        nones = [None for i in range(len(areas))]
        city_list = [city for i in range(len(areas))]
        args = zip(zip(city_list, areas), nones)
        # areas = areas[0: 1]

        # 针对每个板块写一个文件,启动一个线程来操作
        pool_size = THREAD_POOL_SIZE
        pool = threadpool.ThreadPool(pool_size)
        my_requests = threadpool.makeRequests(self.collect_subdistrict_neighborhood_data, args)
        [pool.putRequest(req) for req in my_requests]
        pool.wait()
        pool.dismissWorkers(pool_size, do_join=True)  # 完成后退出

        # 计时结束，统计结果
        t2 = time.time()
        print("Total crawl {0} areas.".format(len(areas)))
        print("Total cost {0} second to crawl {1} data items.".format(t2 - t1, self.total_neighborhood_num))


if __name__ == "__main__":
    # urls = get_xiaoqu_area_urls()
    # print urls
    # get_xiaoqu_info("sh", "beicai")
    spider = WjpNeighborhoodSpider("ke")
    spider.start()