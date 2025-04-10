from sqlalchemy import create_engine, text
from .data_manager_interface import DataManagerInterface
from . import data_models
import os
from dotenv import load_dotenv
import requests


load_dotenv()

OMDB_API_KEY = os.getenv('API_KEY')

QUERY_GET_ALL_USERS = "SELECT id, name FROM user"
QUERY_USER_MOVIES = ("SELECT movie.name"
                     "FROM movie"
                     "JOIN user_movie ON movie.id = user_movie.movie_id"
                     "JOIN user ON user.id = user_movie.user_id"
                     "WHERE user.id = :user_id;")


class SQLiteDataManager(DataManagerInterface):

    def __init__(self, db_file_name):
        """
        Initialize a new engine using the given database URI
        """
        if db_file_name.startswith('sqlite:///'):
            db_file_name = 'sqlite:///' + os.path.abspath(db_file_name[10:])
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
        return self._execute_query(QUERY_GET_ALL_USERS, {})


    def get_user_movies(self, user_id):
        """
        :param user_id:
        :return: list of all movies of a specific user
        """
        params = {'user_id': user_id}
        return self._execute_query(QUERY_USER_MOVIES, params)


    def add_user(self, user):
        existing_user = data_models.User.query.filter_by(name=user).first()
        if existing_user:
            print(f"User '{user}' already exists.")
            return existing_user

        new_user = data_models.User(name=user)
        data_models.db.session.add(new_user)
        data_models.db.session.commit()
        print(f"User '{user}' added successfully.")
        return new_user


    def fetch_movie_from_omdb(self, title):
        try:
            response = requests.get("http://www.omdbapi.com/", params={
                "t": title,
                "apikey": OMDB_API_KEY
            })
            data = response.json()
            if data.get("Response") == "True":
                return {
                    "name": data.get("Title", title),
                    "director": data.get("Director", "Unknown"),
                    "year": int(data.get("Year", 2023)),
                    "rating": int(float(data.get("imdbRating", 5.0)))
                }
            else:
                print(f"OMDb: Movie not found: {title}")
        except Exception as e:
            print(f"Error fetching movie from OMDb: {e}")
        return None


    def add_movie(self, movie_name, user_id=None):
        # Check if movie already exists in the database
        existing_movie = data_models.Movie.query.filter_by(name=movie_name).first()

        if not existing_movie:
            movie_data = self.fetch_movie_from_omdb(movie_name)
            if not movie_data:
                print(f"Falling back to defaults for: {movie_name}")
                movie_data = {
                    "name": movie_name,
                    "director": "Unknown",
                    "year": 2023,
                    "rating": 5
                }

            # Create new movie in the database
            new_movie = data_models.Movie(**movie_data)
            data_models.db.session.add(new_movie)
            data_models.db.session.commit()
            movie = new_movie
            print(f"Movie '{movie.name}' added successfully.")
        else:
            movie = existing_movie
            print(f"Movie '{movie.name}' already exists.")

        # If a user ID is provided, link the movie to the user in the user_movie table
        if user_id:
            user = data_models.User.query.get(user_id)
            if user and movie:
                link_exists = data_models.UserMovie.query.filter_by(user_id=user.id, movie_id=movie.id).first()
                if not link_exists:
                    link = data_models.UserMovie(user_id=user.id, movie_id=movie.id)
                    data_models.db.session.add(link)
                    data_models.db.session.commit()
                    print(f"Linked movie '{movie.name}' to user '{user.name}'.")

        return movie


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






