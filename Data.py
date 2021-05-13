import re
from flask import Flask, request, views
from flask_restful import Api, Resource, reqparse, abort, fields, marshal_with
from flask_sqlalchemy import SQLAlchemy
import hashlib

# Inicjalizacja 
app = Flask(__name__)
api = Api(app)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db' # tworzenie bazy danych

# Tworzenie kolumn bazy danych
class UserModel(db.Model):
	username = db.Column(db.String(100), nullable=False, primary_key=True)
	password = db.Column(db.String(100), nullable=False)

# Tworzenie obiektu RequestParser, do sprawdzania poprawności danych
user_put_args = reqparse.RequestParser()
user_put_args.add_argument('password', type=str, help='Email is requred', required=True)

# Definiowanie zmiennych klasy, w celu zwracania poprawnych wartości
resource_fields = {
	'username': fields.String,
	'password': fields.String
}

# Klasa z metodami http, w celu obługiwania bazy danych
class User(Resource):
	@marshal_with(resource_fields) # konwertowanie do formatu JSON
	def get(self, usr):
		result = UserModel.query.filter_by(username=usr).first() # Wyszukiwanie podanego użytkownika->unikalna nazwa
		if not result:
			abort(404, message='Could not find user..') # 404-nie znaleziono
		return result

	@marshal_with(resource_fields)
	def put(self, usr):
		args = user_put_args.parse_args() # pobiera wszystkie argumenty z user_put_args (password) 
		result_u = UserModel.query.filter_by(username=usr).first() # Wyszukiwanie podanego użytkownika->unikalna nazwa
		
		if result_u:
			abort(409, message="Username is taken!")# 409-Nazwa użytkownika jest już zajęta
		
		hashed = hashlib.sha1(args['password'].encode('utf-8')) # szyfrowanie hasła
		user = UserModel(username=usr, password=hashed.hexdigest()) # Tworzenie obiektu klasy UserModel przy wyołaniu metody put request
		db.session.add(user)
		db.session.commit() # Zatwierdzenie 
		return user, 201 # 201 - Status -> Stworzono
	

api.add_resource(User, "/user/<string:usr>")

# db.create_all()

if __name__ == '__main__':
	app.run()

