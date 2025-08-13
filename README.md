# Business Management

Упрощённая система управления бизнесом: пользователи, команды, задачи, оценки, встречи и календарь.

## Стек
- FastAPI
- SQLAlchemy + Alembic
- PostgreSQL
- Pydantic
- fastapi-users
- sqladmin
- Jinja2
- Uvicorn — сервер запуска
- Docker

## Склонируйте проект**
```bash
git clone 
```

## Создайте виртуальное окружение и активируйте его**
```bash
python -m venv venv
```
```bash
. venv/Scripts/activate
```

## Запуск через Docker
```bash
cp .env.example .env
docker-compose up --build
docker exec -it business_api alembic upgrade head
```
Откройте: http://127.0.0.1:8000

## Структура
```
app/
  api/
    v1/
      routes.py
  core/
    config.py
  db/
    session.py
  models/
    base.py
    evaluation.py
    meeting.py
    task.py
    team.py
    user.py
  web/
    templates/
      base.html
      index.html
  main.py
```

