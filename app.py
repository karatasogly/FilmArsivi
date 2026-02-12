import urllib.parse
from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- DATABASE CONFIG ---
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


# --- UPDATED MOVIE MODEL (Genre & Year Added) ---
class Movie(db.Model):
    __tablename__ = 'movies_v2'  # New table name for schema update
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    director = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50))
    year = db.Column(db.Integer)
    poster_url = db.Column(db.String(500))
    trailer_url = db.Column(db.String(500))


with app.app_context():
    db.create_all()

# --- MODERN UI DESIGN ---
INDEX_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>YusufFlix | Global Archive</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;900&display=swap');
        body { background: #0a0a0a; color: white; font-family: 'Poppins', sans-serif; margin: 0; padding: 20px; }
        .logo { color: #e50914; font-size: 35px; font-weight: 900; text-align: center; margin-bottom: 25px; }
        .container { max-width: 1300px; margin: auto; }

        /* Add Movie Form */
        .add-box { background: #181818; padding: 20px; border-radius: 10px; margin-bottom: 30px; border: 1px solid #333; }
        .input-group { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; }
        input { background: #252525; border: 1px solid #444; padding: 10px; color: white; border-radius: 5px; }
        button { background: #e50914; color: white; border: none; padding: 10px; border-radius: 5px; font-weight: bold; cursor: pointer; }

        /* Movie Grid */
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 25px; }

        .card { 
            background: #141414; border-radius: 12px; overflow: hidden; 
            position: relative; height: 450px; transition: 0.3s;
            border: 1px solid #222;
        }
        .card:hover { transform: scale(1.05); z-index: 100; border-color: #e50914; }

        /* Poster Image - Fixed Aspect Ratio */
        .poster { 
            width: 100%; height: 100%; 
            object-fit: cover; /* Resim alanı tam kaplar, bozulmaz */
            position: absolute; top: 0; left: 0; z-index: 10; 
            transition: opacity 0.4s ease; 
        }
        .card:hover .poster { opacity: 0; pointer-events: none; }

        .video-box { width: 100%; height: 100%; position: absolute; top: 0; left: 0; z-index: 5; background: #000; }

        .info { 
            position: absolute; bottom: 0; left: 0; width: 100%; 
            background: linear-gradient(transparent, rgba(0,0,0,0.9)); 
            padding: 15px; z-index: 15; pointer-events: none; transition: 0.3s;
        }
        .card:hover .info { opacity: 0.1; }
        .info h3 { margin: 0; font-size: 18px; }
        .info p { margin: 2px 0; font-size: 13px; color: #ccc; }
        .meta-tag { font-size: 11px; color: #e50914; font-weight: bold; }

        .delete-btn { 
            position: absolute; top: 10px; right: 10px; z-index: 20;
            background: rgba(0,0,0,0.7); color: white; text-decoration: none; 
            padding: 4px 8px; border-radius: 4px; font-size: 10px;
        }
        .delete-btn:hover { background: red; }
    </style>
</head>
<body>
    <div class="logo">YUSUF<span style="color:white">FLIX</span></div>

    <div class="container">
        <div class="add-box">
            <form action="/add" method="POST" class="input-group">
                <input type="text" name="title" placeholder="Title" required>
                <input type="text" name="director" placeholder="Director" required>
                <input type="text" name="genre" placeholder="Genre (e.g. Action)">
                <input type="number" name="year" placeholder="Year">
                <input type="text" name="poster" placeholder="Poster URL">
                <input type="text" name="trailer" placeholder="YouTube Link">
                <button type="submit">ADD MOVIE</button>
            </form>
        </div>

        <div class="grid">
            {% for movie in movies %}
            <div class="card" onmouseenter="playVid('{{ movie.id }}')" onmouseleave="stopVid('{{ movie.id }}')">
                <a href="/delete/{{ movie.id }}" class="delete-btn">REMOVE</a>
                <img class="poster" src="{{ movie.poster_url if movie.poster_url else 'https://via.placeholder.com/300x450' }}">

                <div class="video-box">
                    {% if movie.trailer_url %}
                        {% set v_id = movie.trailer_url.split('v=')[-1].split('&')[0] if 'v=' in movie.trailer_url else movie.trailer_url.split('/')[-1] %}
                        <iframe id="player-{{ movie.id }}" width="100%" height="100%" 
                            src="https://www.youtube.com/embed/{{ v_id }}?enablejsapi=1&controls=1&modestbranding=1&rel=0&autoplay=0" 
                            frameborder="0" allowfullscreen>
                        </iframe>
                    {% endif %}
                </div>

                <div class="info">
                    <span class="meta-tag">{{ movie.genre }} | {{ movie.year }}</span>
                    <h3>{{ movie.title }}</h3>
                    <p>{{ movie.director }}</p>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>

    <script>
        // YouTube JS API Control
        function playVid(id) {
            var iframe = document.getElementById('player-' + id);
            if(iframe) {
                iframe.contentWindow.postMessage('{"event":"command","func":"playVideo","args":""}', '*');
            }
        }
        function stopVid(id) {
            var iframe = document.getElementById('player-' + id);
            if(iframe) {
                iframe.contentWindow.postMessage('{"event":"command","func":"pauseVideo","args":""}', '*');
                iframe.contentWindow.postMessage('{"event":"command","func":"seekTo","args":[0, true]}', '*');
            }
        }
    </script>
</body>
</html>
'''


@app.route('/')
def index():
    try:
        movies = Movie.query.order_by(Movie.id.desc()).all()
        return render_template_string(INDEX_TEMPLATE, movies=movies)
    except Exception as e:
        return "<h3>Database Syncing... Please refresh in 5 seconds.</h3>"


@app.route('/add', methods=['POST'])
def add_movie():
    new_movie = Movie(
        title=request.form.get('title'),
        director=request.form.get('director'),
        genre=request.form.get('genre'),
        year=request.form.get('year'),
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