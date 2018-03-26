import pymysql
mysql_cli = pymysql.connect(host='localhost', port=3306, database='conference', user='root', password='mysql',
                                 charset='utf8')

paras = ['title', 'current_url', '1990-03-20', '1990-03-20', 'area', 'organizer', 'specialities']
cursor = mysql_cli.cursor()
# a = cursor.execute('insert into conference (title, url, start_date, end_date, area, organized, specialties) VALUES (%s, %s, %s, %s, %s, %s, %s)', paras)
mysql_cli.commit()
paras2 = ['current_url',]
cursor.execute('select id from conference where url = %s', paras2)
print cursor.fetchall()

# print a