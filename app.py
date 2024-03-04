from flask import Flask, render_template
import sqlite3
import redis

app = Flask(__name__)
cache = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

@app.route('/')
def home():
    # Simulating data retrieval from SQLite
    connection = sqlite3.connect('database.db')
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM sample_table')
    data = cursor.fetchall()
    connection.close()

    # Using Redis as a cache
    cached_data = cache.get('cached_data')
    if not cached_data:
        # If data not found in cache, store it and set the cache expiration time
        cache.set('cached_data', str(data), ex=60)
        cached_data = str(data)

    return render_template('index.html', data=data, cached_data=cached_data)

if __name__ == '__main__':
    app.run(debug=True)
