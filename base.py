from redis import Redis

from config import NUMBERS_FILE, GIRLS_FILE

r = Redis()


def _load_girls_list():
    girls_count = 1
    with open(GIRLS_FILE, mode='r', encoding='utf-8') as f:
        for info in f:
            info = info.strip()
            if not info:
                continue
            info = info.split(',')
            r.set(f'girl:{girls_count}:name', info[0].strip())
            r.set(f'girl:{girls_count}:faculty', info[1].strip())
            r.set(f'girl:{girls_count}', 0)
            girls_count += 1
    r.set('girl:count', girls_count)


def load_real_data():
    r.flushall()
    with open(NUMBERS_FILE) as f:
        for num in f:
            num = num.strip()
            if num:
                r.set(f'code:{num}', 0)
    _load_girls_list()
    r.set('real', 1)


def load_fake_data():
    r.flushall()
    for num in range(10000):
        r.set(f'code:{num}', 0)
    _load_girls_list()
    r.set('real', 0)
