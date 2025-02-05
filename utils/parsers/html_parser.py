from bs4 import BeautifulSoup
from .base import BaseParser

class HTMLParser(BaseParser):
    def parse(self, url, ignore_comment=False):
        self.load_content(url)
        results = []
        soup = BeautifulSoup(self.content, 'html.parser')

        for rule in parse_rules:
            if rule['parseType'] == 'column':
                # 处理表格列
                tables = soup.find_all('table')
                for table in tables:
                    rows = table.find_all('tr')
                    for row in rows:
                        cells = row.find_all(['td', 'th'])
                        if len(cells) > rule['index']:
                            results.append({
                                'key': rule['key'],
                                'value': cells[rule['index']].get_text(strip=True)
                            })

            elif rule['parseType'] == 'comment':
                # 处理注释内容
                comments = soup.find_all(string=lambda text: isinstance(text, bs4.Comment))
                for comment in comments:
                    if rule['keyword'] in comment:
                        value = comment.split(rule['keyword'])[-1].strip()
                        results.append({
                            'key': rule['key'],
                            'value': value
                        })

        return results