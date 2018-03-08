FROM alpine:latest
MAINTAINER Vadim Velikodniy <vadim@velikodniy.name>

# Install Redis
RUN apk add --no-cache --update redis && \
    mkdir /data && \
    echo -e "dir /data/" >> /etc/redis.conf && \
    echo -e "dbfilename miss_spsu.rdb" >> /etc/redis.conf

# Install Python3
RUN apk add --no-cache --update python3 && \
    python3 -m ensurepip && \
    rm -r /usr/lib/python*/ensurepip && \
    pip3 install --upgrade pip setuptools && \
    if [ ! -e /usr/bin/pip ]; then ln -s pip3 /usr/bin/pip ; fi && \
    if [[ ! -e /usr/bin/python ]]; then ln -sf /usr/bin/python3 /usr/bin/python; fi && \
    rm -r /root/.cache

# Install uwsgi
RUN apk add --no-cache --update uwsgi uwsgi-python3

# Install the app
RUN mkdir -p /srv/
WORKDIR /srv/

COPY requirements.txt /srv/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /srv/

EXPOSE 3031
VOLUME /data

CMD [ "sh",  "run.sh" ]