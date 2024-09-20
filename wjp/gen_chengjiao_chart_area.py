#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：lianjia-beike-spider-master 
@File    ：gen_chengjiao_chart_area.py
@Author  ：王金鹏
@Date    ：2024/5/13 15:35 
"""


import time
from itertools import zip_longest

import matplotlib.font_manager as fm
import pandas as pd
import os
import io
import numpy as np
import matplotlib.pyplot as plt

# 记录程序开始时间
start_time = time.time()

# 指定目标文件夹路径
data_folder = '../data/ke/chengjiao/sh/20240815'

# 获取文件夹中所有CSV文件的文件名列表
file_list = [f for f in os.listdir(data_folder) if f.endswith('.csv')]
print('文件列表：', file_list)
# 读取所有CSV文件并存储在DataFrame列表中
# 1. 如果是空文件，直接跳过读取
dataframes = []

for file in file_list:
    file_path = os.path.normpath(os.path.join(data_folder, file))

    # 判断文件大小，只有非空文件才尝试读取
    if os.path.getsize(file_path) > 0:
        print(f"文件 {file_path}")

        # 出错处理（可能出现字段数量不匹配的问题，比如绝大部分行是6个字段，个别行是7个字段，会报错！）
        try:
            df = pd.read_csv(file_path, header=None, encoding='utf8')
            dataframes.append(df)
        except Exception as e:
            print(f"文件 {file_path} 读取时出错：{e}")
    else:
        print(f"文件 {file_path} 是空文件，跳过读取。")


    # dataframes.append(df)

# 合并所有数据到一个DataFrame
combined_df = pd.concat(dataframes)
# 数据清洗和处理
combined_df.rename(columns={0: '区域', 1: '地区', 2: '小区', 3: '房屋信息', 4: '成交日期', 5: '成交价', 6: '成交单价', 7: '挂牌价', 8: '挂牌单价'}, inplace=True)

combined_df['成交价'] = combined_df['成交价'].replace('总价未知', np.nan)
combined_df['成交价'] = combined_df['成交价'].str.replace('万', '', regex=False).astype(float)

combined_df['挂牌价'] = combined_df['挂牌价'].replace('挂牌价未知', np.nan)
combined_df['挂牌价'] = combined_df['挂牌价'].str.replace('万', '', regex=False).astype(float)

combined_df['成交单价'] = combined_df['成交单价'].replace('单价未知', np.nan)
combined_df['成交单价'] = combined_df['成交单价'].str.replace('元/平', '', regex=False).astype(float)

combined_df['挂牌单价'] = combined_df['挂牌单价'].replace('挂牌单价未知', np.nan)
combined_df['挂牌单价'] = combined_df['挂牌单价'].str.replace('元/平', '', regex=False).astype(float)

# 处理成交价和挂牌价
combined_df['成交价'] = combined_df['成交价'].apply(lambda x: x / 10000 if x > 1000000 else x)
combined_df['挂牌价'] = combined_df['挂牌价'].apply(lambda x: x / 10000 if x > 1000000 else x)

# 处理成交单价和挂牌单价
combined_df['成交单价'] = combined_df['成交单价'].apply(lambda x: x / 10000 if x > 500000 else x)
combined_df['挂牌单价'] = combined_df['挂牌单价'].apply(lambda x: x / 10000 if x > 1000000 else x)

# 将成交日期转换为日期时间格式
combined_df['成交日期'] = pd.to_datetime(combined_df['成交日期'])

# 提取年份和月份
combined_df['年份'] = combined_df['成交日期'].dt.year
# combined_df['月份'] = combined_df['成交日期'].dt.month
combined_df['季度'] = combined_df['成交日期'].dt.quarter
# 按区域和年份进行分组
grouped = combined_df.groupby(['地区', '年份', '季度'])

# 计算每个季度的数据量
quarterly_counts = grouped.size()

# 筛选出数据量大于等于100条的季度
valid_quarters = quarterly_counts[quarterly_counts >= 0].index

# 过滤出符合条件的数据
valid_data = combined_df[combined_df.set_index(['地区', '年份', '季度']).index.isin(valid_quarters)]
print(valid_data)
# 按区域、年份和季度进行分组
# valid_grouped = valid_data.groupby(['地区', '年份', '季度'])
# 筛选出城南地区的数据
single_area = 'meilong'
area_data = valid_data[valid_data['地区'] == single_area]

# 按照区域、年份和季度进行分组
area_grouped = area_data.groupby(['年份', '季度'])

# 计算每个季度的平均成交单价和成交量
average_prices = area_grouped['成交单价'].mean()
transaction_counts = area_grouped.size()
# 计算每个季度的平均挂牌单价
average_list_prices = area_grouped['挂牌单价'].mean()
print(average_prices.index)
print(average_prices.values)
# 将 MultiIndex 中的每个元组转换为字符串作为标签
labels = [f"{year}-{quarter}" for year, quarter in average_prices.index]
# 创建年份和季度组合的标签
# labels = [f"{year} Q{quarter}" for year, quarter in average_prices.index]
# 设置中文字体
plt.rc("font", family='Microsoft YaHei')
# 绘制折线图和柱状图
fig, ax1 = plt.subplots()
# 绘制折线图
ax1.plot(labels, average_prices.values, color='tab:blue', marker='o', label='成交单价')
ax1.set_xlabel('季度', fontsize=12)
ax1.set_ylabel('平均成交单价（元）', color='tab:blue', fontsize=12)
ax1.tick_params(axis='y', labelcolor='tab:blue')
# 在折线图上方标注数字
for i, price in enumerate(average_prices.values):
    ax1.text(labels[i], price, f'{price:.0f}', ha='center', va='bottom', fontsize=12)

# 绘制挂牌单价折线图
ax1.plot(labels, average_list_prices.values, color='tab:green', marker='x', label='挂牌单价')
# 在挂牌单价折线图上方标注数字
for i, price in enumerate(average_list_prices.values):
    ax1.text(labels[i], price, f'{price:.0f}', ha='center', va='bottom', fontsize=12, color='green')

# 创建第二个 y 轴并绘制柱状图
ax2 = ax1.twinx()
ax2.bar(labels, transaction_counts.values, color='tab:orange', alpha=0.5, label='成交量')
ax2.set_ylabel('成交量', color='tab:orange')
ax2.tick_params(axis='y', labelcolor='tab:orange')

# 添加图例
# fig.legend(loc="upper left", bbox_to_anchor=(0.1,0.9))
# 添加图例
# 添加图例（调整位置参数）
fig.legend(loc="upper right", bbox_to_anchor=(1,0.9))
# 添加标题
plt.title(single_area+'区域季度成交单价和成交量')
plt.xticks(rotation=45)  # 旋转 x 轴标签以免重叠
plt.show()