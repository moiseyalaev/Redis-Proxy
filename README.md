# Redis-Proxy
A transparent Redis proxy as an HTTP web service

## Consideration for Deployment
When deploying a Flask application to a production environment, it's best to use a WSGI (Web Server Gateway Interface) server along with a web server. This is because Flask's built-in server does not handle concurrency well and isn't optimized for performance or security which are essential in production. 

A simple to WSAI to get started with is gunicorn, however, technologies like Nginx and Apache can further help to distrubute client requests and mangle SSL/TLS for HTTPS communication.

## Consideration for Local Cache Implementation
After a bit of deliberation, three general paths emerged for implementing the local cache, each with its own level of granularity and control over details.

1. **Dictionary with a Doubly Linked List**:
   This approach is the most granular and would require us to define our own Node class with references to the previous and next nodes. Using this definition, we would manage a doubly linked list to keep track of the order of access for eviction purposes. A separate dictionary would hold the actual key-value pairs. This approach provides the most control but requires a significant amount of manual management and additional code to ensure correct behavior, which could potentially introduce bugs or maintenance challenges.

2. **Ordered Dictionary**:
   Utilizing Python's `collections.OrderedDict` provides a middle ground. The OrderedDict maintains the order of keys based on when they were last accessed, which simplifies the implementation of LRU eviction. For global expiry, timestamps would be stored alongside the values, and a routine would check these timestamps whenever a key is accessed to see if the value has expired. This approach is straightforward, doesn't introduce additional dependencies, and requires less manual management compared to the first approach.

3. **ThirdParty Dependencies: `redis_cache.RedisCache` and `functools.lru_cache`**:
   Leveraging third-party libraries can significantly simplify the implementation of the caching layer. These libraries are abstract away the lower-level details and provide a higher-level, more convenient interface to work with caching. With that said the major cons lie in needing to mange the dependancy versioning and any bugs it may present. In addtion, control and tailorization to specific needs are  scarificed for ease of use.

Conclusion: I choose to go the route of implimenting my own Ordered Dicitonary since it allowed me to have a suitable level of control for future iterations of the project without requiring most of my development efforts to go towards manging the local cache class.


## If node expired

we pop the key, val pair from the dictionary and then we 