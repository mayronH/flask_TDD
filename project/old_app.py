from os import abort
import sqlite3
from flask import Flask, g
from flask.globals import request, session
from flask.templating import render_template
from werkzeug.utils import redirect
from flask.helpers import flash, url_for
from flask.json import jsonify

# configurações do aplicativo
DATABASE = "flaskr.db"
USERNAME = "admin"
PASSWORD = "admin"
SECRET_KEY = "testando"

# Cria e inicializa um novo aplicativo Flask
app = Flask(__name__)

# Carrega as configurações ddo aplicativo
app.config.from_object(__name__)

def connect_db():
	"""Conectar com o banco"""
	rv = sqlite3.connect(app.config["DATABASE"])
	rv.row_factory = sqlite3.Row
	return rv


def init_db():
	"""Cria o banco de dados"""
	# With é uma simplicação para a abertura e fechamento de um arquivo 
	# 	try:
	# 		__enter__() 
	# 	finally: 
	# 		__exti__()
	with app.app_context():
		db = get_db()
		# open_resource é um comando do Flask para abrir um recurso, no caso no modo read
		with app.open_resource("schema.sql", mode="r") as f:
			db.cursor().executescript(f.read())
		db.commit()


def get_db():
	"""Abre a conexão com o banco de dados"""
	# Verifica se um objeto possui determinado atributo (objeto, atributo)
	# Objeto g é um objeto de context, application context, ele mantem dado de configuração/banco de dados/variaveis e etc
	if not hasattr(g, "sqlite_db"):
		g.slite_db = connect_db()
	return g.slite_db


@app.teardown_appcontext
def close_db(error):
	"""Fecha a conexão com o banco de dados"""
	if hasattr(g, "sqlite_db"):
		g.slite_db.close()


@app.route("/")
def index():
	# Abre a conexão com o banco
	db = get_db()
	# Executa uma query
	cur = db.execute('SELECT * FROM entries ORDER BY id DESC')
	# Pega todas as linhas retornadas pela query
	entries = cur.fetchall()
	# Renderiza o template index.html e envia as entries
	return render_template('index.html', entries=entries)


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


@app.route('/add', methods=['POST'])
def add_entry():
	"""Adicionar um post no banco de dados."""
	if not session.get('logged_in'):
		abort(401)
	db = get_db()
	db.execute(
		'INSERT into entries (title,text) values (?, ?)',
		[request.form['title'], request.form['text']]
	)
	db.commit()
	flash('Nova entrada adicionada com sucesso')
	return redirect(url_for('index'))

@app.route('/delete/<post_id>', methods=['GET'])
def delete_entry(post_id):
	"""Deletar um post do banco de dados."""
	result = {
		'status': 0,
		'message': 'Error', 
	}
	try:
		db = get_db()
		db.execute('DELETE FROM entries WHERE id=' + post_id)
		db.commit()
		result = {
			'status': 1,
			'message': 'Post deletado'
		}
	except Exception as e:
		result = {
			'status': 0,
			'message': repr(e)
		}
	return jsonify(result)

if __name__ == "__main__":
	app.run()