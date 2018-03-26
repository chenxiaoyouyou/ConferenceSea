# coding=utf-8
import logging
from logging.handlers import RotatingFileHandler

# 配置日志功能
# 创建日志对象
logger = logging.getLogger()
# 设定等级
logger.setLevel(level=logging.DEBUG)
# 添加handler
file_handler = RotatingFileHandler('logs/log', maxBytes=1024*1024*100, backupCount=5)
# 设定日志格式
formater = logging.Formatter('%(levelname)s %(filename)s : %(lineno)d  %(message)s')
file_handler.setFormatter(formater)
# 为logger对象添加格式
logger.addHandler(file_handler)