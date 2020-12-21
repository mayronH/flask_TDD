import sqlite3
from pathlib import Path
from functools import wraps

from os import abort

from flask import Flask, g
from flask.globals import request, session
from flask.templating import render_template
from werkzeug.utils import redirect
from flask.helpers import flash, url_for
from flask.json import jsonify
from flask_sqlalchemy import SQLAlchemy


basedir = Path(__file__).resolve().parent

# configurações do aplicativo
DATABASE = "flaskr.db"
USERNAME = "admin"
PASSWORD = "admin"
SECRET_KEY = "testando"
SQLALCHEMY_DATABASE_URI = f'sqlite:///{Path(basedir).joinpath(DATABASE)}'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Cria e inicializa um novo aplicativo Flask
app = Flask(__name__)

# Carrega as configurações ddo aplicativo
app.config.from_object(__name__)

# Inicializa SQLAlchemy
db = SQLAlchemy(app)

from project import models

def login_required(f):
	@wraps(f)
	def decorated_function(*args, **kwargs):
		if not session.get('logged_in'):
			flash('Please log in')
			return jsonify({
				'status': 0,
				'message': 'Please log in'
			}), 401
		return f(*args, **kwargs)
	return decorated_function


@app.route("/")
def index():
	entries = db.session.query(models.Post)
	return render_template('index.html', entries=entries)


@app.route('/search/', methods=['GET'])
def search():
	query = request.args.get("query")
	entries = db.session.query(models.Post)

	if query:
		return render_template('search.html', entries=entries, query=query)
	return render_template('search.html')


@app.route('/add', methods=['POST'])
def add_entry():
	"""Adicionar um post no banco de dados."""
	if not session.get('logged_in'):
		abort(401)
	
	new_entry = models.Post(request.form['title'], request.form['text'])

	db.session.add(new_entry)
	db.session.commit()

	flash('Nova entrada adicionada com sucesso')
	return redirect(url_for('index'))


@app.route('/delete/<post_id>', methods=['GET'])
@login_required
def delete_entry(post_id):
	"""Deletar um post do banco de dados."""
	result = {
		'status': 0,
		'message': 'Error', 
	}
	try:
		db.session.query(models.Post).filter_by(id=post_id).delete()
		db.session.commit()

		result = {
			'status': 1,
			'message': 'Post deletado'
		}

		flash("Entrada deletada com sucesso")
	except Exception as e:
		result = {
			'status': 0,
			'message': repr(e)
		}
	return jsonify(result)


# Cria rota tanto get e post
@app.route('/login', methods=['GET', 'POST'])
def login():
	"""Login/autenticação e session"""
	error = None
	if request.method == "POST":
		if request.form['username'] != app.config["USERNAME"]:
			error = 'Usuario invalido'
		elif request.form['password'] != app.config["PASSWORD"]:
			error = 'Senha invalida'
		else:
			# Cria uma sessão com a informação de que está logado
			session['logged_in'] = True
			# Flash é uma forma de enviar uma mensagem para a view, o tempo de vida do flash é de um request pro outro.
			flash('Logado')
			# Redireciona para o index caso consiga logar
			return redirect(url_for('index'))
	# Volta para a página de login com os erros
	return render_template('login.html', error=error)


@app.route('/logout')
def logout():
	"""Logout/autenticação e session"""
	# Destroi a session logged_in criada quando a pessoa loga
	session.pop('logged_in', None)
	flash('Deslogado')
	return redirect(url_for('index'))


if __name__ == "__main__":
	app.run()