from sqlalchemy import Column, String, Integer
from sqlalchemy.engine.url import URL
from flask_sqlalchemy import SQLAlchemy

from dotenv import dotenv_values

config = dotenv_values('.env')

# URI for the local db. The values should be retrieved from the environment variables
# existing in the .env file.
DB_URI = {
    'drivername': config['DRIVER_NAME'],
    'username': config['USERNAME'],
    'password': config['PASSWORD'],
    'host': config['HOST'],
    'port': config['DB_PORT'],
    'database': config['DB_NAME']
}

# Create the db path
database_path = URL(**DB_URI)

# Create and instance of the db
db = SQLAlchemy()


def setup_db(app, database_path=database_path):
    '''
    binds a flask application and a SQLAlchemy service
    @param: app: instance of the flask application.
    @param: database_path: a path for the local db.
    '''
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()


'''
Question
Creates a db model fro the questions table.
'''


class Question(db.Model):
    __tablename__ = 'questions'

    id = Column(Integer, primary_key=True)
    question = Column(String)
    answer = Column(String)
    category = Column(String)
    difficulty = Column(Integer)

    def __init__(self, question, answer, category, difficulty):
        self.question = question
        self.answer = answer
        self.category = category
        self.difficulty = difficulty

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'question': self.question,
            'answer': self.answer,
            'category': self.category,
            'difficulty': self.difficulty
        }


'''
Category
Creates a db model for the categories table.
'''


class Category(db.Model):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    type = Column(String)

    def __init__(self, type):
        self.type = type
