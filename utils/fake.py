'''Начальная подготовка базы данных'''
from redis import Redis


COUNT = 0 # Число девушек
R = Redis()

R.flushall()

with open('girls.csv', encoding='cp1251') as f:
    for k, info in enumerate(f):
        info = info.split(';')
        R.set('girl:'+str(k+1)+':faculty', info[1].strip().encode('utf-8'))
        R.set('girl:'+str(k+1)+':name', info[2].strip().encode('utf-8'))
        R.set('girl:'+str(k+1), 0)
        COUNT += 1
        print(k+1, info[2])

R.set('girl:count', COUNT)

R.set('voting', 1)

with open('secret.txt') as f:
    R.set('secret', f.readline().strip())
with open('admin_key.txt') as f:
    R.set('admin_key', f.readline().strip())

for num in range(10000):
    R.set('code:'+str(num), 0)
