import pytest
import json
import os
from pathlib import Path
from project.app import app, init_db

TEST_DB = "test.db"

# Configura um ambiente para testes, onde sempre depois do teste ser executado volta para o estado ideal
@pytest.fixture
def client():
	BASE_DIR = Path(__file__).resolve().parent.parent
	app.config["TESTING"] = True
	app.config["DATABASE"] = BASE_DIR.joinpath(TEST_DB)
	
	init_db()
	yield app.test_client()
	init_db()


def login(client, username, password):
	"""Login Helper"""
	# Rota post (/login) com os dados de login e com o comando follow_redirects, que diz para o client seguir o redirect para /login
	return client.post(
		"/login",
		# cria um dicionario de dados com o usuario e senha
		data=dict(username=username, password=password),
		follow_redirects=True,
	)


def logout(client):
	"""Logout Helper"""
	return client.get('/logout', follow_redirects=True)


def test_index(client):
	"""Testa rota index"""
	response = client.get("/", content_type="html/text")
	assert response.status_code == 200


def test_database():
	"""Testa se o banco de dados existe"""
	# init_db()
	# assert Path("flaskr.db").is_file()
	tester = Path("test.db").is_file()
	assert tester


def test_empty_db(client):
	"""Testa se o banco está vazio"""
	rv = client.get('/')
	assert b"Nenhuma entrada encontrada" in rv.data


def test_login_logout(client):
	"""Testa o login e o logout utilizando os helpers"""
	rv = login(client, app.config["USERNAME"], app.config["PASSWORD"])
	assert b"Logado" in rv.data

	rv = logout(client)
	assert b"Deslogado" in rv.data

	rv = login(client, app.config["USERNAME"] + "x", app.config["PASSWORD"])
	assert b"Usuario invalido" in rv.data

	rv = login(client, app.config["USERNAME"], app.config["PASSWORD"] + "x")
	assert b"Senha invalida" in rv.data


def test_message(client):
	"""Testa se o usuario consegue enviar mensagem"""
	login(client, app.config["USERNAME"], app.config["PASSWORD"])
	rv = client.post(
		"/add",
		data = dict(title="<Hello>", text="<strong>HTML</strong> permitido"),
		follow_redirects=True,
	)

	assert b"Nenhuma entrada encontrada" not in rv.data
	assert b"&lt;Hello&gt;" in rv.data
	assert b"<strong>HTML</strong> permitido" in rv.data


def test_delete_message(client):
	"""Testa se a mensagem foi deletada"""
	rv = client.get('/delete/1')
	data = json.loads(rv.data)
	assert data['status'] == 1