import urllib.parse
from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- DATABASE CONFIGURATION ---
SERVER = 'yusuf-film-server-sweden.database.windows.net'
DATABASE = 'yusuf-film-server-sweden'
USERNAME = 'Yusuf2323'
PASSWORD = 'yusuf.2323'
DRIVER = '{ODBC Driver 17 for SQL Server}'

connection_string = f"Driver={DRIVER};Server=tcp:{SERVER},1433;Database={DATABASE};Uid={USERNAME};Pwd={PASSWORD};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=120;"
params = urllib.parse.quote_plus(connection_string)
app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=" + params
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# --- MOVIE MODEL (English Schema) ---
class Movie(db.Model):
    __tablename__ = 'movies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    director = db.Column(db.String(100), nullable=False)
    poster_url = db.Column(db.String(500))
    trailer_url = db.Column(db.String(500))


with app.app_context():
    db.create_all()

# --- UI DESIGN (English & Modern) ---
INDEX_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YusufFlix | Movie Archive</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;700;900&display=swap');
        body { background: #080808; color: white; font-family: 'Poppins', sans-serif; margin: 0; padding: 20px; }
        .logo { color: #e50914; font-size: 40px; font-weight: 900; text-align: center; margin-bottom: 30px; letter-spacing: 2px; }
        .container { max-width: 1400px; margin: auto; }

        /* Add Movie Form */
        .add-box { background: #141414; padding: 25px; border-radius: 12px; margin-bottom: 40px; border: 1px solid #333; }
        .input-group { display: flex; flex-wrap: wrap; gap: 10px; }
        input { background: #222; border: 1px solid #444; padding: 12px; color: white; border-radius: 6px; flex: 1; min-width: 150px; }
        button { background: #e50914; color: white; border: none; padding: 12px 25px; border-radius: 6px; font-weight: bold; cursor: pointer; transition: 0.3s; }
        button:hover { background: #b2070f; }

        /* Movie Grid */
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(380px, 1fr)); gap: 35px; }

        .card { 
            background: #111; border-radius: 15px; overflow: hidden; 
            position: relative; height: 550px; transition: transform 0.3s ease;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }
        .card:hover { transform: scale(1.03); border: 1px solid #e50914; }

        .poster { 
            width: 100%; height: 100%; object-fit: cover; 
            position: absolute; top: 0; left: 0; z-index: 10; 
            transition: opacity 0.5s ease; 
        }
        .card:hover .poster { opacity: 0; pointer-events: none; }

        .video-box { 
            width: 100%; height: 100%; position: absolute; top: 0; left: 0; z-index: 5; 
            background: #000;
        }

        .info { 
            position: absolute; bottom: 0; left: 0; width: 100%; 
            background: linear-gradient(transparent, rgba(0,0,0,0.95)); 
            padding: 25px; z-index: 15; transition: 0.3s; pointer-events: none;
        }
        .card:hover .info { opacity: 0.2; }
        .info h3 { margin: 0; font-size: 22px; }
        .info p { color: #e50914; margin: 5px 0 0; font-weight: bold; }

        .delete-link { 
            position: absolute; top: 15px; right: 15px; z-index: 20;
            background: rgba(229, 9, 20, 0.8); color: white; text-decoration: none; 
            padding: 5px 12px; border-radius: 5px; font-size: 12px; font-weight: bold;
        }
        .delete-link:hover { background: #ff0000; }
    </style>
</head>
<body>
    <div class="logo">YUSUF<span style="color:white">FLIX</span></div>

    <div class="container">
        <div class="add-box">
            <h4 style="margin-top:0; color:#aaa;">Add New Movie</h4>
            <form action="/add" method="POST" class="input-group">
                <input type="text" name="title" placeholder="Movie Title" required>
                <input type="text" name="director" placeholder="Director" required>
                <input type="text" name="poster" placeholder="Poster Image URL">
                <input type="text" name="trailer" placeholder="YouTube Trailer Link">
                <button type="submit">ADD TO LIST</button>
            </form>
        </div>

        <div class="grid">
            {% for movie in movies %}
            <div class="card">
                <a href="/delete/{{ movie.id }}" class="delete-link" onclick="return confirm('Delete this movie?')">REMOVE</a>
                <img class="poster" src="{{ movie.poster_url if movie.poster_url else 'https://via.placeholder.com/400x600?text=No+Poster' }}">

                <div class="video-box">
                    {% if movie.trailer_url %}
                        {% set v_id = movie.trailer_url.split('v=')[-1].split('&')[0] if 'v=' in movie.trailer_url else movie.trailer_url.split('/')[-1] %}
                        <iframe width="100%" height="100%" 
                            src="https://www.youtube.com/embed/{{ v_id }}?controls=1&modestbranding=1&rel=0&iv_load_policy=3" 
                            frameborder="0" allowfullscreen>
                        </iframe>
                    {% endif %}
                </div>

                <div class="info">
                    <h3>{{ movie.title }}</h3>
                    <p>{{ movie.director }}</p>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
'''


@app.route('/')
def index():
    try:
        movies = Movie.query.order_by(Movie.id.desc()).all()
        return render_template_string(INDEX_TEMPLATE, movies=movies)
    except Exception as e:
        return f"<h3>Database is waking up... Please refresh in 10 seconds.</h3>"


@app.route('/add', methods=['POST'])
def add_movie():
    new_movie = Movie(
        title=request.form.get('title'),
        director=request.form.get('director'),
        poster_url=request.form.get('poster'),
        trailer_url=request.form.get('trailer')
    )
    db.session.add(new_movie)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/delete/<int:id>')
def delete_movie(id):
    movie = Movie.query.get(id)
    if movie:
        db.session.delete(movie)
        db.session.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()