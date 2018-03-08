upstream miss_spsu_uwsgi {
    server 127.0.0.1:3031;
}

server {
    listen 80;
    server_name miss.spsu.ru;

    location / {
        uwsgi_pass miss_spsu_uwsgi;
        include uwsgi_params;
    }
}