'''
app.py contains all of the server application
this is where you'll find all of the get/post request handlers
the socket event handlers are inside of socket_routes.py
'''

from flask import Flask, render_template, request, make_response
import os
from flask_socketio import SocketIO
from services import article_service
import secrets
from flask_jwt_extended import (
    jwt_required, 
    JWTManager, 
    unset_jwt_cookies
)
from middlewares.auth import jwt_required
from routes.auth import auth
from routes.user import user
from routes.article import article
from routes.room import room
from routes.comment import comment
from routes.block import block
from services import room_service, user_service
# import logging
# this turns off Flask Logging, uncomment this to turn off Logging
# log = logging.getLogger('werkzeug')
# log.setLevel(logging.ERROR)

app = Flask(__name__)
app.register_blueprint(user)
app.register_blueprint(auth)
app.register_blueprint(room)
app.register_blueprint(article)
app.register_blueprint(comment)
app.register_blueprint(block)


app.config['JWT_SECRET_KEY'] = "minh"
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config['SECRET_KEY'] = secrets.token_hex()

jwtManager = JWTManager()

# secret key used to sign the session cookie
cert_file = 'cert.pem'
key_file = 'key.pem'
if not os.path.exists(cert_file) or not os.path.exists(key_file):
    print("SSL certificate or private key file not found!")
    exit(1)

socketio = SocketIO(app)
jwtManager.init_app(app)

# don't remove this!!
import socket_routes

# index page
@app.route("/")
def index():
    return render_template("index.jinja")

# login page
@app.route("/login")
def login():    
    return render_template("login.jinja")

# handler when a "404" error happens
@app.errorhandler(404)
def page_not_found(_):
    return render_template('404.jinja'), 404

# handles a get request to the signup page
@app.route("/signup")
def signup():
    return render_template("signup.jinja")

# home page, where the messaging app is
@app.route("/home")
@jwt_required()
def home():
    return render_template("home.jinja")

@app.route("/contact")
@jwt_required()
def contact():
    return render_template("contact.jinja")

@app.route("/newfeed")
@jwt_required()
def newfeed():
    user_id = request.user_id
    role = request.role
    articles = article_service.new_feed(user_id, role)
    return render_template("newfeed.jinja", articles=articles)

@app.route("/block")
@jwt_required()
def block():
    return render_template("block.jinja")
        
@app.route('/logout')
def logout():
    resp = make_response(render_template("index.jinja"))
    unset_jwt_cookies(resp)
    return resp, 200


@app.route("/api/rooms/upload-image/<room_id>", methods = ["POST"])
@jwt_required(False)
def upload_image(room_id):
    room = room_service.get_by_id(room_id)
    if room is None:
        return {"status_code": 404, "error": "room not found"}, 404

    file = request.files["image"]
    file_extensions = ["jpg", "jpeg", "png", "gif", "webp"]
    if file.filename.split(".")[-1].lower() not in file_extensions:
        return {"status_code": 400, "error": "Invalid file format"}, 400
    
    base_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(base_dir, "static/images/message", f"{room_id}.{file.filename}")
    file.save(file_path)

    file_path = "/static/images/message/" + f"{room_id}.{file.filename}"
    message_id = room_service.create_message(room_id, request.user_id, "image", file_path)
    user = user_service.get_by_id(request.user_id)
    socketio.emit("image", {
        "author": request.user_id,
        "avatar": user.avatar,
        "content": file_path,
        "kind": "image",
        "id": message_id,
        "room_id": room_id
    })
    return {"status_code": 201, "data": None}, 201

if __name__ == '__main__':
    socketio.run(app)
