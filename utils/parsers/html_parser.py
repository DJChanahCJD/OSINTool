from bs4 import BeautifulSoup
import bs4
from .base import BaseParser

class HTMLParser(BaseParser):
    def parse(self, url, table_type=0):
        self.load_content(url)
        table = []
        comment = ""
        soup = BeautifulSoup(self.content, 'html.parser')

        # HTML解析方法（三种类型：表格、ul/ol/li、div） -> table_type = 0/1/2
        # （类DFS，从底层文本和类添加列，
        # 如果上层包含未添加的文本则添加，否则忽略）
        # 对于相同的类名使用append，需要支持预览解析表格，
        # 靠类名也不行，
        # 对于<a>标签，另外处理。（单独一列？）
        # 仍然通过列数进行集成。

        if table_type == 0:
            # 表格解析
            tables = soup.find_all('table')
            for table_tag in tables:
                rows = table_tag.find_all('tr')
                for row in rows:
                    cols = row.find_all(['th', 'td'])
                    table.append([col.get_text(strip=True) for col in cols])

        return table, comment