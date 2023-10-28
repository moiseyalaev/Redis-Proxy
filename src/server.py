from os import environ
from flask import Flask, jsonify, abort
from cache import Cache
from threading import Semaphore

# Creating instances of the app and cache
app = Flask(__name__)
semaphore = Semaphore(int(environ.get('MAX_CLIENTS', 20)))  # default of 20
cache = Cache(
    environ.get('REDIS_HOST', 'localhost'), # default to localhost
    int(environ.get('REDIS_PORT', 6379)), # default port to 6379
)

# Define get request
@app.route('/<key>', methods=['GET'])
def get(key):
    acquired = semaphore.acquire(blocking = False)
    if not acquired:
        abort(429)
    try:
        value = cache.get(key)
        if value: return jsonify({'value': value})

        # Otherwise, return a 204 status error to indicate that the server successfully
        # excuted the request but the is no value to send in the response body
        return ('', 204)
    finally:
        semaphore.release()

if __name__ == '__main__':
    app.run(
        host=environ.get('PROXY_HOST', '0.0.0.0'),
        port=int(environ.get('PROXY_PORT', 8000))
    )
