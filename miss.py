from datetime import datetime
from uuid import uuid4

from flask import Flask, request, render_template, session, redirect, url_for, jsonify, flash, Response
from redis import Redis, WatchError

import base
from config import SECRET, TIMEOUT_IP, TIMEOUT, DEBUG, ADMIN_KEY

app = Flask(__name__)
r = Redis()


def is_real_data():
    real = r.get('real')
    return real is not None and int(real) == 1


def is_voting_started():
    v = r.get('voting')
    return v is not None and int(v) == 1


def toggle_voting(v=None):
    if v is None:
        v = not is_voting_started()
    voting = 1 if v else 0
    r.set('voting', voting)


def log(sid, code, message):
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr
    m = datetime.utcnow().isoformat() + ': ' + ip + ': ' + sid + ': ' + str(decode(code)) + ': ' + message
    r.lpush('log', m)


def get_stat(ids=None):
    if ids is None:
        count = int(r.get('girl:count'))
        return get_stat(range(1, count))

    girls = []
    for k in ids:
        v = r.get('girl:%d' % k)
        if v is None:
            return None
        girls.append({
            'girlid': k,
            'name': r.get('girl:%d:name' % k).decode('utf-8'),
            'faculty': r.get('girl:%d:faculty' % k).decode('utf-8'),
            'votes': int(v),
        })
        total = sum(g['votes'] for g in girls)
        for g in girls:
            g['percent'] = int(g['votes'] / total * 100) if total > 0 else 0
    return girls


def decode(code):
    ids = []
    k = 1
    while code > 0:
        if code % 2 != 0:
            ids.append(k)
        k += 1
        code //= 2
    return ids


@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}


# Страница для голосования
@app.route('/')
def index():
    # Поставить куки с UUID, если ещё не стоит
    if 'id' not in session:
        sid = uuid4().hex
        session['id'] = sid

    # Отобразить страницу со списком участниц
    # Если голосование не идёт, отобразить результаты и написать, что голосование не идёт
    girls = get_stat()
    return render_template('index.html',
                           girls=girls,
                           voting_started=is_voting_started(),
                           real_data=is_real_data())


@app.route('/vote-prepare')
def vote_prepare():
    ids = [int(i) - 1 for i in request.args.getlist('girls')]
    code = sum(2 ** k for k in ids)
    return redirect(url_for('vote', girlcode=code))


# Страничка с формой для ввода кода
@app.route('/vote/<int:girlcode>', methods=['GET', 'POST'])
def vote(girlcode):
    if girlcode == 0:
        flash('Выберите хотя бы одну участницу', 'message')
        return redirect(url_for('index'))

    ids = decode(girlcode)
    girls = get_stat(ids)
    if girls is None:
        flash('Одна из участниц не существует', 'error')
        return redirect(url_for('index'))

    # По GET подтверждение голосования
    if request.method == 'GET':
        # Началось ли голосование
        if not is_voting_started():
            flash('Голосование ещё не началось', 'message')
            return redirect(url_for('index'))
        return render_template('vote.html', girls=girls)

    # По POST голосование

    # Если нет куки — написать, что нужны???
    # Поставить куки с UUID, если ещё не стоит
    sid = 0
    try:
        sid = session['id']
    except KeyError:
        log(sid, girlcode, 'NOCOOKIES')
        flash('Для голосования требуется включить куки', 'error')
        return redirect(url_for('index'))

    # Если счётчик неверных номеров с этого куки > 0, вывести сообщение о паузе
    if r.get('cookie:' + sid) == b'1':
        flash('В прошлый раз вы ввели неправильный код, подождите %d секунд' % TIMEOUT, 'error')
        return redirect(url_for('vote', girlcode=girlcode))

    # Если счётчик неверных номеров с этого IP > 5, вывести сообщение о паузе
    if request.headers.getlist("X-Forwarded-For"):
        ip = request.headers.getlist("X-Forwarded-For")[0]
    else:
        ip = request.remote_addr

    if r.get('ipban:' + ip) == b'1':
        flash('Похоже на подбор номеров, подождите %d секунд' % TIMEOUT_IP, 'error')
        return redirect(url_for('vote', girlcode=girlcode))

    # Началось ли голосование
    if not is_voting_started():
        flash('Голосование ещё не началось', 'message')
        return redirect(url_for('vote', girlcode=girlcode))
    print('*')
    code = request.form['code']
    print('*')
    if code.strip() == '':
        flash('Вы забыли ввести код', 'error')
        return redirect(url_for('vote', girlcode=girlcode))

    code_key = 'code:' + code
    girl_keys = ['girl:' + str(girl['girlid']) for girl in girls]

    with r.pipeline() as pipe:
        while True:
            try:
                pipe.watch(code_key, *girl_keys)
                votes = pipe.get(code_key)

                if votes is None:
                    # Увеличить счётчик неверных голосов с этого куки с таймаутом
                    if int(r.incr('ip:' + ip)) > 5:
                        log(sid, girlcode, 'IPBAN (%s)' % code)
                        r.set('ipban:' + ip, 1, ex=TIMEOUT_IP)
                        flash('Похоже на подбор номеров (вы сможете голосовать через %d секунд)' % TIMEOUT_IP, 'error')
                        return redirect(url_for('vote', girlcode=girlcode))
                    log(sid, girlcode, 'NOCODE (%s)' % code)
                    r.set('cookie:' + sid, 1, ex=TIMEOUT)
                    flash('Нет такого кода (вы сможете голосовать через %d секунд)' % TIMEOUT, 'error')
                    return redirect(url_for('vote', girlcode=girlcode))

                votes = int(votes)
                if votes > 0:
                    log(sid, girlcode, 'DOUBLEVOTING (%s)' % code)
                    flash('Вы уже голосовали', 'error')
                    return redirect(url_for('vote', girlcode=girlcode))

                votes += 1

                pipe.multi()
                pipe.set(code_key, votes)
                for girl_key in girl_keys:
                    pipe.incr(girl_key)
                pipe.execute()
                break
            except WatchError:
                continue
    log(sid, girlcode, 'OK (%s)' % code)
    flash('Ваш голос учтён', 'message')
    return redirect(url_for('index'))


# Страница со статистикой
@app.route('/stat')
def stat():
    return render_template('stat.html')


# Статистика (возвращает JSON)
@app.route('/stat-data')
def stat_data():
    # Вернуть JSON с именем, факультетом, числом голосов
    return jsonify(get_stat())


# Админка
@app.route('/admin', methods=['GET', 'POST'])
def admin():
    # Единственная кнопка — остановить или запустить голосование
    # Показывать статус голосования
    if request.method == 'GET':
        return render_template('admin.html',
                               voting_started=is_voting_started(),
                               real_data=is_real_data())

    action = request.form.get('action', 'toggle_voting')

    # Проверить код админа
    if request.form.get('admin_key', None) != ADMIN_KEY and action != '':
        flash('Неверный код администратора', 'error')

    if action == 'toggle_voting':
        toggle_voting()
    elif action == 'show_log':
        logs = '\n'.join([l.decode('utf-8') for l in r.lrange('log', 0, -1)])
        return Response(logs, mimetype='text/plain')
    elif action == 'load_real':
        base.load_real_data()

    return redirect(url_for('admin'))


app.secret_key = SECRET
app.config['SESSION_TYPE'] = 'filesystem'
app.debug = DEBUG

base.load_fake_data()
toggle_voting(False)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
