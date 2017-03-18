miss_spsu
=========

Система онлайн-голосования для конкурса «Мисс ПГУ — 2017».

Система была сделана для одноразового использования за пару дней, поэтому
нет тестов, а кое-где код можно бы и улучшить (да, я не горжусь им).

Развёртывание
-------------

Система написана на Python с использованием фреймворка Flask.
Для развёртывания требуются:

- Python 3 + библиотеки из `requirements.txt`.
- HTTP-сервер Nginx (можно и другой). Конфигурационный файл — `config/miss.spsu.ru`.
- Сервер uWSGI. Конфигурационный файл — `config/miss.xml`.
- СУБД Redis. (Если не знакомы — рекомендую полистать «Маленькую книжку о Redis».)

Для теста достаточно только Python 3 и Redis. Просто запускаем `miss.py`.

Для работы системы необходимо подготовить уникальные номера для голосования,
инициализировать базу и настроить приложение.

Для этого:

1. Генерируются номера (скрипт `utils/generate.py`, результат записывается в `numbers.txt`).
2. Заполняется список участниц (файл `utils/girls.csv`).
3. Заполняется уникальный ключ для подписи сессии (файл `utils/secret.txt`).
4. Заполняется пароль администратора (файл `utils/admin_key.txt`).
5. Подготавливается база (скрипт `prepare_base.py`). Для теста можно запустить `fake.py` — вместо номерков 
6. Генерируются и печатаются билетики (в документе `tickets/Мисс ПГУ.docm` запускаем макрос Numbers и указываем путь к numbers.txt; документ рассчитан на 550 билетков).
7. Запускаем серверы, всё должно работать. Для фейковых данных голосование сразу включено.

Для работы достаточно минимального дроплета на Digital Ocean (c 512 Мбайт ОЗУ без подкачки).

Система успешно выдержала запросы от приблизительно 500 человек в течение нескольких минут.

Работа
------

По адресу «/» находится сама голосовалка. Дизайн рассчитан на мобильные устройства.
На десктопе всё плохо. Если головование включено, то можно голосовать за несколько участниц.

По адресу «/stat» — статистика для вывода на проектор. Рассчитана на разрешение 800×600. Обновляется автоматически каждый две секунды.

По адресу «/admin» — включение и выключение голосования.

CSS- и JS-фреймворки не самые лёкие, так что страничка в первый раз может загружаться несколько секунд
через мобильный интернет. (Да, это можно оптимизировать.)

Защита от накруток
------------------

При попытке подобрать номер сначала блокируется на 20 секунд браузер. Если продолжать — то на 90 секунд блокируется весь IP.

В Redis ведётся лог (ключ `log`). Записывается время, ключ сессии, выбор, ответ сервера. По логам можно отследить «накрутки» голосов.

Дамп базы с прошлого конкурса — `data/dump.rdb`.

Планы на будущее
----------------

Что-то мне не очень хочется ещё раз что-то в спешке писать для этого конкурса.