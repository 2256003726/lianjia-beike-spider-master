from itertools import zip_longest

import matplotlib.font_manager as fm
import pandas as pd
import os
import io
import numpy as np
import matplotlib.pyplot as plt

from lib.zone.city import get_chinese_city

# 指定目标文件夹路径
# data_folder = '../../data/ke/xiaoqu/sh/20231222'
data_folder = '../../data/ke/xiaoqu/zz/20240115'

# data_folder = '../../data/ke/xiaoqu/zz/20240115'
# 获取文件夹中所有CSV文件的文件名列表
file_list = [f for f in os.listdir(data_folder) if f.endswith('.csv')]
print('文件列表：', file_list)
# 读取所有CSV文件并存储在DataFrame列表中
# 1. 如果是空文件，直接跳过读取
# 2. 如果每行信息超过6列（用逗号分割），说明小区名字被分割了，则合并第4个字段(包含)到倒数第二个字段(不包含)
dataframes = []
for file in file_list:
    file_path = os.path.normpath(os.path.join(data_folder, file))
    # print("路径：", file_path)
    try:
        # 判断文件大小，只有非空文件才尝试读取
        if os.path.getsize(file_path) > 0:
            print(f"文件 {file_path}")
            df = pd.read_csv(file_path, encoding='utf-8', header=None, on_bad_lines='error',encoding_errors='ignore')  # 使用指定的编码格式读取文件
            dataframes.append(df)
        else:
            print(f"文件 {file_path} 是空文件，跳过读取。")
    except pd.errors.ParserError as e:  # 出错处理（可能出现字段数量不匹配的问题，比如绝大部分行是6个字段，个别行是7个字段，会报错！）
        lines = []
        with open(file_path, 'r', encoding='gbk') as eFile:
            lines = eFile.readlines()
        # 处理错误行
        for i, line in enumerate(lines):
            # 处理字段数量不符合预期的行(标准字段是6个，处理字段为7个的)，将第4至倒数第二个合并为一个字段，如：20231222,宝山,高境,国权北路405,407号,暂无数据,0套在售二手房
            split_line = line.split(',')
            if len(split_line) > 6:
                print(f"文件 {file_path.split('\\')[-1]}处理第 {i + 1} 行数据时出错，内容为：{line}")
                merged_field = '&'.join(split_line[3:-2])  # 用 & 拼接小区中间的号码（原本的 , 拼接会导致读取文件出错）
                print(merged_field)
                new_line = ','.join(split_line[:3] + [merged_field] + split_line[-2:])
                df = pd.read_csv(io.StringIO(new_line), encoding='utf-8')
                dataframes.append(df)

    # dataframes.append(df)

# 合并所有数据到一个DataFrame
combined_df = pd.concat(dataframes)

# 数据清洗和处理
combined_df.rename(columns={0: '日期', 1: '区域', 2: '地区', 3: '小区名', 4: '房价', 5: '二手房数量'}, inplace=True)
combined_df['房价'] = combined_df['房价'].replace('暂无数据', np.nan)
combined_df['房价'] = combined_df['房价'].str.replace('元/m2', '', regex=False).astype(float)
# 按区域计算平均房价和中位数房价
average_prices = combined_df.groupby('区域')['房价'].mean()
median_prices = combined_df.groupby('区域')['房价'].median()
# 按平均房价排序区域
sorted_areas = average_prices.sort_values(ascending=False).index
if sorted_areas[-1] == "0套在售二手房":
    sorted_areas = sorted_areas[0:-1]

# 设置中文字体
plt.rc("font", family='Microsoft YaHei')

# 绘制柱状图
fig, ax = plt.subplots(figsize=(10, 6))
average_prices.loc[sorted_areas].plot(kind='bar', color='skyblue', alpha=0.7, label='均价', ax=ax)
median_prices.loc[sorted_areas].plot(kind='bar', color='orange', alpha=0.7, label='中位数', ax=ax)

ax.set_xlabel('区')
ax.set_ylabel('房价')
print(data_folder[-10:-8])
ax.set_title('{0}{1}各区房价图（平均数和中位数）'.format(data_folder[-8:], get_chinese_city(data_folder[-11:-9])))
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
