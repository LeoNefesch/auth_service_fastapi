# Cервис авторизации
*Проект написан в ОС Windows 10 Pro. Установлен Docker Desktop.

Стек:
- Python 3.12.6
- FastAPI
- PostgreSQL
- Docker
- Redis

Для автоматизации кодстайлинга используется `pre-commit`.

Установка хуков pre-commit:
```commandline
pre-commit install
```
Первичный запуск pre-commit:
```commandline
pre-commit run --all-files
```

## Локальный запуск:
_Примечание: все команды выполнять из корневой директории проекта._

Обновить pip:
```commandline
python.exe -m pip install --upgrade pip
```
Установить библиотеки:
```commandline
pip install -r requirements.txt
```
Запустить БД (в контейнере):
```commandline
docker compose up -d db
```
Запустить redis (в контейнере):
```commandline
docker compose up -d redis
```

В другой консоли выполнить команду для применения миграций:
```commandline
alembic upgrade head
```
и запустить веб-сервер:
```commandline
uvicorn app.main:app
```
swagger доступен в браузере по адресу `http://127.0.0.1:8000/docs`

## Запуск в контейнерах:
_Примечание: все команды выполнять из корневой директории проекта._

Сборка образов:
```commandline
docker compose build
```
Запуск контейнеров:
```commandline
docker compose up -d
```
swagger доступен в браузере по адресу `http://localhost:8000/docs`

Остановка контейнеров (`-v` означает удаление томов с данными):
```commandline
docker compose down -v
```
