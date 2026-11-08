from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app import cache
from app.config import settings
from app.database import get_db, init_db
from app.models import Link
from app.schemas import ShortenRequest, ShortenResponse, StatsResponse
from app.utils import generate_short_code


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    await init_db()
    yield
    # shutdown — закрываем соединения
    await cache.redis.aclose()


app = FastAPI(title="URL Shortener", version="1.0.0", lifespan=lifespan)


@app.post("/shorten", response_model=ShortenResponse)
async def shorten(payload: ShortenRequest, db: AsyncSession = Depends(get_db)) -> ShortenResponse:
    original = str(payload.url)

    # 1. Проверяем кэш — может, уже сокращали такой URL
    cached_code = await cache.get_from_cache(f"orig:{original}")
    if cached_code:
        return ShortenResponse(
            short_code=cached_code,
            short_url=f"{settings.base_url}/{cached_code}",
            original_url=original,
        )

    # 2. Генерируем код с защитой от коллизий
    for _ in range(5):
        code = generate_short_code(original)
        existing = await db.execute(select(Link).where(Link.short_code == code))
        if existing.scalar_one_or_none() is None:
            break
    else:
        raise HTTPException(status_code=500, detail="Не удалось сгенерировать уникальный код")

    link = Link(short_code=code, original_url=original)
    db.add(link)
    await db.commit()

    # 3. Кладём в кэш для быстрого поиска
    await cache.set_to_cache(f"code:{code}", original, ttl=24 * 3600)
    await cache.set_to_cache(f"orig:{original}", code, ttl=24 * 3600)

    return ShortenResponse(
        short_code=code,
        short_url=f"{settings.base_url}/{code}",
        original_url=original,
    )


@app.get("/{short_code}")
async def redirect(short_code: str, db: AsyncSession = Depends(get_db)) -> RedirectResponse:
    # 1. Сначала кэш
    cached_url = await cache.get_from_cache(f"code:{short_code}")
    if cached_url:
        await cache.increment_stat(f"stat:{short_code}")
        return RedirectResponse(cached_url)

    # 2. Потом БД
    result = await db.execute(select(Link).where(Link.short_code == short_code))
    link = result.scalar_one_or_none()
    if link is None:
        raise HTTPException(status_code=404, detail="Ссылка не найдена")

    await cache.set_to_cache(f"code:{short_code}", link.original_url, ttl=24 * 3600)
    await cache.increment_stat(f"stat:{short_code}")
    return RedirectResponse(link.original_url)


@app.get("/stats/{short_code}", response_model=StatsResponse)
async def stats(short_code: str, db: AsyncSession = Depends(get_db)) -> StatsResponse:
    result = await db.execute(select(Link).where(Link.short_code == short_code))
    link = result.scalar_one_or_none()
    if link is None:
        raise HTTPException(status_code=404, detail="Ссылка не найдена")

    clicks = await cache.get_stat(f"stat:{short_code}")
    return StatsResponse(
        short_code=short_code,
        original_url=link.original_url,
        clicks=clicks,
    )