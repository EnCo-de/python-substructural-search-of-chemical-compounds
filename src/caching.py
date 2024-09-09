import redis
import json

# Connect to Redis
redis_client = redis.Redis(host='redis', port=6379, db=0,
                           protocol=3, decode_responses=True)
# url_connection = redis.from_url("redis://localhost:6379?decode_responses="
#                                 "True&health_check_interval=2&protocol=3")


def get_cached_result(key: str):
    result = redis_client.get(key)
    if result:
        return json.loads(result)
    return None


def set_cache(key: str, value: dict, expiration: int = 60):
    redis_client.setex(key, expiration, json.dumps(value))
