from .base import BaseParser
import requests
import csv
from io import StringIO
import pandas as pd

class CSVParser(BaseParser):
    def parse(self, url, ignore_comment=False, table_type=0):
        self.load_content(url)
        # 使用 pandas 读取 CSV 内容
        df = pd.read_csv(StringIO(self.content))

        # 将 DataFrame 转换为二维数组，并处理空值
        table = df.fillna('').values.tolist()

        # 将标题行作为注释内容
        comment = df.columns.tolist()

        return table, comment