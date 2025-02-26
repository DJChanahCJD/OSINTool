import re

def parse_keywords(content, keyword):
    """使用正则表达式匹配注释中的关键词"""
    pattern = re.compile(keyword)
    matches = pattern.findall(content)
    return matches if matches else None

def parse_first_keyword(content, keyword):
    """使用正则表达式匹配注释中的第一个关键词"""
    pattern = re.compile(keyword)
    match = pattern.search(content)
    return match.group(1) if match else None

def match_all(content, pattern):
    """使用正则表达式匹配注释中的关键词"""
    pattern = re.compile(pattern)
    matches = pattern.findall(content)
    return matches if matches else None

def match_one(content, keyword):
    """使用正则表达式匹配注释中的第一个关键词"""
    pattern = re.compile(keyword)
    match = pattern.search(content)
    return match.group(1) if match else None