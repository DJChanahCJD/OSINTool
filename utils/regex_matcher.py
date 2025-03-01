import re

def match_all(content, pattern):
    """使用正则表达式匹配所有匹配项"""
    pattern = re.compile(pattern)
    matches = pattern.findall(content)
    return matches if matches else None

def match_one(content, keyword):
    """使用正则表达式匹配第一个匹配项"""
    # 去除分行
    content = content.replace('\n', '').strip()
    pattern = re.compile(keyword)
    match = pattern.search(content)
    # 去除HTML标签
    if match:
        match = re.sub(r'<.*?>', '', match.group(1))
    return match