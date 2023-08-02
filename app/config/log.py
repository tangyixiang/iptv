import os
import time
from loguru import logger

# 日志的路径
log_path = os.path.join(os.getcwd(), "logs")
if not os.path.exists(log_path):
    os.mkdir(log_path)
# 日志输出的文件格式
log_path_format = os.path.join(log_path, f'ocs-iptv-{time.strftime("%Y-%m-%d")}.log')

logger.add(log_path_format, rotation="00:00", retention="5 days", enqueue=True)
