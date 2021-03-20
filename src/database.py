import mysql.connector

class database:
    def __init__(self, host, username, password):
        self.host = host
        self.username = username
        self.password = password
        mydb = mysql.connector.connect(
        host=self.host,
        user=self.username,
        password=self.password
        )

    def createTables():
        return False

    def getChecks(userid):
        return ''

    def getUser(userid):
        return ''

    def addUser(userid):
        return ''

    def isUserExists(userid):
        return False
    
