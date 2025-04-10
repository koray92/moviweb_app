from flask import Flask, render_template, request, redirect, url_for, flash
from backend.datamanager.sqlite_data_manager import SQLiteDataManager
from backend.datamanager.data_models import db, User, Movie, UserMovie
import os



app = Flask(__name__, template_folder='frontend/templates',
            static_folder='frontend/static',
            instance_relative_config=True)

app.config['SQLALCHEMY_DATABASE_URI'] = (
        'sqlite:///' + os.path.join(app.instance_path, 'moviwebapp.db'))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'key'
db.init_app(app)


with app.app_context():
    """ 
    Creates the database with its tables and adds
    the first user with the name "Koray"
    """
    db.create_all()
    if not User.query.first():
        users = [
            User(id=1, name="Koray")
        ]
        db.session.add_all(users)
        db.session.commit()


data_manager = SQLiteDataManager(app.config['SQLALCHEMY_DATABASE_URI'])


@app.route('/')
def home():
    """
    Defines the homepage route
    :return: "Welcome to MovieWeb App!"
    """
    return "Welcome to MovieWeb App!"


@app.route('/users')
def list_users():
    """
    Calls the function from DataManager to get all users from the DB
    :return: Displays all added users from the table "users"
    """
    users = data_manager.get_all_users()
    return render_template('users.html', users=users)


@app.route('/users/<int:user_id>')
def user_movies(user_id):
    """
    Checks the user_id of the clicked user and fetches all movies
    assigned to the user
    :return: Displays all movies from the table "UserMovie" based on
             the user_id. If there is no user in the db, 404 error occurs
    """
    user = User.query.get(user_id)  # Make sure user_id is an integer
    if not user:
        return f"User with ID {user_id} not found.", 404


    user_movie_list = Movie.query.join(  # Fetch movies linked to the user
        UserMovie
    ).filter(UserMovie.user_id == user_id).all()

    return render_template('user_movies.html', user=user,
                           user_movie_list=user_movie_list)


@app.route('/add_user', methods=['GET', 'POST'])
def add_user():
    """
    Adds a new user to the "User" database. It checks if the user already exists and
    validates the input of the user.
    :return: If the user already exists an error message will be displayed.
             Otherwise the user will be added to the db if input has been validated
             succesfully and the user will be redirected to the /users route.
    """
    if request.method == 'POST':
        user = request.form.get('username')
        if not user.isalpha():
            print("Please type a valid username (only alphabetic characters are allowed).")
            flash('Error: Please type a valid username '
                  '(only alphabetic characters are allowed).', 'error')
            return render_template('add_user.html')
        elif user:
            data_manager.add_user(user)
            return redirect(url_for('list_users'))

    return render_template('add_user.html')


@app.route('/users/<int:user_id>/add_movie', methods=['GET', 'POST'])
def add_movie(user_id):
    """
    Adds a new movie to the "Movie" database. It checks if the movie already exists and
    validates the input of the user.
    :return: If the user already exists an error message will be displayed.
             Otherwise the user will be added to the db if input has been validated
             succesfully and the user will be redirected to the /users route.
   """
    user = User.query.get(user_id)

    if not user:
        return f"User with ID {user_id} not found", 404

    if request.method == 'POST':
        movie_name = request.form.get('movie_name')
        if movie_name:
            data_manager.add_movie(movie_name, user_id=user_id)
            return redirect(url_for('user_movies', user_id=user_id))

    return render_template('add_movie.html', user=user,
                           user_id=user_id)


@app.route('/users/<user_id>/update_movie/<movie_id>',
           methods=['GET', 'POST'])
def update_movie(user_id, movie_id):

    movie = Movie.query.get(movie_id)  # Fetch the movie by its ID

    if not movie:
        return f"Movie with ID {movie_id} not found.", 404

    if request.method == 'POST':
        movie.name = request.form.get('name')
        movie.director = request.form.get('director')
        movie.year = request.form.get('year')
        movie.rating = request.form.get('rating')

        db.session.commit()

        return redirect(url_for('user_movies', user_id=user_id))

    return render_template('update_movie.html', movie=movie,
                           user_id=user_id)


@app.route('/users/<user_id>/delete_movie/<movie_id>', methods=['GET'])
def delete_movie(user_id, movie_id):

    user_movie = UserMovie.query.filter_by(user_id=user_id, movie_id=movie_id).first()

    if not user_movie:
        return f"Movie with ID {movie_id} not found for this user.", 404

    db.session.delete(user_movie)  # Delete the UserMovie entry to unlink the movie from the user

    movie = Movie.query.get(movie_id)  # Now fetch the movie itself

    if movie and not movie.movie_users:  # If the movie is not associated with any other user, delete the movie
        db.session.delete(movie)

    db.session.commit()

    return redirect(url_for('user_movies', user_id=user_id))


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True)