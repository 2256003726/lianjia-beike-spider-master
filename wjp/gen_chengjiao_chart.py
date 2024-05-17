#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：lianjia-beike-spider-master 
@File    ：gen_chengjiao_chart.py
@Author  ：王金鹏
@Date    ：2024/5/11 15:32 
"""
# -*- coding: utf-8 -*-
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
data_folder = '../data/ke/chengjiao/sh/20240511'

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
combined_df['成交单价'] = combined_df['成交单价'].apply(lambda x: x / 10000 if x > 1000000 else x)
combined_df['挂牌单价'] = combined_df['挂牌单价'].apply(lambda x: x / 10000 if x > 1000000 else x)
# 按区域计算平均房价和中位数房价
average_prices = combined_df.groupby('区域')['成交单价'].mean()
median_prices = combined_df.groupby('区域')['成交单价'].median()

# average_list_prices = combined_df.groupby('区域')['挂牌单价'].mean()

# 按平均房价排序区域
sorted_areas = average_prices.sort_values(ascending=False).index
print(sorted_areas)



# 设置中文字体
plt.rc("font", family='Microsoft YaHei')

# 绘制柱状图
fig, ax = plt.subplots(figsize=(10, 6))
average_prices.loc[sorted_areas].plot(kind='bar', color='skyblue', alpha=0.7, label='均价', ax=ax)
median_prices.loc[sorted_areas].plot(kind='bar', color='orange', alpha=0.7, label='中位数', ax=ax)

ax.set_xlabel('区')
ax.set_ylabel('房价')
ax.set_title('{0}上海各区房价图（平均数和中位数）'.format(data_folder[-8:]))
# ax.set_title('{0}上海各区房价图（平均数和中位数）'.format(20240228))
ax.legend()
# # 在柱状图上显示平均和中位数的值
# for i, v in enumerate(average_prices.loc[sorted_areas]):
#     ax.text(i, v + 10, f'{v:.2f}', ha='center', va='bottom', fontsize=8, color='black')
#     ax.text(i, median_prices.loc[sorted_areas[i]] + 10, f'{median_prices.loc[sorted_areas[i]]:.2f}', ha='center', va='bottom', fontsize=8, color='black')
# 在柱状图上显示平均和中位数的值
for i, v in enumerate(average_prices.loc[sorted_areas]):
    ax.text(i, v + 5, f'{v:.2f}', ha='center', va='bottom', fontsize=8, color='blue')
    ax.text(i, median_prices.loc[sorted_areas[i]] + 5, f'{median_prices.loc[sorted_areas[i]]:.2f}', ha='center',
            va='top', fontsize=8, color='red')
plt.xticks(rotation=45)  # 如果区域名过长，可以旋转x轴标签
plt.tight_layout()
plt.show()


# 记录结束时间
end_time = time.time()

# 计算执行时间
execution_time = end_time - start_time
print(f"程序执行时间为: {execution_time} 秒")