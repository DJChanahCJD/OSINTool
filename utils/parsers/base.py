from abc import ABC, abstractmethod
import requests

class BaseParser(ABC):
    def __init__(self):
        self.content = None

    def load_content(self, url):
        """加载URL内容"""
        response = requests.get(url)
        response.raise_for_status()  # 检查请求是否成功
        self.content = response.text
        print(f"已加载URL: {url}")
        print(f"内容长度: {len(self.content)}")
        print(f"内容: {self.content}")

        return self.content

    """
        输出: 表格, 注释内容
            table, comment
    """
    @abstractmethod
    def parse(self, url, ignore_comment=False, table_type=0):
        """解析内容

        Args:
            url (str): 目标URL
        Returns:
            list: [{'key': str, 'value': str}]
        """
        pass