from .parsers.html_parser import HTMLParser
from .parsers.txt_parser import TXTParser

class ParserFactory:
    _parsers = {
        'html': HTMLParser,
        'txt': TXTParser
    }

    @classmethod
    def get_parser(cls, format_type):
        """获取指定格式的解析器实例"""
        parser_class = cls._parsers.get(format_type.lower())
        if not parser_class:
            raise ValueError(f'Unsupported format: {format_type}')
        return parser_class()

    @classmethod
    def register_parser(cls, format_type, parser_class):
        """注册新的解析器"""
        cls._parsers[format_type.lower()] = parser_class