# Шаг 1: сгенерировать начальную миграцию
cd backend
alembic revision --autogenerate -m "initial_schema"

# Шаг 2: применить
alembic upgrade head

# Шаг 3: проверить что схема актуальна (в CI)
alembic check   # выдаст ошибку если есть незамигрированные изменения