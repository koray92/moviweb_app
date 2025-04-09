from abc import ABC, abstractmethod



class DataManagerInterface(ABC):


    @abstractmethod
    def get_all_users(self):
        pass


    @abstractmethod
    def get_user_movies(self, user_id):
        pass


    @abstractmethod
    def add_user(self, user):
        """Add a new user"""
        pass


    @abstractmethod
    def add_movie(self, movie):
        """Add a new movie"""
        pass


    @abstractmethod
    def update_movie(self, movie):
        """Update movie details"""
        pass


    @abstractmethod
    def delete_movie(self, movie_id):
        """Delete movie based on its ID"""
        pass