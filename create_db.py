from project.app import db
from project.models import Post

db.create_all()

db.session.commit()