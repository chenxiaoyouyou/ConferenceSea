from multiprocessing import Pool
import time
class a:
    def helle(self):
        print ('start')
        time.sleep(2)
        print ('end')

def d(i):
    v = a()
    v.helle()
    print ('hello')
    time.sleep(2)
    print ('world')


po = Pool(2)
for i in range(7):
    # b = a()
    # c = a.helle
    po.apply_async(d,(i,))
    print i

po.close()
po.join()