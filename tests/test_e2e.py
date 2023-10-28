import os
import unittest
import requests
import redis
import time
import logging 
from concurrent.futures import ThreadPoolExecutor
class TestIntegration(unittest.TestCase):
    # Initalize logging
    logging.basicConfig(level = logging.WARNING)
    LOGGER = logging.getLogger(__name__)

    BASE_URL = f"http://{os.environ.get('PROXY_HOST', 'localhost')}:{os.environ.get('PROXY_PORT', '8000')}"

    def setUp(self):
        redis_host = os.environ.get('REDIS_HOST', 'localhost')
        redis_port = int(os.environ.get('REDIS_PORT', 6379))
        self.redis_client = redis.Redis(host = redis_host, port = redis_port, db = 0)
        self.redis_client.flushall() 

    def test_http_web_service(self):
        key, value = 'test_key', 'test_value'
        self.redis_client.set(key, value)

        response = requests.get(f'{self.BASE_URL}/{key}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['value'], value)
        
        # Check that we get a 204 when get with a nonexistent key
        response = requests.get(f'{self.BASE_URL}/nonexistent_key')
        self.assertEqual(response.status_code, 204)

    def test_cached_get(self):
        key, value = 'cached_key', 'cached_value'
        self.redis_client.set(key, value)

        # First request should hit Redis backing 
        response = requests.get(f'{self.BASE_URL}/{key}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['value'], value)

        # Second request should hit the local cache if the proxy's item is deleted
        self.redis_client.delete(key) 
        response = requests.get(f'{self.BASE_URL}/{key}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['value'], value)

    def test_global_expiry(self):
        key, value = 'expiring_key', 'expiring_value'
        self.redis_client.set(key, value)

        # Initial request should store the value in the local cache
        response = requests.get(f'{self.BASE_URL}/{key}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()['value'], value)

        expiry_time = int(os.environ.get('CACHE_EXPIRY_TIME', 5))  # Default to 5 secs
        if expiry_time > 10:  # Assuming 1 minute is a reasonable maximum for testing
            self.LOGGER.warning(
                f"Cache expiry time is too long for testing. Consider a time less than 10 secs"
            )

        # Wait for the expiry time plus a little extra
        time.sleep(expiry_time+ 1 )

        # Now the value should be expired in the local cache, and not found in Redis
        response = requests.get(f'{self.BASE_URL}/{key}')
        self.assertEqual(response.status_code, 204)

    def test_lru_eviction(self):
        cache_capacity = int(os.environ.get('CACHE_CAPACITY', 100))  # default to 100 keys

        if cache_capacity > 100:
            self.LOGGER.warning(
                f"Cache capacity is too large for testing. Consider a capacity less than 100"
            )

        # Fill the cache and then add one more item to trigger eviction
        for i in range(cache_capacity + 1): 
            key = f'key{i}'
            value = f'value{i}'
            self.redis_client.set(key, value)
            requests.get(f'{self.BASE_URL}/{key}')

        # Now the first item should be evicted
        response = requests.get(f'{self.BASE_URL}/key0')
        self.assertEqual(response.status_code, 204)

    def test_parallel_concurrent_requests(self):
         with ThreadPoolExecutor(max_workers = 10) as executor:
            futures = []
            for i in range(10):
                future = executor.submit(requests.get, f'{self.BASE_URL}/key{i}')
                futures.append(future)

            # Wait for all futures to complete and expect all return a 200
            for future in futures:
                result = future.result()
                self.assertEqual(result.status_code, 200)

    def test_rate_limiting(self):
        max_clients = int(os.environ.get('MAX_CLIENTS', 20))
        # Exceed the max client limit
        num_requests = max_clients + 10

        with ThreadPoolExecutor() as executor:
            futures = []
            for i in range(num_requests):
                future = executor.submit(requests.get, f'{self.BASE_URL}/key{i}')
                futures.append(future)
            
            for future in futures:
                response = future.result()
                # Eventually we expect a 429
                if response.status_code != 200:
                    self.assertEqual(response.status_code, 429)
