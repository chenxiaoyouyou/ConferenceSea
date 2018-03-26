# coding=utf-8
import redis
import logging
from logging.handlers import RotatingFileHandler
import threading
# logger = logging.getLogger()
# logger.setLevel(level=logging.DEBUG)
# file_log_handler = RotatingFileHandler('logs/log', maxBytes=1024*1024*100)
# # 创建记录日志的格式
# formater = logging.Formatter('%(levelname)s %(filename)s : %(lineno)d  %(message)s')
# file_log_handler.setFormatter(formater)
# logger.addHandler(file_log_handler)


#
# result = reS.set('name', 'fangzheng')
# print result
# result1 = reS.sadd('name1', 'heoolw')
# result2 = reS.sadd('name1', 'world')
# logger.error(result2)
# print result1
# print result2
# logger.debug('dfasdsaf')
def insert():
    reS = redis.StrictRedis(host='localhost', port=6379, db=0)
    for i in range(100000):
        reS.sadd('hello', i)


if __name__ == '__main__':

    for i in range(3):
        t = threading.Thread(target=insert)
        t.start()