# coding=utf-8
import pymysql
mysql_cli = pymysql.connect(host='localhost', port=3306, database='conference', user='root', password='mysql',
                                 charset='utf8')
cursor = mysql_cli.cursor()
cursor.execute('select * from organizers')
print cursor.fetchone()