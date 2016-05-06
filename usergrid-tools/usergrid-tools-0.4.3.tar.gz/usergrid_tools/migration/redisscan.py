import redis
r = redis.Redis("localhost", 6379)
for key in r.scan_iter():
    print '%s: %s' % (r.ttl(key), key)

    if key[0:3] in ['v3:', 'v2', 'v1']:
        r.delete(key)

    elif ':visited' in key:
        r.delete(key)
