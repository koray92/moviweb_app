from flask_sqlalchemy import SQLAlchemy
from flask import Flask


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///movies.sqlite'
app.config['SECRET_KEY'] = 'key'
db = SQLAlchemy(app)


class UserMovie(db.Model):
    __tablename__ = 'user_movie'
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    movie_id = db.Column(db.Integer, db.ForeignKey('movie.id'), primary_key=True)

    user = db.relationship("User", back_populates="user_movies")
    movie = db.relationship("Movie", back_populates="movie_users")

    

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)

    # Many-to-many relationship
    user_movies = db.relationship('UserMovie', back_populates='user')

    def __repr__(self):
        return f"<User {self.name}>"

    def __str__(self):
        return self.name


# Define the Movie model
class Movie(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    director = db.Column(db.String(50), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    rating = db.Column(db.Integer, nullable=False)

    # Many-to-many relationship
    movie_users = db.relationship('UserMovie', back_populates='movie')

    def __repr__(self):
        return f"<Movie {self.name}>"

    def __str__(self):
        return self.name


# Create the new tables
with app.app_context():
    db.create_all()