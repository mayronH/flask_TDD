import sqlite3
from flask import Flask, g

# configurações do aplicativo
DATABASE = "flaskr.db"

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
def hello():
	return "Hello World!"


if __name__ == "__main__":
	app.run()