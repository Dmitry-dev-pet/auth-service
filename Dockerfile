# Используем официальный образ Python
FROM python:3.13-slim

# Устанавливаем рабочую директорию
WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.lock .
COPY pyproject.toml .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.lock

# Копируем исходный код
COPY app/ app/

# Указываем команду для запуска приложения
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]