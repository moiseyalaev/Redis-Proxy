from os import environ
from flask import Flask, request, jsonify
from cache import Cache
# import src.cache as cache

# Create constant variables that are assigned on setup

# Creating instances of the app and cache
app = Flask(__name__)
cache = Cache(
    environ.get('REDIS_HOST', 'localhost'), # default to localhost
    int(environ.get('REDIS_PORT', 6379)), # default port to 6379
)

# Define get request
@app.route('/<key>', methods=['GET'])
def get(key):
    value = cache.get(key)
    if value: return jsonify({'value': value})

    # Otherwise, return a 204 status error to indicate that the server successfully
    # excuted the request but the is no value to send in the response body
    return ('', 204)

if __name__ == '__main__':
    app.run()
