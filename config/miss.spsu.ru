upstream miss_serv {
    server unix:/tmp/miss.sock;
}

server {
    listen 80;
    server_name miss.spsu.ru;

    location / {
        uwsgi_pass miss_serv;
        include uwsgi_params;
    }

    location /static/ {
        root /srv/miss_spsu/static/;
    }
}		