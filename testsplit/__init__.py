from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

db = SQLAlchemy()

def create_app():
	app = Flask(__name__)

	app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
	app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

	app.secret_key = '6ALc723hiM9mEJAr5t6'
	app.permanent_session_lifetime = timedelta(minutes=20)

	db.init_app(app)

	with app.app_context():
		from . import routes
		db.create_all()
		
	return app