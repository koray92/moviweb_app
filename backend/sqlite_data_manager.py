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


    def _get_all_users(self):
        """
        Returns all entries of the "User" table
        """
        return self._execute_query(QUERY_GET_ALL_USERS)


    def _get_user_movies(self, user_id):
        """
        :param user_id:
        :return: list of all movies of a specific user
        """
        params = {'user_id': user_id}
        return self._execute_query(QUERY_USER_MOVIES, params)



def print_results(results=SQLiteDataManager.get_all_users(data_models.db)):
    """
    Get a list of flight results (List of dictionary-like objects from SQLAachemy).
    Even if there is one result, it should be provided in a list.
    Each object *has* to contain the columns:
    FLIGHT_ID, ORIGIN_AIRPORT, DESTINATION_AIRPORT, AIRLINE, and DELAY.
    """

    print(results)

print_results()




