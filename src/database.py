import mysql.connector
import redis
from OpenCV.OpenCv import OpenCv

class database:
    def createTables(self):
        tables = [
            "CREATE TABLE IF NOT EXISTS `akp_users` ( `user_id` INT NOT NULL AUTO_INCREMENT , `user_name` TEXT NULL , `user_phone` TEXT NOT NULL , `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP , `updated_at` TIMESTAMP NOT NULL DEFAULT NOW() ON UPDATE now() , PRIMARY KEY (`user_id`)) ENGINE = InnoDB CHARSET=utf8 COLLATE utf8_persian_ci;",
            "CREATE TABLE IF NOT EXISTS `akp_checks` ( `check_id` INT NOT NULL AUTO_INCREMENT , `check_name` TEXT NULL , `check_image_url` TEXT NULL , `check_status` TEXT NULL, `check_result` TEXT NULL , `check_taken_time` TEXT NULL , `check_user` INT NOT NULL , `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP , `updated_at` TIMESTAMP NOT NULL DEFAULT NOW() ON UPDATE now() , PRIMARY KEY (`check_id`)) ENGINE = InnoDB CHARSET=utf8 COLLATE utf8_persian_ci;",
            "CREATE TABLE IF NOT EXISTS `akp_attachments` ( `attach_id` INT NOT NULL AUTO_INCREMENT , `user_id` INT NOT NULL , `attach_url` TEXT NOT NULL , `uploaded_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP , PRIMARY KEY (`attach_id`)) ENGINE = InnoDB;",
        ]
        for table in tables:
            self.reconnect()
            cursor = self.db.cursor(buffered=True)
            cursor.execute(table)
        cursor.close()
        if self.redis.set('tables', 'yes'):
            return True
        return False

    def getChecks(self, user_phone):
        userid = self.getUserIdByPhone(user_phone)
        query = "SELECT * FROM `akp_checks` WHERE check_user = %s ORDER BY check_id DESC"
        self.reconnect()
        cursor = self.db.cursor(buffered=True, dictionary=True)
        cursor.execute(query, (userid, ))
        self.db.commit()
        data = cursor.fetchall()
        for i,d in enumerate(data):
            d["check_result"] = json.loads(d["check_result"])
            data[i] = d
        return {
            'error' : False,
            'code' : 200,
            'data' : data
        }
        return ''

    def getCheck(self, checkid):
        if self.isCheckExists(checkid) is not True:
            return {
                'error' : False,
                'code' : 404,
                'message' : 'No check founed with this id'
            }, 404
        
        query = "SELECT * FROM `akp_checks` WHERE check_id = %s"
        self.reconnect()
        cursor = self.db.cursor(buffered=True, dictionary=True)
        cursor.execute(query, (checkid, ))
        self.db.commit()
        data = cursor.fetchone()
        import json
        data["check_result"] = json.loads(data["check_result"])
        
        return {
            'error' : False,
            'code' : 200,
            'data' : data
        }

    def addCheck(self, check_user, check_image_url, check_name = None):
        import time
        start_time = time.time()
        
        keys, values = self.oc.process(image_url = check_image_url)
        
        data = {
            "keys" : keys,
            "values" : values,
            "analysis" : ""
        }
        import json
        check_result = json.dumps(data)

        if check_image_url == None:
            return {
                'error' : True,
                'code' : 400,
                'message' : 'unvalid image url'
            }, 400
        query = "INSERT INTO `akp_checks` (check_user, check_name, check_status, check_image_url, check_result, check_taken_time) VALUES (%s, %s, %s, %s, %s, %s)"
        self.reconnect()
        cursor = self.db.cursor(buffered=True)
        check_status = 'waiting'

        if check_name is None:
            import random
            check_name = "Check #" + (str(random.randint(0,9))) + (str(random.randint(0,9))) + (str(random.randint(0,9))) + (str(random.randint(0,9))) + (str(random.randint(0,9))) + (str(random.randint(0,9)))
        cursor.execute(query, (check_user, check_name, check_status, check_image_url, check_result, (time.time() - start_time)))
        self.db.commit()
        cursor.close()
        return {
            'error' : False,
            'code' : 201,
            'check_id' : self.getLatestCheck(),
            'message' : 'check created',
            'data' : data,
        }, 201

    def getLatestCheck(self):
        self.reconnect()
        cursor = self.db.cursor(buffered=True)
        cursor.execute("SELECT check_id FROM `akp_checks` ORDER BY check_id DESC LIMIT 1", ())
        if cursor.rowcount > 0:
            return cursor.fetchone()[0]
        return False

    def addFile(self, file_url, userid):
        if not self.isFileExists(file_url):
            query = "INSERT INTO `akp_attachments` (user_id, attach_url) VALUES (%s, %s)"
            self.reconnect()
            cursor = self.db.cursor(buffered=True)
            cursor.execute(query, (userid, file_url))
            self.db.commit()
            cursor.close()

    def isFileExists(self, file_url):
        query = "SELECT * FROM `akp_attachments` WHERE attach_url = %s LIMIT 1"
        values = (file_url,)
        self.reconnect()
        cursor = self.db.cursor(buffered=True)
        cursor.execute(query, values)

        if cursor.rowcount > 0:
            cursor.close()
            return True
        cursor.close()
        return False

    def getUsersChecks(self, userid):
        query = "SELECT * FROM `akp_checks` WHERE check_user = %s ORDER BY check_id DESC"
        self.reconnect()
        cursor = self.db.cursor(buffered=True, dictionary=True)
        cursor.execute(query, (userid, ))
        cursor.close()
        data = cursor.fetchall()
        import json
        for i,d in enumerate(data):
            d["check_result"] = json.loads(d["check_result"])
            data[i] = d
        return {
            'error' : False,
            'data' : data
        }

    def modifyCheckResult(self, check_id, keys, values):
        check_result = {
            "keys" : keys,
            "values" : values,
            "analysis" : ""
        }
        import json
        check_result = json.dumps(check_result)
        
        self.updateCheckResult(check_id, check_result, check_status= "Modified")
        self.updateAnalysis(check_id, self.oc.analysis(keys, values))
        return {
            'error' : False,
            'code' : 200,
            'message' : 'Result modified',
            'data' : self.getCheck(check_id)
        }

    def updateAnalysis(self, check_id, result):
        check = self.getCheck(check_id)
        import json
        check["data"]["check_result"]["analysis"] = result
        check["data"]["check_result"] = json.dumps(check["data"]["check_result"])
        self.updateCheckResult(check_id, check["data"]["check_result"], check_status="Done")

    def updateCheckResult(self, checkid, check_result, check_taken_time = None, check_status = None):
        if self.isCheckExists(checkid) is False:
            return {
                'error' : False,
                'code' : 404,
                'message' : "No check founed with this id"
            }, 404
        
        query = "UPDATE `akp_checks` SET `check_result` = %s , `check_taken_time` = %s , `check_status` = %s WHERE check_id = %s"
        if check_status is None:
            old_check_status = self.getCheckStatus(checkid)
            if old_check_status is not False:
                check_status = old_check_status
        self.reconnect()
        cursor = self.db.cursor(buffered=True)
        cursor.execute(query, (check_result, check_taken_time, check_status, checkid))
        self.db.commit()
        return {
            'error' : False,
            'code' : 200,
            'message' : 'Check updated',
            'data' : self.getCheck(checkid)
        }

    def updateCheck(self, checkid, checkname):
        if self.isCheckExists(checkid) is False:
            return {
                'error' : False,
                'code' : 404,
                'message' : "No check founed with this id"
            }, 404
        query = "UPDATE `akp_checks` SET `check_name` = %s WHERE `check_id` = %s"
        self.reconnect()
        cursor = self.db.cursor(buffered=True)
        cursor.execute(query, (checkname, checkid))
        self.db.commit()
        return {
            'error' : False,
            'code' : 200,
            'message' : 'check updated',
            'data' : self.getCheck(checkid)
        }

    def getCheckStatus(self, checkid):
        query = "SELECT check_status FROM `akp_checks` WHERE check_id = %s LIMIT 1"
        self.reconnect()
        cursor = self.db.cursor(buffered=True, dictionary=True)
        cursor.execute(query, (checkid, ))
        res = cursor.fetchone()
        if res is None:
            return False
        return res['check_status']

    def isCheckExists(self, checkid):
        query = "SELECT * FROM `akp_checks` WHERE check_id = %s LIMIT 1"
        values = (checkid,)
        self.reconnect()
        cursor = self.db.cursor(buffered=True)
        cursor.execute(query, values)

        if cursor.rowcount > 0:
            cursor.close()
            return True
        cursor.close()
        return False

    def getUserIdByPhone(self, user_phone):
        query = "SELECT user_id FROM `akp_users` WHERE user_phone = %s LIMIT 1"
        self.reconnect()
        cursor = self.db.cursor(buffered=True, dictionary=True)
        cursor.execute(query, (user_phone, ))
        self.db.commit()
        return cursor.fetchone()['user_id']

    def isUserExistsById(self, userid):
        query = "SELECT * FROM `akp_users` WHERE user_id = %s LIMIT 1"
        values = (userid,)
        self.reconnect()
        cursor = self.db.cursor(buffered=True)
        cursor.execute(query, values)

        if cursor.rowcount > 0:
            cursor.close()
            return True
        cursor.close()
        return False

    def getUser(self, user_phone):
        query = "SELECT * FROM `akp_users` WHERE user_phone = %s LIMIT 1"
        self.reconnect()
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
                'data' : self.getUser(user_phone)[0]['data'],
            }, 200
        query = "INSERT INTO `akp_users` (user_phone) VALUES (%s)"
        self.reconnect()
        cursor = self.db.cursor(buffered=True)
        cursor.execute(query, (user_phone, ))
        self.db.commit()
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
        self.reconnect()
        cursor = self.db.cursor(buffered=True)
        cursor.execute(query, values)
        self.db.commit()
        
        if cursor.rowcount > 0:
            cursor.close()
            return True
        cursor.close()
        return False
    
    def reconnect(self):
        self.db.reconnect()

    def __init__(self, host, username, password, dbname):
        self.host = host
        self.username = username
        self.password = password
        self.dbname = dbname
        self.oc = OpenCv()
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
