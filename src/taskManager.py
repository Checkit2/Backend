import redis
class TaskManager:
    def __init__(self):
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        pass

    def newTask(self):
        self.redis.lpush('jobs', "job_id")
        pass

    def getTask():
        pass
    
    def removeTask():
        pass
nt = TaskManager()
nt.newTask()