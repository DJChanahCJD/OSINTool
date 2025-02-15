from .base import BaseParser
import requests
import csv
from io import StringIO
import pandas as pd
import re


class CSVParser(BaseParser):
    def parse(self, url, parseType=0, columns=None, patterns=None, table_pattern=None):
        """
        解析CSV文件并根据传入的 columns 和 patterns 进行处理。
        若parseType==0, 则通过 columns 根据索引定位列
        若parseType==1, 则通过 patterns 对列值进行正则处理
        一行行添加到结果列表中
        """
        # 加载 CSV 内容
        table = self.parse_to_table(url)

        if parseType == 0:  # 按列索引解析
            return self.convert_to_dict(table, columns, patterns)
        elif parseType == 1:  # 如果是正则匹配类型，进行正则处理
            return self.convert_to_dict_with_patterns(table, columns, patterns)

        return table

    def parse_to_table(self, url):
        """加载并解析 CSV 文件，返回二维表格（列表）"""
        self.load_content(url)
        # 使用 pandas 读取 CSV 内容
        df = pd.read_csv(StringIO(self.content))
        # 将 DataFrame 转换为二维数组，并处理空值
        table = df.fillna('').values.tolist()

        return table

    def convert_to_dict(self, table, columns, patterns):
        """将二维数组转换为字典列表，使用 columns 来选择特定的列"""
        if not table:
            return []

        # column_names = table[0]  # 第一行是列名
        dict_list = []

        # 将每一行转换为字典
        for row in table[1:]:
            row_dict = {}

            # 使用 columns 映射索引并提取数据
            for key, index in columns.items():
                if index < len(row):  # 确保索引有效
                    row_dict[key] = row[index]

            dict_list.append(row_dict)

        return dict_list

    def convert_to_dict_with_patterns(self, table, columns, patterns):
        """基于正则模式将整个表格转换为字典列表"""
        if not table:
            return []

        # column_names = table[0]  # 第一行是列名
        dict_list = []

        for row in table[1:]:
            row_str = ' '.join(map(str, row))  # 将整行数据拼接成字符串
            row_dict = {}
            for key, pattern in patterns.items():
                row_dict[key] = self.apply_pattern(row_str, pattern)
            dict_list.append(row_dict)

        return dict_list

    def apply_pattern(self, value, pattern):
        """应用正则表达式对值进行处理"""
        try:
            # 进行正则匹配
            match = re.search(pattern, value)
            if match:
                return match.group(0)  # 返回第一个匹配结果
        except re.error:
            return value  # 如果正则表达式无效，则返回原值
        return value