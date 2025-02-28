import random
from playwright.async_api import async_playwright
from lxml import html
from utils.common import get_random_user_agent
from urllib.parse import urljoin
import re
import asyncio

from .base import BaseParser

class HTMLParser(BaseParser):
    def __init__(self, task):
        super().__init__(task)
        xpaths = task.get('xpaths', {})
        self.task = task
        self.before_action_group = task.get('before_action_group', [])
        self.table_xpath = xpaths.get('table', '')
        self.rows_xpath = xpaths.get('row', '')
        self.next_page_xpath = xpaths.get('next_page', '')
        self.headless = False  # True表示不显示浏览器窗口
        self.browser = None

        # 提前编译正则表达式
        self.compiled_patterns = {}
        for field, pattern in self.patterns.items():
            if pattern.startswith("r'") and pattern.endswith("'"):
                pattern = pattern[2:-1]
            try:
                self.compiled_patterns[field] = re.compile(pattern)
            except re.error as e:
                print(f"正则表达式无效: {str(e)}")

    def _parse_cookies(self):
        if self.cookies:
            cookie_list = self.cookies.split(';')
            return {cookie.strip().split('=', 1)[0]: cookie.strip().split('=', 1)[1] for cookie in cookie_list}
        return {}

    async def _perform_actions(self, page):
        if self.before_action_group:
            print("执行开始解析前的动作组操作...")
            element = None
            for action in self.before_action_group:
                action_type = action.get('actionType')
                target = action.get('target')
                if action_type == 'click':
                    await self._perform_click_action(page, target)
                elif action_type == 'input':
                    await self._perform_input_action(page, element, target)

    async def _perform_click_action(self, page, target):
        try:
            element = page.locator(f'xpath={target}')
            if await element.is_visible() and not await element.is_disabled():
                print(f"执行点击动作: {target}")
                await element.click()
                await asyncio.sleep(random.uniform(1, 3))  # 等待动作执行完成
        except Exception as e:
            print(f"点击动作失败: {str(e)}")

    async def _perform_input_action(self, page, element, target):
        try:
            if element and await element.is_visible() and not await element.is_disabled():
                print(f"执行输入动作: {target}")
                await element.fill(target)
                await asyncio.sleep(random.uniform(1, 3))  # 等待动作执行完成
        except Exception as e:
            print(f"输入动作失败: {str(e)}")

    async def _parse_pages(self, page):
        all_results = []
        while True:
            print("获取页面源码...")
            self.content = await page.content()

            results = await self.parse_table_with_patterns(self.content, self.task)
            if not results:
                print("未找到表格数据")
                break
            all_results.extend(results)

            if len(all_results) >= self.maxCount:
                print(f"达到预定数据量{self.maxCount}，停止抓取")
                all_results = all_results[:self.maxCount]
                break

            if not await self._click_next_page(page):
                break

        return all_results

    async def _click_next_page(self, page):
        try:
            next_page = page.locator(f'xpath={self.next_page_xpath}')
            if await next_page.is_visible() and not await next_page.is_disabled():
                print("点击下一页...")
                await next_page.click()
                await asyncio.sleep(random.uniform(3, 5))
                await page.wait_for_selector(f'xpath={self.table_xpath}')
                return True
            else:
                print("已到达最后一页")
                return False
        except Exception as e:
            print(f"无法点击下一页: {str(e)}")
            return False

    async def _process_children(self, subtask, row_html):
        all_child_results = []
        link_xpath = subtask.get('linkXPath', '')
        link_elements = html.fromstring(row_html).xpath(link_xpath)
        if not link_elements:
            return []

        child_url = link_elements[0].get('href')
        if child_url:
            # 判断是否为完整 URL，如果不是则加上当前域名
            if not child_url.startswith(('http://', 'https://')):
                print("拼接完整URL...")
                child_url = urljoin(self.url, child_url)

        # 创建新的 context
        child_context = await self.browser.new_context(extra_http_headers={'User-Agent': get_random_user_agent()})
        try:
            subtask['url'] = child_url
            from utils.parser_factory import ParserFactory
            parser = ParserFactory.get_parser(subtask)
            # 检查 subtask 中是否存在 maxCount 字段
            max_count = subtask.get('maxCount', 0)
            child_results = await parser.parse(max_count, context=child_context)
            all_child_results.extend(child_results)
            print(f"子页面解析完成, {len(child_results)}条...")
        except Exception as e:
            print(f"处理子任务时出错: {str(e)}")
        finally:
            # 关闭子页面和 context
            await child_context.close()

        return all_child_results

    async def parse(self, maxCount=0, context=None):
        if maxCount > 0:
            self.maxCount = maxCount

        cookie_dict = self._parse_cookies()

        async with async_playwright() as p:
            isMainTask = context is None
            if isMainTask:
                self.browser = await p.chromium.launch(headless=self.headless)
                context = await self.browser.new_context(extra_http_headers={'User-Agent': get_random_user_agent()})
            page = await context.new_page()

            if cookie_dict:
                print("设置cookies...", cookie_dict)
                await page.context.add_cookies([{
                    'name': key,
                    'value': value,
                    'url': self.url,
                } for key, value in cookie_dict.items()])

            await page.goto(self.url)

            print("等待页面加载...")
            await asyncio.sleep(3)

            print("滚动到表格底部...")
            await page.evaluate(f"""
                const table = document.evaluate('{self.table_xpath}', document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue;
                if (table) table.scrollIntoView();
            """)

            await self._perform_actions(page)

            all_results = await self._parse_pages(page)

            if isMainTask:
                await context.close()
                await self.browser.close()

        print(f"======是否为主任务：{isMainTask}，解析完成=======")
        print(f"总数据量: {len(all_results)}")
        print(f"前3行: {all_results[:3]}")
        return all_results

    async def parse_table_with_patterns(self, html_content, task=None):
        tree = html.fromstring(html_content)
        data = []

        try:
            # 尝试获取表格元素
            table = next(iter(tree.xpath(self.table_xpath)), tree)
            if table is tree:
                print(f"未找到表格元素：{self.table_xpath}")
            print(f"表格: {table}")

            # 获取行元素
            rows = table.xpath(self.rows_xpath) if self.rows_xpath else [table]
            if not rows:
                rows = [table]
            print(f"行数: {len(rows)}")
            rows = rows[:self.maxCount]

            for row in rows:
                row_html = html.tostring(row, encoding='unicode')
                print(f"当前行: {row_html[:100]}")
                row_data = {}

                for field, pattern in self.patterns.items():
                    print(f"当前使用的字段: {field}")
                    compiled_pattern = self.compiled_patterns.get(field)
                    if not compiled_pattern:
                        print(f"无效的正则表达式: {pattern}")
                        continue

                    matches = list(compiled_pattern.finditer(row_html))
                    if not matches:
                        print(f"未找到匹配项: {field}")
                        continue

                    print(f"匹配项sssss: {matches}")
                    for match in matches:
                        print(f"匹配项内容: {match.group(0)}")
                        field_names = [item.strip() for item in field.split(',')]
                        print(f"字段名: {field_names}")
                        if len(field_names) > 1:
                            for i, field in enumerate(field_names, 1):
                                if field not in row_data:
                                    row_data[field] = ""
                                if match.group(i):
                                    # 去除HTML标签
                                    clean_text = re.sub(r'<[^>]*>', '', match.group(i))
                                    row_data[field] += clean_text
                                else:
                                    row_data[field] = ""
                        else:
                            if field not in row_data:
                                row_data[field] = ""
                            if match.group(1):
                                # 去除匹配结果中的 HTML 标签
                                clean_text = re.sub(r'<[^>]*>', '', match.group(1))
                                row_data[field] += clean_text

                if row_data:
                    data.append(row_data)
                    print(f"当前行解析完成: {row_data}")

                # 处理子任务
                children = task.get('children', [])
                if len(children) > 0:
                    try:
                        print("尝试获取子任务...")
                        for subtask in children:
                            field = subtask.get('title')
                            if field in row_data:
                                field += "_children"
                            child_results = await self._process_children(subtask, row_html)
                            if child_results:
                                data[-1][field] = child_results
                    except Exception as e:
                        print(f"子任务处理错误: {str(e)}")

            return data

        except Exception as e:
            print(f"解析错误: {str(e)}")
            return data