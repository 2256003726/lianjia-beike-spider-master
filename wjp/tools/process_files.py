#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
@Project ：lianjia-beike-spider-master 
@File    ：process_files.py
@Author  ：王金鹏
@Date    ：2024/2/6 10:28 
"""
import os
from itertools import zip_longest


def process_and_update_csv(file_path, log_file):
    lines = []
    #第一次 open 使用 'r' 模式来读取文件内容，第二次 open 使用 'w' 模式来覆盖写入文件内容。
    # 这样可以确保在处理文件时，我们先读取文件内容到内存，然后基于这个内容进行写操作，而不会在读取和写入之间发生冲突。
    with open(file_path, 'r', encoding='utf-8') as file:
        try:
            lines = file.readlines()
        except Exception as e:
            # 重新打开文件，逐行读取并处理
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                lines = []
                for i, line in enumerate(file):
                    try:
                        # 在这里处理每一行的数据
                        lines.append(line.strip())
                    except UnicodeDecodeError as e:
                        # 如果发生错误，打印错误信息并将错误信息写入日志文件
                        print(f"处理文件 {file_path} 的第 {i + 1} 行时出错：{e}")
                        with open(log_file_path, "a", encoding="utf-8") as log_file:
                            log_file.write(
                                f"处理文件 {file_path} 的第 {i + 1} 行时出错：{e}\n")

    with open(file_path, 'w', encoding='utf-8') as file:
        for i, line in enumerate(lines):
            # 去除开头的逗号
            if line.startswith(','):
                line = line[1:]
            split_line = line.strip().split(',')
            # 处理字段数量不符合预期的行(标准字段是6个，处理字段为7个的)，将第4至倒数第二个合并为一个字段，
            # 如：20231222,宝山,高境,国权北路405,407号,暂无数据,0套在售二手房
            if len(split_line) > 6:
                # 如果列数大于6，合并指定列
                merged_field = '&'.join(split_line[3:-2])
                new_line = ','.join(split_line[:3] + [merged_field] + split_line[-2:])
                # 输出处理信息到控制台
                print(f"处理文件 {file_path} 的第 {i + 1} 行：原始行内容为：{line.strip()}，处理后行内容为：{new_line}")
                log_file.write(
                    f"处理文件 {file_path} 的第 {i + 1} 行：原始行内容为：{line.strip()}，处理后行内容为：{new_line}\n")
            # 处理字段数量不符合预期的行(标准字段是6个，处理字段不足6个)，使用合法行的前面若干字段给其赋值
            # 如果是第一行，则找到后面行中第一个列数为6的行，若不是第一行，则使用前一行
            # 如：,高境,国权北路405,407号,暂无数据,0套在售二手房
            elif len(split_line) < 6:

                # 输出处理信息到控制台
                print(f"文件 {file_path} 中的第 {i + 1} 行字段少于6个,原始行内容为：{line.strip()},已删除。")
                log_file.write(f"文件 {file_path} 中的第 {i + 1} 行字段少于6个,原始行内容为：{line.strip()},已删除。\n")
                continue

            else:
                # 如果列数等于6，保持原样
                new_line = line.strip()

            file.write(new_line + '\n')


if __name__ == '__main__':
    # 使用方法
    # 指定目标文件夹路径
    data_folder = '../../data/ke/xiaoqu/zz/20240115'
    # data_folder = '../../data/ke/xiaoqu/sh/20230115'

    # data_folder = '../../data/ke/xiaoqu/zz/20240115'
    # 获取文件夹中所有CSV文件的文件名列表
    file_list = [f for f in os.listdir(data_folder) if f.endswith('.csv')]
    print('文件列表：', file_list)
    # 创建logs文件夹
    logs_folder = os.path.join(os.path.dirname(data_folder), "logs")
    os.makedirs(logs_folder, exist_ok=True)

    # 创建日志文件
    base_folder_name = os.path.basename(data_folder)
    log_file_path = os.path.join(logs_folder, base_folder_name.replace('/', '_') + "_processing_log.txt")

    # 循环处理每个文件
    for file_name in file_list:
        file_path = data_folder + '/' + file_name
        print('处理文件:', file_path)
        with open(log_file_path, 'a', encoding='utf8') as log_file:
            process_and_update_csv(file_path, log_file)