import base64
import hashlib

from app.config import settings

ALPHABET = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"


def generate_short_code(url: str) -> str:
    """Детерминированный short_code на основе URL + соль времени.
    Для простоты: хэш → base62. В реальности лучше использовать
    случайность + проверку коллизий в БД."""
    import time

    payload = f"{url}:{time.time_ns()}"
    digest = hashlib.sha256(payload.encode()).digest()
    num = int.from_bytes(digest[:8], "big")

    result = []
    base = len(ALPHABET)
    for _ in range(settings.short_code_length):
        num, rem = divmod(num, base)
        result.append(ALPHABET[rem])
    return "".join(result)