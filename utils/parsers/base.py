from abc import ABC, abstractmethod
import os
import requests
from utils.common import get_random_user_agent

class BaseParser(ABC):
    def __init__(self, task):
        parse_rules = task.get('parseValues', [])
        columns = {rule['key']: rule['index'] for rule in parse_rules}
        patterns = {rule['key']: rule['pattern'] for rule in parse_rules}

        self.columns = columns
        self.patterns = patterns
        self.url = task.get('url', '')
        self.children = task.get('children', [])
        self.maxCount = task.get('maxCount', 10)
        self.cookies = task.get('cookies', '')
        self.parseType = task.get('parseType', 0)
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
            headers = {'User-Agent': get_random_user_agent(), 'Cookie': self.cookies}
            response = requests.get(url, headers=headers)
            response.raise_for_status()  # 检查请求是否成功
            self.content = response.text
            print(f"已加载URL: {url}")

    @abstractmethod
    def parse(self, maxCount=None, context=None):
        """
        输出: 解析表格
        """
        pass

    def get_content(self):
        """
        输出: 网页源码
        """
        return self.content