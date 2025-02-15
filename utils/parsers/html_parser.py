import requests
from lxml import html
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.options import Options
from utils.common import get_random_user_agent
import time

# 安装驱动：https://learn.microsoft.com/zh-cn/microsoft-edge/webdriver-chromium/?tabs=c-sharp&form=MA13LH#download-microsoft-edge-webdriver
# 是否提供多种驱动？

class HTMLParser:
    def __init__(self, url, table_xpath, rows_xpath, next_page_xpath, patterns, maxCount=1000):
        self.url = url
        self.table_xpath = table_xpath
        self.rows_xpath = rows_xpath
        self.next_page_xpath = next_page_xpath
        self.patterns = patterns
        self.maxCount = maxCount
        self.content = None

    def get_content(self):
        return self.content

    def parse(self):
        # 创建 edgeOptions 对象
        edge_options = Options()
        # 设置无头模式
        edge_options.add_argument('--headless')  # 静默模式
        # 设置 User-Agent
        edge_options.add_argument(f'user-agent={get_random_user_agent()}')

        # 使用 Selenium 获取动态加载的内容
        driver = webdriver.Edge(options=edge_options)  # 确保已安装 edge 驱动
        driver.get(self.url)

        print("等待页面加载...")

        # 等待表格加载完成
        wait = WebDriverWait(driver, 10)    # 等待 10 秒
        table = wait.until(EC.presence_of_element_located((By.XPATH, self.table_xpath)))

        # 滚动到表格底部，以确保所有内容加载完成
        driver.execute_script("arguments[0].scrollIntoView(false);", table)
        print("滚动到表格底部...")
        time.sleep(5)  # 等待5秒以确保页面加载完成

        all_results = []
        count = 0

        while True:
            # 获取当前页面源码
            self.content = driver.page_source
            print("获取页面源码...")

            # 解析数据
            results = self.parse_table_with_patterns(self.content)
            all_results.extend(results)

            if len(all_results) >= self.maxCount:
                print(f"达到预定数据量{self.maxCount}，停止抓取")
                all_results = all_results[:self.maxCount]
                break

            try:
                # 查找下一页按钮
                next_page = wait.until(EC.element_to_be_clickable((By.XPATH, self.next_page_xpath)))
                # 判断下一页按钮是否可用
                if 'disabled' in next_page.get_attribute('class'):
                    print("已到达最后一页")
                    break
                # 点击下一页按钮
                next_page.click()
                print("点击下一页...")
                # 等待页面加载
                time.sleep(5)
            except Exception as e:
                print(f"无法点击下一页: {str(e)}")
                break


        driver.quit()

        print("======解析完成=======")
        print(f"总数据量: {len(all_results)}")
        print(f"前5行: {all_results[:5]}")
        return all_results

    def parse_table_with_patterns(self, html_content):
        tree = html.fromstring(html_content)
        data = []

        try:
            table = tree.xpath(self.table_xpath)[0]
            print(f"表格: {table}")
            rows = table.xpath(self.rows_xpath)
            print(f"行数: {len(rows)}")

            # 处理每一行
            for row in rows:
                row_html = html.tostring(row, encoding='unicode')
                row_data = {}

                # 对每个模式进行全局匹配
                for field, pattern in self.patterns.items():
                    matches = re.finditer(pattern, row_html)
                    # 去掉 r' 和末尾的 '
                    if pattern.startswith("r'") and pattern.endswith("'"):
                        pattern = pattern[2:-1]
                    for match in matches:
                        # 如果该字段包含多个子字段（由逗号分隔），则逐一保存每个匹配项
                        field_names = [item.strip() for item in field.split(',')]  # 逗号分隔的多个字段，去除多余空格
                        if len(field_names) > 1:
                            for i, field in enumerate(field_names, 1):
                                if match.group(i):
                                    row_data[field] = match.group(i)
                                else:
                                    row_data[field] = ""
                        else:
                            # 初始化 row_data[field] 为一个空字符串
                            if field not in row_data:
                                row_data[field] = ""
                            row_data[field] += match.group(1) if match.group(1) else ""


                # 只保存非空的行数据
                if row_data:
                    print(f"行数据: {row_data}")
                    data.append(row_data)

            return data

        except Exception as e:
            print(f"解析错误: {str(e)}")
            return []