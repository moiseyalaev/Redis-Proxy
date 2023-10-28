import redis

class BackingRedis:
    def __init__(self, host = 'localhost', port = 6379):
        try:
            self.redis_client = redis.Redis(host = host, port = port)
        except redis.ConnectionError:
            raise Exception("Unable to connect to Redis")

    # wrapper around redis get method for future extensibility
    def get(self, key: str):
      return self.redis_client.get(key)
