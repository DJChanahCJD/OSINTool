from .base import BaseParser
import requests
import csv
from io import StringIO
import pandas as pd

class CSVParser(BaseParser):
    def parse(self, url, ignore_comment=False):
        self.load_content(url)
        # 使用 pandas 读取 CSV 内容
        df = pd.read_csv(StringIO(self.content))
        # 将标题行作为注释内容
        comment = df.columns.tolist()
        # 将 DataFrame 转换为二维数组
        table = df.values.tolist()

        return table, comment