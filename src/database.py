import mysql.connector
import redis

class database:
    def createTables(self):
        tables = [
            "CREATE TABLE IF NOT EXISTS `akp_users` ( `user_id` INT NOT NULL AUTO_INCREMENT , `user_name` TEXT NULL , `user_phone` TEXT NOT NULL , `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP , `updated_at` TIMESTAMP NOT NULL DEFAULT NOW() ON UPDATE now() , PRIMARY KEY (`user_id`)) ENGINE = InnoDB CHARSET=utf8 COLLATE utf8_persian_ci;",
            "CREATE TABLE IF NOT EXISTS `akp_checks` ( `check_id` INT NOT NULL AUTO_INCREMENT , `check_name` TEXT NULL , `check_result` TEXT NULL , `check_taken_time` TEXT NULL , `check_user` INT NOT NULL , `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP , `updated_at` TIMESTAMP NOT NULL DEFAULT NOW() ON UPDATE now() , PRIMARY KEY (`check_id`)) ENGINE = InnoDB CHARSET=utf8 COLLATE utf8_persian_ci;",
        ]
        for table in tables:
            cursor = self.db.cursor(buffered=True)
            cursor.execute(table)
        cursor.close()
        if self.redis.set('tables', 'yes'):
            return True
        return False

    def getChecks(self, user_phone):
        userid = self.getUserIdByPhone(user_phone)
        query = "SELECT * FROM `akp_checks` WHERE check_user = %s"
        cursor = self.db.cursor(buffered=True, dictionary=True)
        cursor.execute(query, (userid, ))
        self.db.commit()
        return {
            'error' : False,
            'code' : 200,
            'data' : cursor.fetchall()
        }
        return ''

    def getCheck(self, user_phone, checkid):
        if self.isCheckExists(checkid) is not True:
            return {
                'error' : False,
                'code' : 404,
                'message' : 'No check founed with this id'
            }, 404
        
        userid = self.getUserIdByPhone(user_phone)
        query = "SELECT * FROM `akp_checks` WHERE check_user = %s AND check_id = %s"
        cursor = self.db.cursor(buffered=True, dictionary=True)
        cursor.execute(query, (userid, checkid))
        self.db.commit()
        return {
            'error' : False,
            'code' : 200,
            'data' : cursor.fetchone()
        }

    def isCheckExists(self, checkid):
        query = "SELECT * FROM `akp_checks` WHERE check_id = %s LIMIT 1"
        values = (checkid,)
        cursor = self.db.cursor(buffered=True)
        cursor.execute(query, values)
        self.db.commit()
        print(cursor.rowcount)
        if cursor.rowcount > 0:
            cursor.close()
            return True
        cursor.close()
        return False

    def getUserIdByPhone(self, user_phone):
        query = "SELECT user_id FROM `akp_users` WHERE user_phone = %s LIMIT 1"
        cursor = self.db.cursor(buffered=True, dictionary=True)
        cursor.execute(query, (user_phone, ))
        self.db.commit()
        return cursor.fetchone()['user_id']

    def getUser(self, user_phone):
        query = "SELECT * FROM `akp_users` WHERE user_phone = %s LIMIT 1"
        cursor = self.db.cursor(buffered=True, dictionary=True)
        cursor.execute(query, (user_phone, ))
        self.db.commit()
        user = cursor.fetchone()

        return {
            'error' : False,
            'code' : 200,
            'data' : user
        }, 200

    def addUser(self, user_phone):
        if self.isUserExists(user_phone):
            return {
                'error' : False,
                'code' : 200,
                'message' : 'User already exists',
            }, 200
        query = "INSERT INTO `akp_users` (user_phone) VALUES (%s)"
        cursor = self.db.cursor(buffered=True)
        cursor.execute(query, (user_phone, ))
        cursor.close()
        
        return {
            'error' : False,
            'code' : 201,
            'message' : 'User created',
            'data' : self.getUser(user_phone)[0]['data'],
        }, 201

    def isUserExists(self, user_phone):
        query = "SELECT * FROM `akp_users` WHERE user_phone = %s LIMIT 1"
        values = (user_phone,)
        cursor = self.db.cursor(buffered=True)
        cursor.execute(query, values)
        self.db.commit()
        print(cursor.rowcount)
        if cursor.rowcount > 0:
            cursor.close()
            return True
        cursor.close()
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
