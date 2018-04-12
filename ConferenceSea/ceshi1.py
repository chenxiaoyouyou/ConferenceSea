import pymysql

con = pymysql.connect(host='localhost', port=3306, database='conference', user='root', password='mysql', charset='utf8')
from gain_speakers import Speaker

speaker = Speaker()
speaker.interested = 'inte'
speaker.specialities = ''
speaker.name = 'xiaoming'
speaker.url = 'htto'
speaker.position = 'processor'



sql = """insert into speakers(url, name, position, specialties, interested) VALUES ('%s', '%s', '%s', '%s', '%s')""" % (speaker.url, speaker.name, speaker.position, speaker.specialities, speaker.interested)
print sql
cur = con.cursor()
cur.execute(sql)
con.commit()
cur.close()
con.close()