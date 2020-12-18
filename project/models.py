from project.app import db



class Post(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	title = db.Column(db.String, nullable=False)
	text = db.Column(db.String, nullable=False)

	def __init__(self, title, text):
		self.title = title
		self.text = text

	
	def __repr__(self):
		# f Antes da String é uma forma de interpolação entre string e variaveis
		return f'<title {self.title}>'