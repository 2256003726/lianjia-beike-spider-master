#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：lianjia-beike-spider-master 
@File    ：gen_ershou_chart.py.py
@Author  ：王金鹏
@Date    ：2024/3/1 14:39 
"""
import time

import matplotlib.font_manager as fm
import pandas as pd
import os
import io
import numpy as np
import matplotlib.pyplot as plt

# 记录程序开始时间
start_time = time.time()

# 指定目标文件夹路径
data_folder = '../data/ke/ershou/sh/20240229'

# 获取文件夹中所有CSV文件的文件名列表
file_list = [f for f in os.listdir(data_folder) if f.endswith('.csv')]
print('文件列表：', file_list)

dataframes = []

for file in file_list:
    file_path = os.path.normpath(os.path.join(data_folder, file))

    # 判断文件大小，只有非空文件才尝试读取
    if os.path.getsize(file_path) > 0:
        print(f"文件 {file_path}")

        # 出错处理（可能出现字段数量不匹配的问题，比如绝大部分行是6个字段，个别行是7个字段，会报错！）
        try:
            df = pd.read_csv(file_path, header=None, names=['日期', '区', '板块', '描述', '总价', '信息'], encoding='utf8')
            dataframes.append(df)
        except Exception as e:
            print(f"文件 {file_path} 读取时出错：{e}")
    else:
        print(f"文件 {file_path} 是空文件，跳过读取。")