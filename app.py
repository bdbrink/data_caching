from flask import Flask, render_template, request
from flask_socketio import SocketIO
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import sqlite3
import redis

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
socketio = SocketIO(app)
login_manager = LoginManager(app)
cache = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

# Simulate a user database for demonstration purposes
class User(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/')
@login_required
def home():
    connection = sqlite3.connect('chinook.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM albums')
    data = cursor.fetchall()
    connection.close()

    # Using Redis as a cache
    cached_data = cache.get('cached_data')
    if not cached_data:
        cache.set('cached_data', str(data), ex=60)
        cached_data = str(data)

    return render_template('index.html', data=data, cached_data=cached_data)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form['user_id']
        user = User(user_id)
        login_user(user)
        return redirect(request.args.get('next') or '/')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@app.route('/visualization')
@login_required
def visualization():
    connection = sqlite3.connect('chinook.db')

    # Sample data for visualization
    cursor = connection.cursor()
    cursor.execute('SELECT genres.Name, COUNT(tracks.TrackId) AS TrackCount FROM genres JOIN tracks ON genres.GenreId = tracks.GenreId GROUP BY genres.Name')
    data = cursor.fetchall()
    connection.close()

    # Create a bar chart using Plotly
    fig = px.bar(data, x='Name', y='TrackCount', title='Track Count by Genre')
    graph_json = fig.to_json()

    return render_template('visualization.html', graph_json=graph_json)

@socketio.on('message')
def handle_message(msg):
    socketio.emit('message', msg)

if __name__ == '__main__':
    socketio.run(app, debug=True)
