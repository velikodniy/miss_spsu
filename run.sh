#!/usr/bin/env sh
nohup redis-server /etc/redis.conf &
uwsgi --socket 0.0.0.0:3031 --plugins python3 --protocol uwsgi --processes 4 --wsgi miss:app