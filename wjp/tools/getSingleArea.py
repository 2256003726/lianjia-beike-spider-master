#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：lianjia-beike-spider-master 
@File    ：getSingleArea.py
@Author  ：王金鹏
@Date    ：2024/5/13 11:00 
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

class ChengJiaoSingleArea(BaseSpider):

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
        print('第一页：', page)
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
            # total_page = 30 if total_page > 30 else total_page

        except Exception as e:
            print("\tWarning: only find one page for {0}".format(area))
            print("网页是：{0}".format(page))
            print(e)

        # 从第一页开始,一直遍历到最后一页
        for i in range(1, total_page + 1):
            headers = create_headers()
            page = 'https://{0}.{1}.com/chengjiao/{2}/pg{3}'.format(city, SPIDER_NAME, area, i)
            print(page)  # 打印版块页面地址
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
                    print('小区为：', title)
                    continue  # 继续执行下一个循环
        return chengjiao_list

    def start(self):
        city = get_city()
        self.today_path = create_date_path("{0}/chengjiao".format(SPIDER_NAME), city, self.date_string)
        t1 = time.time()  # 开始计时

        # 获得城市有多少区列表, district: 区县
        districts = get_districts(city)
        # print('City: {0}'.format(city))
        # print('Districts: {0}'.format(districts))
        # 获得每个区的板块, area: 板块
        areas = list()
        for district in districts:
            # if district == 'minhang':
            #     areas_of_district = get_areas(city, district)
            #     print('{0}: Area list:  {1}'.format(district, areas_of_district))
            #     # 用list的extend方法,L1.extend(L2)，该方法将参数L2的全部元素添加到L1的尾部
            #     areas.extend(areas_of_district)
            #     # 使用一个字典来存储区县和板块的对应关系, 例如{'beicai': 'pudongxinqu', }
            #     for area in areas_of_district:
            #         area_dict[area] = district
            if district == 'minhang':
                # areas_of_district = get_areas(city, district)
                # print(areas_of_district)
                # return
                areas_of_district = ['meilong'] # 手动赋值
                print(areas_of_district)
                print('{0}: Area list:  {1}'.format(district, areas_of_district))
                # 用list的extend方法,L1.extend(L2)，该方法将参数L2的全部元素添加到L1的尾部
                areas.extend(areas_of_district)
                print(areas)

                # 使用一个字典来存储区县和板块的对应关系, 例如{'beicai': 'pudongxinqu', }
                for area in areas_of_district:
                    area_dict[area] = district
                print(area_dict)
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
    # spider = XiaoQuBaseSpider(SPIDER_NAME)
    # date = get_custom_date_string(2024, 3, 27)
    cookie_str = 'SECKEY_ABVK=0xPwa6aF6497XTmVk7ONP94LIR6D+bC8JU+NvkSeFAE%3D; BMAP_SECKEY=yEAJ7XQenl5lz-H7FJU6ngPpBuiN7YshLC3YiffQF_Q4urRRPqVwZFx88MT35rm8RrboqaAmoQetMO3BNS_g7r6m5na1NgCFjEIKxU9zDzp9EChiMYtn9T28qLMxG1ZY56tHZQO97a_nSDDr8wbGGqYfog8iOhX9AKe1mGdMBjmwK5-Pinsn4aRLyi-nLPre; lianjia_uuid=7eb67d73-c17d-4612-a7ea-3d072d1ed6be; crosSdkDT2019DeviceId=3jfztq-4zlfbd-25usgofq588t5nj-hoqolh8md; _ga=GA1.2.1471045471.1718161908; ke_uuid=5f009f0342ef5961ee1dd0dad22665e9; lfrc_=a764d531-bd53-4022-aab6-c11e8d38b31d; ftkrc_=9e7a80c5-18b0-41e3-8497-eef8bbf9d761; __xsptplus788=788.3.1721868060.1721868060.1%234%7C%7C%7C%7C%7C%23%23%23; select_city=310000; Hm_lvt_9152f8221cb6243a53c83b956842be8a=1721785615,1723614229; HMACCOUNT=DD527BC0F9FD8F37; login_ucid=2000000343964847; lianjia_token=2.00130b5c7a7e104d3902a6754ba9f9fd59; lianjia_token_secure=2.00130b5c7a7e104d3902a6754ba9f9fd59; security_ticket=B/Btu7JEH7rUAADGwD87q4jHfQ00xiTxfyDmcIPK1Y7lYIx3iTsLkmNlFgkn+gRkfEUfVO4w1vtVKL94iXB4lc6hxzXAuQpJ+SWz9VS5gZIMtXioywIL8g2cjQayZ+bMWAzj3sfLCpN9fDwtKbBWc15FAS3mGBxBGe7dbW4KaOg=; lianjia_ssid=8f131793-faf2-4179-9baa-85645bcdf155; hip=0ZziHOEifpks2g82GsUTd72PVU8KQ_qsKJxm9XJsS1241OsyQ8JZ-D7zy9a-lB3BvM9bWn9Sf3UpvS9iGnjD6OEJ3ECY_XWzsztwUPW3ElXRcuzaRniqOBfwflbthr-tj2b0ry7VdQvXmANzJ_Kv_6JTDUGn_8JLISJWFfffZfExqQubfoU%3D; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221900a35d9b3395-0cd25dd4cbf544-26001c51-2359296-1900a35d9b41e4e%22%2C%22%24device_id%22%3A%221900a35d9b3395-0cd25dd4cbf544-26001c51-2359296-1900a35d9b41e4e%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_utm_source%22%3A%22baidu%22%2C%22%24latest_utm_medium%22%3A%22pinzhuan%22%2C%22%24latest_utm_campaign%22%3A%22wyshanghai%22%2C%22%24latest_utm_content%22%3A%22biaotimiaoshu%22%2C%22%24latest_utm_term%22%3A%22biaoti%22%7D%7D; Hm_lpvt_9152f8221cb6243a53c83b956842be8a=1723685386; srcid=eyJ0Ijoie1wiZGF0YVwiOlwiZTFkMzgwMDI1MjI1YTdiYmQzNjI2Mzk2NGJhOGY4MTNkZGYwMDk2NDkxZjZmOWIzZWFjYjgxZDdlMmU5YzhkYzhhYzQzNGVkYmNiNDhhOWNiYTY4YzMxODdiZjg1MTdhNWZlMmE5Y2U4ZWZiNjBmMTczMGIzMjhhN2Q3ZGY5Y2VhMmE5N2U3MDA2YWI2OWUyMGQ1OTJiMWY0MWY2M2FhMzcyODE3YjI0MGNmMmI0Mzc1NzUxYjEyMjJhMGZhYmI0MDdkMzE3YzI3NTJjOGM5OGRkOGJiMWY4OWFjZGVhMDFhZDUwY2JhZTkyNzk4ODAzM2E0NTVlODUwN2JjNmNjOVwiLFwia2V5X2lkXCI6XCIxXCIsXCJzaWduXCI6XCI3Mzg2NjljNlwifSIsInIiOiJodHRwczovL3NoLmtlLmNvbS9jaGVuZ2ppYW8vbWVpbG9uZy8iLCJvcyI6IndlYiIsInYiOiIwLjEifQ=='
    cookies = {item.split("=")[0]: item.split("=")[1] for item in cookie_str.split("; ")}
    spider = ChengJiaoSingleArea(SPIDER_NAME, cookie=cookies)
    spider.start()