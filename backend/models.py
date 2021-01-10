import os
from sqlalchemy import Column, String, Integer, create_engine
from sqlalchemy.engine.url import URL
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import json

DB_URI = {
    'drivername': 'postgres',
    'username': 'horizon',
    'password': '0105415595',
    'host': 'localhost',
    'port': '5432',
    'database': 'trivia'
}


db = SQLAlchemy()
migrate = Migrate()
'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''


def setup_db(app, database_path=DB_URI):
    app.config["SQLALCHEMY_DATABASE_URI"] = URL(**database_path)
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    migrate.init_app(app, db)
    # db.create_all()


'''
Question

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

'''


class Category(db.Model):
    __tablename__ = 'categories'

    id = Column(Integer, primary_key=True)
    type = Column(String)

    def __init__(self, type):
        self.type = type

