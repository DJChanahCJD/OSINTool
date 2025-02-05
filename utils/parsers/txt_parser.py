from .base import BaseParser

class TXTParser(BaseParser):
    def parse(self, url, ignore_comment=False):
        self.load_content(url)
        table = []
        comment = ''
        lines = self.content.split('\n')

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line.startswith('#'):    # 注释内容
                if ignore_comment:
                    continue
                comment += line + '\n'
            else:   # 表格内容（获取完整表格，包括被注释的部分）
                """
                    例如:
                    123.com  # 11:00  999
                    4434.com # 19:00  888
                """
                line = line.replace('#', '').strip()
                if line:
                    table.append(line.split())


        return table, comment