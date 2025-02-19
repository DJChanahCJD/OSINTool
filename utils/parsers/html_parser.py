import random
from playwright.sync_api import sync_playwright
from lxml import html
from utils.common import get_random_user_agent
# from urllib.parse import urlparse
import re
import time

class HTMLParser:
    def __init__(self, url, table_xpath, rows_xpath, next_page_xpath, patterns, maxCount=10):
        self.url = url
        self.table_xpath = table_xpath
        self.rows_xpath = rows_xpath
        self.next_page_xpath = next_page_xpath
        self.patterns = patterns
        self.maxCount = maxCount
        self.content = None

    def get_content(self):
        return self.content

    def parse(self, cookies=None):
        # 如果有cookie字符串，处理为cookie格式
        cookie_dict = {}
        if cookies:
            cookie_list = cookies.split(';')
            for cookie in cookie_list:
                # 分割cookie并将其转换为字典形式
                key, value = cookie.strip().split('=', 1)
                cookie_dict[key] = value


        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)  # Set headless=True to disable browser UI
            page = browser.new_page(extra_http_headers={'User-Agent': get_random_user_agent()})

            # 如果传入了cookie，设置cookies
            if cookie_dict:
                print("设置cookies...", cookie_dict)
                # # 通过 urlparse 从 URL 中提取域名
                # parsed_url = urlparse(self.url)
                # domain = parsed_url.netloc  # 提取域名部分
                page.context.add_cookies([{
                    'name': key,
                    'value': value,
                    'url': self.url,
                } for key, value in cookie_dict.items()])

            page.goto(self.url)

            print("等待页面加载...")
            page.wait_for_selector(f'xpath={self.table_xpath}')

            print("滚动到表格底部...")
            page.evaluate(f"""
                const table = document.evaluate('{self.table_xpath}', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                if (table) table.scrollIntoView();
            """)

            all_results = []

            while True:
                print("获取页面源码...")
                self.content = page.content()

                results = self.parse_table_with_patterns(self.content)
                all_results.extend(results)

                if len(all_results) >= self.maxCount:
                    print(f"达到预定数据量{self.maxCount}，停止抓取")
                    all_results = all_results[:self.maxCount]
                    break

                try:
                    next_page = page.locator(f'xpath={self.next_page_xpath}')   # 定位下一页按钮

                    if next_page.is_visible() and not next_page.is_disabled():
                        print("点击下一页...")
                        next_page.click()
                        time.sleep(random.uniform(3, 5))  # 延时3到5秒，等待页面加载（必要，否则会爬取到未加载完的数据又跳到下一页）
                        page.wait_for_selector(f'xpath={self.table_xpath}')
                    else:
                        print("已到达最后一页")
                        break
                except Exception as e:
                    print(f"无法点击下一页: {str(e)}")
                    break

            browser.close()

        print("======解析完成=======")
        print(f"总数据量: {len(all_results)}")
        print(f"前5行: {all_results[:5]}")
        return all_results

    def parse_table_with_patterns(self, html_content):
        tree = html.fromstring(html_content)
        data = []

        try:
            # 用XPath定位表格和行
            table = tree.xpath(self.table_xpath)[0]
            print(f"表格: {table}")
            rows = table.xpath(self.rows_xpath)
            print(f"行数: {len(rows)}")

            # 解析每一行
            for row in rows:
                row_html = html.tostring(row, encoding='unicode')
                row_data = {}

                # 遍历每个字段和对应的正则表达式
                for field, pattern in self.patterns.items():
                    matches = re.finditer(pattern, row_html)
                    if pattern.startswith("r'") and pattern.endswith("'"):
                        pattern = pattern[2:-1]
                    for match in matches:
                        field_names = [item.strip() for item in field.split(',')]
                        if len(field_names) > 1:
                            for i, field in enumerate(field_names, 1):
                                if match.group(i):
                                    row_data[field] = match.group(i)
                                else:
                                    row_data[field] = ""
                        else:
                            if field not in row_data:
                                row_data[field] = ""
                            row_data[field] += match.group(1) if match.group(1) else ""

                # 添加到数据列表
                if row_data:
                    print(f"行数据: {row_data}")
                    data.append(row_data)

            return data

        except Exception as e:
            print(f"解析错误: {str(e)}")
            return []
