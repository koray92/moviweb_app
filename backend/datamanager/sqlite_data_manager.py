from flask_sqlalchemy import SQLAlchemy
from data_manager_interface import DataManagerInterface
from sqlalchemy import create_engine, text
import data_models


QUERY_GET_ALL_USERS = "SELECT name FROM user"
QUERY_USER_MOVIES = ("SELECT movie.name"
                     "FROM movie"
                     "JOIN user_movie ON movie.id = user_movie.movie_id"
                     "JOIN user ON user.id = user_movie.user_id"
                     "WHERE user.name = :user_id;")


class SQLiteDataManager(DataManagerInterface):

    def __init__(self, db_file_name):
        """
        Initialize a new engine using the given database URI
        """
        self.db = SQLAlchemy(db_file_name)
        self._engine = create_engine(db_file_name)


    def _execute_query(self, query, params):
        """
        Execute an SQL query with the params provided in a dictionary,
        and return a list of records (dictionary-like objects).
        If an exception is raised, print the full error message.
        """
        try:
            with self._engine.connect() as connection:
                result = connection.execute(text(query), params)
                rows = [dict(row._mapping) for row in result]
                return rows
        except Exception as e:
            print(f"Database query error: {e}")  # Print detailed error
            return []


    def get_all_users(self):
        """
        Returns all entries of the "User" table
        """
        return self._execute_query(QUERY_GET_ALL_USERS)


    def get_user_movies(self, user_id):
        """
        :param user_id:
        :return: list of all movies of a specific user
        """
        params = {'user_id': user_id}
        return self._execute_query(QUERY_USER_MOVIES, params)


    def add_user(self, user):
        """add a new user to your database"""

        # Check if user already exists
        existing_user = data_models.User.query.filter_by(name=user).first()
        if existing_user:
            print(f"User '{user}' already exists.")
            return existing_user

        # Add new user
        new_user = data_models.User(name=user)
        data_models.db.session.add(new_user)
        data_models.db.session.commit()
        print(f"User '{user}' added successfully.")
        return new_user


    def add_movie(self, movie):
        """add a new movie to your database"""
        # Check if user already exists
        existing_movie = data_models.User.query.filter_by(name=movie).first()
        if existing_movie:
            print(f"Movie '{movie}' already exists.")
            return existing_movie

        # Add new movie
        new_movie = data_models.User(name=movie)
        data_models.db.session.add(new_movie)
        data_models.db.session.commit()
        print(f"Movie '{movie}' added successfully.")
        return new_movie

    def update_movie(self, movie_data):
        """
        Updates an existing movie in the database.
        :param movie_data: dict with keys including 'id' and any fields to update
        :return: the updated Movie object or None if not found
        """
        movie_id = movie_data.get('id')
        if not movie_id:
            print("Movie ID is required for update.")
            return None

        movie = data_models.Movie.query.get(movie_id)
        if not movie:
            print(f"No movie found with ID {movie_id}.")
            return None

        # Update fields if they exist in the input data
        if 'name' in movie_data:
            movie.name = movie_data['name']
        if 'director' in movie_data:
            movie.director = movie_data['director']
        if 'year' in movie_data:
            movie.year = movie_data['year']
        if 'rating' in movie_data:
            movie.rating = movie_data['rating']

        data_models.db.session.commit()
        print(f"Movie ID {movie_id} updated successfully.")
        return movie


    def delete_movie(self, movie_id):
        """
        Deletes a movie and all its associations from the database.
        :param movie_id: The ID of the movie to delete
        :return: True if deleted, False if movie not found
        """
        movie = data_models.Movie.query.get(movie_id)
        if not movie:
            print(f"No movie found with ID {movie_id}.")
            return False

        # First, delete associated UserMovie entries
        data_models.UserMovie.query.filter_by(movie_id=movie_id).delete()

        # Then delete the movie
        data_models.db.session.delete(movie)
        data_models.db.session.commit()
        print(f"Movie ID {movie_id} deleted successfully.")
        return True


#def print_results(results=SQLiteDataManager.get_all_users(data_models.db)):






