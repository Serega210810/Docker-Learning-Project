# ====== STAGE 1: Сборка зависимостей ======
FROM python:3.11-slim AS builder

WORKDIR /build

# Копируем только requirements — это отдельный слой кэша
COPY requirements.txt .

# Устанавливаем зависимости в отдельную папку
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ====== STAGE 2: Финальный образ ======
FROM python:3.11-slim

# Переменные окружения для Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# Создаём непривилегированного пользователя (безопасность!)
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser

WORKDIR /app

# Копируем зависимости из builder-стадии (меньше размер образа)
COPY --from=builder /install /usr/local

# Копируем код приложения
COPY ./app ./app

# Меняем владельца на appuser
RUN chown -R appuser:appuser /app

# Переключаемся на непривилегированного пользователя
USER appuser

# Пробрасываем порт (документация, не обязателен для работы)
EXPOSE 8000

# Healthcheck — Docker сам проверяет, живо ли приложение
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/docs')" || exit 1

# Команда запуска
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]