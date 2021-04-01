import os
from flask import Flask, escape, request, jsonify, flash, redirect, url_for
from database import database
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = os.path.join('static', 'images')
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
PUBLIC_APP_URL = "http://localhost:5000/" + os.path.join('static', 'images')

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PUBLIC_APP_URL'] = PUBLIC_APP_URL

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

@app.route('/checks/<userid>', methods=['GET'])
def getUsersChecks(userid):
    return kara.getUsersChecks(userid)

@app.route('/check/update/<check_id>', methods=['PUT'])
def modifyCheckResult(check_id):
    req = request.json
    if req == None:
        return {
            'error' : True,
            'code' : 400,
            'message' : 'Some variables not passed',
        }, 400
    return kara.modifyCheckResult(check_id, req['keys'], req['values'])

@app.route('/check/<check_id>', methods=['GET'])
def getSingleCheck(check_id):
    return kara.getCheck(check_id)

@app.route('/checks/new', methods=['POST'])
def addCheck():
    req = request.json
    if req == None:
        return {
            'error' : True,
            'code' : 400,
            'message' : 'Some variables not passed'
        }, 400
    return kara.addCheck(req['user'], req['image_url'], req['check_name'])

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def hash_file(file_path):
    import sys
    import hashlib

    # BUF_SIZE is totally arbitrary, change for your app!
    BUF_SIZE = 65536  # lets read stuff in 64kb chunks!

    sha1 = hashlib.sha1()

    with open(file_path, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha1.update(data)

    return sha1.hexdigest()


@app.route('/upload/<user_id>', methods=['GET', 'POST'])
def upload(user_id):
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return {
                'error' : True,
                'message' : 'no file founded in request',
                'code' : 400
            }, 400
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            return {
                'error' : True,
                'message' : 'no file founded in request',
                'code' : 400
            }, 400
        if file and allowed_file(file.filename):
            if not kara.isUserExistsById(user_id):
                return {
                    'error' : True,
                    'code': 404,
                    'message' : 'no user founded with this id'
                }, 404
            filename = secure_filename("u-" + user_id + "-" + file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            kara.addFile(os.path.join(app.config['PUBLIC_APP_URL'], filename), user_id)
            return {
                'error' : False,
                'code' : 200,
                'message' : 'File uploaded',
                'data' :  os.path.join(app.config['PUBLIC_APP_URL'], filename)
            }
        if not allowed_file(file.filename):
            return {
                'error' : True,
                'code' : 403,
                'message' : 'This type of file not supported, Supported types [jpg,png,jpeg]'
            }
        return {
            'error' : False,
            'code' : 200
        }

@app.route('/upload', methods=['GET', 'POST'])
def rupload():
    return {
        'error' : True,
        'code' : 400,
        'message' : 'enter user id in url request'
    }

@app.route('/checks/<check_id>', methods=['PUT'])
def updateCheck(check_id):
    req = request.json
    if req == None:
        return {
            'error' : True,
            'code' : 400,
            'message' : 'Some variables not passed'
        }, 400
    return kara.updateCheck(check_id, req['name'])

@app.route('/checks/result/<check_id>', methods=['PUT'])
def updateCheckResult(check_id):
    req = request.json
    if req == None:
        return {
            'error' : True,
            'code' : 400,
            'message' : 'Some variables not passed'
        }, 400
    return kara.updateCheckResult(check_id, req['result'], req['taken_time'], req['status'])

@app.route("/me")
def me_api():
    # return kara.updateCheckResult(2, 'res', 200, 'Done')
    return f'You'

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

if __name__ == "__main__":
    app.run(host='0.0.0.0')