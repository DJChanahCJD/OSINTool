import logging
import os
from datetime import datetime, timedelta

# 配置日志记录
def setup_logger(log_file='log.txt', log_level=logging.INFO):
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)

    # 创建文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(log_level)

    # 创建格式化器并添加到处理器，包含 API 信息
    formatter = logging.Formatter('%(asctime)s - %(api_info)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)

    # 将处理器添加到 logger
    logger.addHandler(file_handler)

    # 清理 7 天前的日志
    clean_logs(log_file)

    return logger

# 清理 7 天前的日志
def clean_logs(log_file='log.txt'):
    if os.path.exists(log_file):
        now = datetime.now()
        seven_days_ago = now - timedelta(days=7)
        new_logs = []
        with open(log_file, 'r', encoding='utf-8') as f:
            for line in f:
                try:
                    # 解析日志行中的时间
                    log_time_str = line.split(' - ')[0]
                    log_time = datetime.strptime(log_time_str, '%Y-%m-%d %H:%M:%S,%f')
                    if log_time >= seven_days_ago:
                        new_logs.append(line)
                except (IndexError, ValueError):
                    # 如果解析失败，保留该行日志
                    new_logs.append(line)

        # 将过滤后的日志重新写入文件
        with open(log_file, 'w', encoding='utf-8') as f:
            f.writelines(new_logs)