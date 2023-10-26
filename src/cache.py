from os import environ
from backing_redis import BackingRedis
from collections import OrderedDict
from datetime import datetime, timedelta

class Cache:
    def __init__(self, host, port):
        self.backing_redis = BackingRedis(host=host, port=port)
        self.local_cache = OrderedDict()
        self.expiry_time = int(environ.get('CACHE_EXPIRY_TIME', 300)) # Default to 5 mins
        self.capacity = int(environ.get('CACHE_CAPACITY', 1000))  # Default to 1000 keys

    def get(self, key: str):
        # Check if the item is in the cache and not expired
        if key in self.local_cache:
            item, timestamp = self.local_cache.pop(key)

            if datetime.now() - timestamp < self.expiry_time:
                # Push item to the front to show that it was most recently used
                self.local_cache[key] = (item, timestamp)
                return item

        # Otherwise, check backing Redis instance
        item = self.backing_redis.get(key)
        if item is not None:
            # Insert the item into the cache and ensure the cache's size
            self.local_cache[key] = (item, datetime.now())
            self._ensure_cache_size()
            
        return item

    def _ensure_cache_size(self):
        # Evict least recently used items if the cache is over capacity
        while len(self.local_cache) > self.capacity:
            self.local_cache.popitem(last=False)  # LRU item is at the beginning
