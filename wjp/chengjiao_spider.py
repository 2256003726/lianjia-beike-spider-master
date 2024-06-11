#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：lianjia-beike-spider-master 
@File    ：chengjiao_spider.py
@Author  ：王金鹏
@Date    ：2024/3/27 16:20 
"""
import re

import threadpool
from bs4 import BeautifulSoup

from lib.item.ChengJiao import ChengJiao
from lib.spider.base_spider import *
from lib.utility.log import *
from lib.utility.path import create_date_path
from lib.zone.area import *
from lib.zone.city import get_city


class ChengJiaoBaseSpider(BaseSpider):
    def collect_area_chengjiao_data(self, city_name, area_name, fmt="csv"):
        """
        对于每个板块,获得这个板块下所有小区的信息
        并且将这些信息写入文件保存
        :param city_name: 城市
        :param area_name: 板块
        :param fmt: 保存文件格式
        :return: None
        """
        district_name = area_dict.get(area_name, "")  # 行政区名
        csv_file = self.today_path + "/{0}_{1}.csv".format(district_name, area_name)
        with open(csv_file, "w", encoding='utf-8-sig') as f:
            # 开始获得需要的板块数据
            cjs = self.get_chengjiao_info(city_name, area_name)
            # 锁定
            if self.mutex.acquire(1):
                self.total_num += len(cjs)
                # 释放
                self.mutex.release()
            if fmt == "csv":
                for chengjiao in cjs:
                    f.write(chengjiao.text() + "\n")
        print("Finish crawl area: " + area_name + ", save data to : " + csv_file)
        logger.info("Finish crawl area: " + area_name + ", save data to : " + csv_file)

    # @staticmethod
    def get_chengjiao_info(self, city, area):
        total_page = 1
        district = area_dict.get(area, "")
        chinese_district = get_chinese_district(district)
        chinese_area = chinese_area_dict.get(area, "")
        chengjiao_list = list()
        page = 'https://{0}.{1}.com/chengjiao/{2}/'.format(city, SPIDER_NAME, area)
        print('第一页：',page)
        logger.info(page)

        headers = create_headers()
        response = requests.get(page, timeout=10, headers=headers, cookies=self.cookie)
        html = response.content
        # print(html)
        soup = BeautifulSoup(html, "lxml")

        # 获得总的页数
        try:
            page_box = soup.find_all('div', class_='page-box')[0]
            matches = re.search(r'.*"totalPage":(\d+),.*', str(page_box))
            total_page = int(matches.group(1))
            total_page = 30 if total_page > 30 else total_page

        except Exception as e:
            print("\tWarning: only find one page for {0}".format(area))
            print("网页是：{0}".format(page))
            print(e)

        # 从第一页开始,一直遍历到最后一页
        for i in range(1, total_page + 1):
            headers = create_headers()
            page = 'https://{0}.{1}.com/chengjiao/{2}/pg{3}'.format(city, SPIDER_NAME, area, i)
            # print(page,'具体页面')  # 打印版块页面地址
            BaseSpider.random_delay()
            response = requests.get(page, timeout=10, headers=headers, cookies=self.cookie)

            html = response.content
            soup = BeautifulSoup(html, "html.parser")
            # 获得有小区信息的panel
            house_elems = soup.find_all('li', {'data-view-event': 'ModuleExpo'})

            for house_elem in house_elems:
                try:

                    # 提取信息
                    title = house_elem.find("div", class_="title").text.strip()  # 标题
                    last_space_index = title.rfind(' ')
                    if last_space_index != -1:
                        # 从倒数第一个空格位置开始截取字符串
                        area_str = title[last_space_index + 1:]
                        # 去掉结尾的"平米"
                        area1 = area_str.rstrip("平米")
                    else:
                        area1 = None
                    deal_date = house_elem.find("div", class_="dealDate").text.strip()  # 成交日期
                    total_price_elem = house_elem.find("div", class_="totalPrice")
                    unit_price_elem = house_elem.find("div", class_="unitPrice")
                    if total_price_elem and unit_price_elem:
                        total_price_span = total_price_elem.find("span", class_="number")
                        unit_price_span = unit_price_elem.find("span", class_="number")

                        if total_price_span and unit_price_span:
                            total_price_text = total_price_span.get_text()
                            unit_price_text = unit_price_span.get_text()

                            total_price = total_price_text + "万"
                            unit_price = unit_price_text + "元/平"
                        else:
                            # 处理找不到 span 元素的情况
                            total_price = "总价未知"
                            unit_price = "单价未知"
                    else:
                        # 处理元素不存在的情况
                        total_price = "总价未知"
                        unit_price = "单价未知"
                    house_info = house_elem.find("div", class_="houseInfo").text.strip()  # 基本信息
                    deal_cycle_info_div = house_elem.find("div", class_="dealCycleeInfo")  # 挂牌价信息的父级元素
                    deal_cycle_span = deal_cycle_info_div.find("span", class_="dealCycleTxt")
                    list_price_span = deal_cycle_span.find("span")
                    # list_price = list_price_span.text.strip("挂牌") if deal_cycle_span else ""  # 挂牌价
                    list_price_text = list_price_span.text.strip()  # 获取文本内容
                    list_price = "挂牌价未知"  # 如果不是正常的挂牌价格，则赋值为空字符串
                    list_unit_price = "挂牌单价未知"
                    match = re.search(r'挂牌(\d+)万', list_price_text)
                    if match:
                        list_price_numeric = float(match.group(1))  # 提取数字部分并转换为浮点数
                        if list_price_numeric > 1:
                            list_price = match.group(1) + "万"  # 提取挂牌价格并添加单位
                            list_unit_price = round(list_price_numeric * 10000 / float(area1))  # 计算挂牌单价
                            list_unit_price = str(list_unit_price) + "元/平"  # 添加单位


                    # 作为对象保存
                    chengjiao = ChengJiao(chinese_district, chinese_area, title, deal_date, total_price, unit_price,
                                          list_price, list_unit_price, house_info)
                    chengjiao_list.append(chengjiao)
                except Exception as e:
                    print("发生错误:", e)
                    print('页面为：', page)
                    print('小区为：',title)
                    continue  # 继续执行下一个循环
        return chengjiao_list

    def start(self):
        city = get_city()
        self.today_path = create_date_path("{0}/chengjiao".format(SPIDER_NAME), city, self.date_string)
        t1 = time.time()  # 开始计时

        # 获得城市有多少区列表, district: 区县
        districts = get_districts(city)
        print('City: {0}'.format(city))
        print('Districts: {0}'.format(districts))

        # 获得每个区的板块, area: 板块
        areas = list()
        for district in districts:
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
        pool_size = thread_pool_size
        pool = threadpool.ThreadPool(pool_size)
        my_requests = threadpool.makeRequests(self.collect_area_chengjiao_data, args)
        [pool.putRequest(req) for req in my_requests]
        pool.wait()
        pool.dismissWorkers(pool_size, do_join=True)  # 完成后退出

        # 计时结束，统计结果
        t2 = time.time()
        print("Total crawl {0} areas.".format(len(areas)))
        print("Total cost {0} second to crawl {1} data items.".format(t2 - t1, self.total_num))

if __name__ == "__main__":
    cookie_str = '*****你自己的cookie，请登录贝壳账号后使用自己的*****'
    cookies = {item.split("=")[0]: item.split("=")[1] for item in cookie_str.split("; ")}
    spider = ChengJiaoBaseSpider(SPIDER_NAME, cookie=cookies)
    spider.start()