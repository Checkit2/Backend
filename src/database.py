import mysql.connector

class database:
    def createTables(self):
        tables = [
            "CREATE TABLE IF NOT EXISTS `akp_users` ( `user_id` INT NOT NULL AUTO_INCREMENT , `user_name` TEXT NULL , `user_phone` TEXT NOT NULL , `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP , `updated_at` TIMESTAMP NOT NULL DEFAULT NOW() ON UPDATE now() , PRIMARY KEY (`user_id`)) ENGINE = InnoDB CHARSET=utf8 COLLATE utf8_persian_ci;",
        ]
        for table in tables:
            cursor = self.db.cursor()
            cursor.execute(table)
        return False

    def getChecks(userid):
        return ''

    def getUser(userid):
        return ''

    def addUser(userid):
        return ''

    def isUserExists(userid):
        # q = "SELECT * FROM `akp_users` "
        return False
    
    def __init__(self, host, username, password, dbname):
        self.host = host
        self.username = username
        self.password = password
        self.dbname = dbname
        self.db = mysql.connector.connect(
            host = self.host,
            user = self.username,
            password = self.password,
            database = self.dbname,
        )
        # Creating databases if not exists
        self.createTables()
