from flask import Flask, escape, request, jsonify
from database import database

app = Flask(__name__)
kara = database('localhost','akp','somepass', 'akp')

@app.route('/')
def hello():
    name = request.args.get("name", "World")
    return f'Hello, {escape(name)}!'

@app.route('/result')
def showResult():
    return f'Result'

@app.route('/register', methods=['GET', 'POST'])
def registerUser():
    req = request.json
    if req == None:
        return {
            'error' : True,
            'code' : 400,
            'message' : 'Some variables not passed',
        }, 400
    try:
        return kara.addUser(req['phone'])
    except KeyError:
        return {
        'error' : True,
        'code' : 400,
        'message' : 'Some variables not passed',
    }, 400
    return {
        'w' : 'what is happening'
    },200

@app.route('/checks/<userid>')
def getUsersChecks(userid):
    return '{}\'s profile'.format(escape(userid))

@app.route("/me")
def me_api():
    return kara.getChecks("09226742397")

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

@app.errorhandler(404)
def page_not_found(e):
    return {
        'error' : False,
        'code' : 404,
        'message' : f"The requested URL path {request.path} was not founded on the server."
    },404


@app.errorhandler(405)
def method_not_allowed(e):
    return {
        'error' : False,
        'code' : 404,
        'message' : f"The requested method '{request.method}' is not allowed."
    }, 405

@app.errorhandler(403)
def access_denied():
    return {
        'error' : False,
        'code' : 403,
        'message' : f"Access denied."
    }, 403
