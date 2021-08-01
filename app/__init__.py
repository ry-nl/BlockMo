from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
from app.chain import BlockChain

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = '6ALc723hiM9mEJAr5t6'
app.permanent_session_lifetime = timedelta(minutes=20)
db = SQLAlchemy(app)

blockchain = BlockChain()

from app import routes