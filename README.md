# Useful_links
Сервис хранения полезных ссылок с фильтрацией и поиском.
WEB и API реализации.
## Автор:
Алексей Наумов ( algena75@yandex.ru )
## Используемые технолологии:
* Flask
* SQLite
* SQLAlchemy
* Bootstrap
* REST API
* Swagger
## Как запустить проект:
Клонировать репозиторий и перейти в него в командной строке:


```
git clone git@github.com:Algena75/useful_links.git
```

```
cd useful_links
```

Cоздать и активировать виртуальное окружение:

```
python3 -m venv venv
```

* Если у вас Linux/macOS

    ```
    source venv/bin/activate
    ```

* Если у вас windows

    ```
    source venv/scripts/activate
    ```

Установить зависимости из файла requirements.txt:

```
python3 -m pip install --upgrade pip
```

```
pip install -r requirements.txt
```
## Как запустить проект локально:
В корне проекта создать файл `.env` с настройками для базы данных, после чего выполнить:
```
flask run
```
Открыть `http://localhost:5000/`. Документация на API доступна по адресу `http://127.0.0.1:5000/api/docs`.