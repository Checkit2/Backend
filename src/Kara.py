import redis
redis = redis.Redis(host='localhost', port=6379, db=0)
while True:
    while(redis.llen('jobs')!=0):
        print(redis.lpop('jobs'))
    import time
    time.sleep(10)