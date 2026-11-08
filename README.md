# 🔗 URL Shortener

Асинхронный сокращатель ссылок на **FastAPI** с кэшированием в **Redis** и хранением в **PostgreSQL**. Полностью контейнеризован с помощью **Docker Compose**.

![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?logo=postgresql&logoColor=white)
![Redis](https://img.shields.io/badge/Redis-7-DC382D?logo=redis&logoColor=white)

---

## ✨ Возможности

- ⚡ **Асинхронный FastAPI** — высокая производительность
- 🗄️ **PostgreSQL** — надёжное хранение ссылок
- ⚡ **Redis** — кэширование для мгновенных редиректов + счётчик кликов
- 🐳 **Docker Compose** — запуск одной командой
- 🔒 **Non-root пользователь** в контейнере — безопасность
- 🏥 **Healthchecks** — автоматический мониторинг сервисов
- 📊 **Swagger UI** — интерактивная документация API

---

## 🚀 Быстрый старт

### Требования

- [Docker](https://docs.docker.com/get-docker/) (24.0+)
- [Docker Compose](https://docs.docker.com/compose/install/) (v2.0+)

### Установка и запуск

1. **Клонируйте репозиторий:**
bash
git clone https://github.com/Serega210810/Docker-Learning-Project.git
cd Docker-Learning-Project

2. **Скопируйте `.env.example` в `.env`:**
   ```bash
   cp .env.example .env

3. Запустите все сервисы:
 docker compose up -d --build

4. Откройте документацию API:
Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc

Остановка
# Остановить контейнеры (данные сохранятся)
docker compose down

# Остановить и удалить volumes (БД очистится!)
docker compose down -v

Примеры использования
1. Создать короткую ссылку

curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com"}'


Ответ:
{
  "short_code": "aB3xK9",
  "short_url": "http://localhost:8000/aB3xK9",
  "original_url": "https://github.com"
}


Перейти по короткой ссылке
curl -I http://localhost:8000/aB3xK9

Ответ: HTTP/1.1 307 Temporary Redirect → Location: https://github.com

3. Посмотреть статистику
curl http://localhost:8000/stats/aB3xK9


Ответ:

{
  "short_code": "aB3xK9",
  "original_url": "https://github.com",
  "clicks": 42
}

Как это работает
1. Пользователь отправляет POST /shorten с длинным URL
2. FastAPI проверяет кэш в Redis — если ссылка уже сокращалась, возвращает готовый код
3. Если нет — генерирует уникальный short_code, сохраняет в PostgreSQL и кэширует в Redis
4. При переходе по /{short_code} приложение сначала ищет в Redis (мгновенно), потом в БД
5. Счётчик кликов хранится в Redis для высокой скорости записи

🐳 Docker-конфигурация
Dockerfile
Использует multi-stage build для минимизации размера образа:

# Stage 1: Сборка зависимостей
FROM python:3.11-slim AS builder
WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# Stage 2: Финальный образ
FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin appuser
WORKDIR /app
COPY --from=builder /install /usr/local
COPY ./app ./app
RUN chown -R appuser:appuser /app
USER appuser
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/docs')" || exit 1
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

⚙️ Переменные окружения
Создайте файл .env на основе .env.example:
DATABASE_URL=postgresql+asyncpg://app:app@db:5432/shortener
REDIS_URL=redis://redis:6379/0
BASE_URL=http://localhost:8000
SHORT_CODE_LENGTH=6

Ключевые особенности:
✅ Multi-stage build — уменьшает размер образа (~150 МБ вместо ~900 МБ)
✅ Non-root пользователь — безопасность контейнера
✅ Кэширование слоёв — requirements.txt копируется отдельно от кода
✅ Healthcheck — Docker автоматически проверяет здоровье приложения
✅ Slim-образ — минимальная поверхность для атак

ВАЖНО: КОД НЕ БЫЛ ТЕСТИРОВАН ПЕРЕД ВЫГРУЗКОЙ НА GITHUB

👤 Автор
Serega210810
GitHub: @Serega210810