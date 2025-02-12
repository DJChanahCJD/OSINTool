from abc import ABC, abstractmethod
import os
import requests

class BaseParser(ABC):
    def __init__(self):
        self.content = None

    def load_content(self, url):
        """加载URL或本地文件内容"""
        if url.startswith('file://'):
            # 去掉 file:// 前缀，并将路径中的正斜杠替换为反斜杠
            file_path = url.replace('file://', '').replace('/', '\\')
            if os.path.isfile(file_path):
                with open(file_path, 'r', encoding='utf-8') as file:
                    self.content = file.read()
                print(f"已加载本地文件: {file_path}")
            else:
                raise FileNotFoundError(f"本地文件不存在: {file_path}")
        else:
            response = requests.get(url)
            response.raise_for_status()  # 检查请求是否成功
            self.content = response.text
            print(f"已加载URL: {url}")

    @abstractmethod
    def parse(self, url, table_type=0):
        """
        输出: 表格
            table
        """
        pass