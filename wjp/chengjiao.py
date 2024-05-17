#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：lianjia-beike-spider-master 
@File    ：chengjiao.py
@Author  ：王金鹏
@Date    ：2024/4/19 16:11 
"""
from lib.spider.base_spider import SPIDER_NAME
from wjp.chengjiao_spider import ChengJiaoBaseSpider

if __name__ == "__main__":
    # spider = XiaoQuBaseSpider(SPIDER_NAME)
    # date = get_custom_date_string(2024, 3, 27)
    # spider = ChengJiaoBaseSpider(SPIDER_NAME)
    # spider.start()
    cookie_str = 'lianjia_uuid=144f9b35-c17b-4f50-b59f-403e8d9f3db7; crosSdkDT2019DeviceId=-ksyepa-1hrfwo-qxlbr3l19i0cm0o-4vbq1xhnh; lfrc_=5b15772d-2000-40a8-a127-18f708e91911; select_city=310000; lianjia_ssid=e7abf813-faa0-4055-9766-691fbb70fc3e; Hm_lvt_9152f8221cb6243a53c83b956842be8a=1713836015,1713856445,1713861511,1715318678; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%2218f09cdfab8497-091034e9d545cf-26001d51-2359296-18f09cdfab9626%22%2C%22%24device_id%22%3A%2218f09cdfab8497-091034e9d545cf-26001d51-2359296-18f09cdfab9626%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E4%BB%98%E8%B4%B9%E5%B9%BF%E5%91%8A%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fwww.baidu.com%2Fother.php%22%2C%22%24latest_referrer_host%22%3A%22www.baidu.com%22%2C%22%24latest_search_keyword%22%3A%22%E8%B4%9D%E5%A3%B3%22%2C%22%24latest_utm_source%22%3A%22baidu%22%2C%22%24latest_utm_medium%22%3A%22pinzhuan%22%2C%22%24latest_utm_campaign%22%3A%22wyshanghai%22%2C%22%24latest_utm_content%22%3A%22biaotimiaoshu%22%2C%22%24latest_utm_term%22%3A%22biaoti%22%7D%7D; login_ucid=2000000343964847; lianjia_token=2.00132353c47e384287028e7af5a5d3a5ba; lianjia_token_secure=2.00132353c47e384287028e7af5a5d3a5ba; security_ticket=Sc7p58oT0o5qAFJFDYtnX8xtLiyaF6k5tXncWJRDOKjIlLaU1hTUy3JPcN3y0tS5Bi/WvBAMbCgnlLXPz0qlZeDe9kkQI+QY9mwQT8w1W8ceESgwJ8ZNUULNADRHV7tYFU6VlDMD8MSqx+Ny3fgzxcZUdJX9vzsv+fG7aN5jKHY=; Hm_lpvt_9152f8221cb6243a53c83b956842be8a=1715318748; srcid=eyJ0Ijoie1wiZGF0YVwiOlwiM2MwMTQ4YzQyMTY1OWE2ZTAyNzYzMGU2NTkwMDYxMzA3OGNkNGIwOWExZjJlMTU0MWFmYmIyZjJlZmQ0NzNjNzAwNTlkYzAwNGI5NmIzY2M1MTdhMmFkOGJjY2NiNjg3ZmFjODI4NWUxNWE0M2E3ZWI5N2E5ZjY5MThhNDI3OTQyODNhZmEzNDk4ZjViNzBlM2U5MTA2ZWIzMDkzNTMzNmY5NGQ3OTM5YmY3YjhiZmY1ZDY2NWRlYmIxMDNiMDFiMzk4OGE0M2JlN2E1ODNmOTY3YzU4MjIwMzVkZDFiM2FhZDY5ZGYyMjM2NDNhMzU5NzNkMmVhNDljNWYzZmM5M1wiLFwia2V5X2lkXCI6XCIxXCIsXCJzaWduXCI6XCIyMTAxZDkyOVwifSIsInIiOiJodHRwczovL3NoLmtlLmNvbS9jaGVuZ2ppYW8vIiwib3MiOiJ3ZWIiLCJ2IjoiMC4xIn0=; lianjia_ssid=e7abf813-faa0-4055-9766-691fbb70fc3e; lianjia_uuid=2999b082-728c-4303-b0f8-75ff5908cf62'
    cookies = {item.split("=")[0]: item.split("=")[1] for item in cookie_str.split("; ")}
    spider = ChengJiaoBaseSpider(SPIDER_NAME, cookie=cookies)
    spider.start()