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
    kara = database('localhost','akp','somepass')
    return {
        "username": kara.host,
        "theme": "",
        "image": "",
    }