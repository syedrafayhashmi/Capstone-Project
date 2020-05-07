import os
import datetime
from sqlalchemy import Column, String, Integer, DateTime
from flask_sqlalchemy import SQLAlchemy
import json

project_dir = os.path.dirname(os.path.abspath(__file__))

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''


def setup_db(app, database_name):
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///{}".format(os.path.join(
        project_dir, database_name))
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)

'''
db_drop_and_create_all()
    drops the database tables and starts fresh
    can be used to initialize a clean database
    !!NOTE you can change the database_filename variable to
    have multiple verisons of a database
'''


def db_drop_and_create_all():
    db.drop_all()
    db.create_all()

'''
Movie
a persistent Movie entity, extends the base SQLAlchemy Model
'''


class Movie(db.Model):
    # Autoincrementing, unique primary key
    id = Column(Integer().with_variant(Integer, "sqlite"), primary_key=True)
    # String Title
    title = Column(String(80), nullable=False)
    # DateTime Release_Date
    release_date = Column(DateTime(), nullable=False)
    # To access the movie list of actors
    actors = db.relationship("MovieActor", back_populates="movie")

    '''
    format()
        json form representation of the Movie model
    '''
    def format(self):
        return {
            'id': self.id,
            'title': self.title,
            'release_date': self.release_date
        }

    '''
    insert()
        inserts a new model into a database
    '''
    def insert(self):
        db.session.add(self)
        db.session.commit()

    '''
    delete()
        deletes a model from the database
    '''
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    '''
    update()
        updates a model in a database
    '''
    def update(self):
        db.session.commit()

    def __repr__(self):
        return json.dumps(self.format())


'''
Actor
a persistent Actor entity, extends the base SQLAlchemy Model
'''


class Actor(db.Model):
    # Autoincrementing, unique primary key
    id = Column(Integer().with_variant(Integer, "sqlite"), primary_key=True)
    # String Name
    name = Column(String(80), nullable=False)
    # Integer Age
    age = Column(Integer(), nullable=True, default=30)
    # String Gender -- should be restricted by the Front-End
    gender = Column(String(80), nullable=True, default="None")
    # To access the actor list of movies
    movies = db.relationship("MovieActor", back_populates="actor")

    '''
    format()
        json form representation of the Actor model
    '''
    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
        }

    '''
    insert()
        inserts a new model into a database
    '''
    def insert(self):
        db.session.add(self)
        db.session.commit()

    '''
    delete()
        deletes a model from the database
    '''
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    '''
    update()
        updates a model in a database
    '''
    def update(self):
        db.session.commit()

    def __repr__(self):
        return json.dumps(self.format())

'''
MovieActor
a persistent MovieActor entity, represnt the many-to-many relationship
between the Movie & the Actor
'''


class MovieActor(db.Model):
    # Autoincrementing, unique primary key
    id = Column(Integer().with_variant(Integer, "sqlite"), primary_key=True)
    movie_id = Column(Integer(), db.ForeignKey(Movie.id))
    actor_id = Column(Integer(), db.ForeignKey(Actor.id))
    movie = db.relationship("Movie", back_populates="actors")
    actor = db.relationship("Actor", back_populates="movies")

    '''
    format()
        json form representation of the MovieActor model
    '''
    def format(self):
        return {
            'id': self.id,
            'movie_id': self.movie_id,
            'actor_id': self.actor_id
        }

    '''
    insert()
        inserts a new model into a database
    '''
    def insert(self):
        db.session.add(self)
        db.session.commit()

    '''
    delete()
        deletes a model from the database
    '''
    def delete(self):
        db.session.delete(self)
        db.session.commit()

    '''
    update()
        updates a model in a database
    '''
    def update(self):
        db.session.commit()

    def __repr__(self):
        return json.dumps(self.format())
