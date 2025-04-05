# main.py
from flask import Flask,  session 

from app.routes.vendor import vendor_bp 
from app.routes.shop import shop_bp
from app.routes.user import user_bp
from app.routes.info import info_bp
from app.routes.mail import mail_bp
from app.routes.admin import admin_bp

from app.services.mail import mail


import os
from dotenv import load_dotenv
from pathlib import Path


load_dotenv()
app = Flask(__name__ ,static_folder= str(Path().cwd()/"app/static"))

app.secret_key = os.getenv("APP_SECRET_KEY")
app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER')
app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
app.config['MAIL_USE_TLS'] = True 
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_DEFAULT_SENDER')


mail.init_app(app)

app.register_blueprint(vendor_bp)
app.register_blueprint(shop_bp)
app.register_blueprint(user_bp)
app.register_blueprint(info_bp)
app.register_blueprint(mail_bp)
app.register_blueprint(admin_bp)


@app.route("/log")
def log_out():
    session.clear()
    return "Bye"

@app.route("/")
def g():
    return "".join([f"<br> {k}: {v}</br>" for k,v in session.items()])

@app.route("/help")
def help():
    return "hello"

@app.route("/index")
def index():
    return "index"
