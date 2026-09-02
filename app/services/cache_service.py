from cachetools import TTLCache

# Кеш за пазарни цени и индикатори (валиден 5 минути / 300 секунди)
stock_cache = TTLCache(maxsize=100, ttl=300)

# Кеш за AI анализи (валиден 30 минути / 1800 секунди)
ai_cache = TTLCache(maxsize=100, ttl=1800)