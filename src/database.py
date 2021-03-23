import mysql.connector
import redis

class database:
    def createTables(self):
        tables = [
            "CREATE TABLE IF NOT EXISTS `akp_users` ( `user_id` INT NOT NULL AUTO_INCREMENT , `user_name` TEXT NULL , `user_phone` TEXT NOT NULL , `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP , `updated_at` TIMESTAMP NOT NULL DEFAULT NOW() ON UPDATE now() , PRIMARY KEY (`user_id`)) ENGINE = InnoDB CHARSET=utf8 COLLATE utf8_persian_ci;",
        ]
        for table in tables:
            cursor = self.db.cursor()
            cursor.execute(table)
        if self.redis.set('tables', 'yes'):
            return True
        return False

    def getChecks(self, userid):
        return ''

    def getUser(self, userid):
        return ''

    def addUser(self, userid):
        return ''

    def isUserExists(self, userid):
        # q = "SELECT * FROM `akp_users` "
        return False
    
    def __init__(self, host, username, password, dbname):
        self.host = host
        self.username = username
        self.password = password
        self.dbname = dbname
        self.redis = redis.Redis(host='localhost', port=6379, db=0)
        self.db = mysql.connector.connect(
            host = self.host,
            user = self.username,
            password = self.password,
            database = self.dbname,
        )
        # Creating databases if not exists
        if self.redis.get('tables') == None: # If anything in sql queries changes redis should be restart
            self.createTables()
