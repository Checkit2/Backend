from flask import Flask, escape, request
from database import database

app = Flask(__name__)

@app.route('/')
def hello():
    name = request.args.get("name", "World")
    return f'Hello, {escape(name)}!'

@app.route('/result')
def showResult():
    return f'Result'

@app.route('/register')
def registerUser():
    return f'Added'

@app.route('/checks/<userid>')
def getUsersChecks(userid):
    return '{}\'s profile'.format(escape(userid))

@app.route("/me")
def me_api():
    user = "amir"
    kara = database('localhost','akp','somepass', 'akp')
    return {
        "username": kara.host,
        "theme": "",
        "image": "",
    }

@app.route("/status")
def status():
    return {
        'status' : 'awake',
        'checkit_backend_version' : '0.1',
        'checkit_builder_version' : '0.1',
        'mysql_version' : '8.0.23',
        'redis_version' : '6.2.1',
        'python_version' : '3.8.5',
        'flask_version' : '1.1.2'
    }