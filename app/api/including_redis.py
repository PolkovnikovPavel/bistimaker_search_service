import datetime
import redis
from app.api.identification import REDIS_HOST

# Подключаемся к Redis
redis_client = redis.StrictRedis(host=REDIS_HOST, port=6379, db=0)


def set_cache(key: str, id: str, data, timer: int = 900):
    if isinstance(data, list):
        set_list_cache_to_redis(key, id, data, timer)
    else:
        set_item_cache_to_redis(key, id, data, timer)


def set_item_cache_to_redis(key: str, id: str, data, timer: int = 900):
    bestiaries_dicts = dict(data._mapping)
    redis_client.setex(f'{key}_{id}', timer, str(bestiaries_dicts))


def set_list_cache_to_redis(key: str, id: str, data, timer: int = 900):
    bestiaries_dicts = [dict(user._mapping) for user in data]
    redis_client.setex(f'{key}_{id}', timer, str(bestiaries_dicts))


def get_cache_from_redis(key: str, id: str):
    cached_data = redis_client.get(f'{key}_{id}')
    if cached_data:
        return eval(cached_data)
    else:
        return None


def delete_cache_from_redis(key: str, id: str):
    redis_client.delete(f'{key}_{id}')

