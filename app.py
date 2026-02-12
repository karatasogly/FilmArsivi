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


class Movie(db.Model):
    __tablename__ = 'movies_v2'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    director = db.Column(db.String(100), nullable=False)
    genre = db.Column(db.String(50))
    year = db.Column(db.Integer)
    poster_url = db.Column(db.String(500))
    trailer_url = db.Column(db.String(500))


with app.app_context():
    db.create_all()

# --- THE ULTIMATE TEMPLATE ---
INDEX_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>YusufFlix | Premium Cinema</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;900&display=swap');
        body { background: #050505; color: white; font-family: 'Poppins', sans-serif; margin: 0; padding: 0; scroll-behavior: smooth; }
        .logo { color: #e50914; font-size: 40px; font-weight: 900; text-decoration: none; letter-spacing: -1px; }

        /* Navbar & Search */
        header { 
            display: flex; justify-content: space-between; align-items: center; 
            padding: 20px 5%; background: linear-gradient(to bottom, rgba(0,0,0,0.8), transparent);
            position: fixed; width: 90%; top: 0; z-index: 1000;
        }
        .search-bar { 
            background: rgba(255,255,255,0.1); border: 1px solid #444; padding: 8px 15px;
            border-radius: 20px; color: white; width: 250px; outline: none; transition: 0.3s;
        }
        .search-bar:focus { width: 350px; border-color: #e50914; background: rgba(0,0,0,0.8); }

        /* Hero Banner */
        .hero { 
            height: 70vh; background: linear-gradient(to right, #050505, transparent 60%), url('https://images.alphacoders.com/133/1338429.png');
            background-size: cover; background-position: center; display: flex; align-items: center; padding: 0 5%;
            margin-bottom: 40px;
        }
        .hero-content { max-width: 600px; }
        .hero-content h1 { font-size: 60px; margin: 0; font-weight: 900; }
        .hero-content p { font-size: 18px; color: #ccc; margin: 20px 0; }

        .container { padding: 0 5%; max-width: 1400px; margin: auto; }

        /* Add Box */
        .add-box { background: #111; padding: 25px; border-radius: 15px; margin-bottom: 50px; border: 1px solid #222; }
        .input-group { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; }
        input { background: #222; border: 1px solid #333; padding: 12px; color: white; border-radius: 8px; }
        .add-btn { background: #e50914; color: white; border: none; padding: 12px; border-radius: 8px; font-weight: bold; cursor: pointer; transition: 0.3s; }
        .add-btn:hover { background: #ff0a16; transform: translateY(-2px); }

        /* Movie Grid */
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 30px; }

        .card { 
            background: #111; border-radius: 12px; overflow: hidden; 
            position: relative; height: 420px; transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
            border: 1px solid #222; cursor: pointer;
        }

        /* NEON GLOW EFEKTİ */
        .card:hover { 
            transform: scale(1.08); z-index: 100; border-color: #e50914;
            box-shadow: 0 0 30px rgba(229, 9, 20, 0.5); 
        }

        .poster { 
            width: 100%; height: 100%; object-fit: contain; /* Sığdırma ayarı */
            background: #000; position: absolute; top: 0; left: 0; z-index: 10; 
            transition: opacity 0.5s ease; 
        }
        .card:hover .poster { opacity: 0; pointer-events: none; }

        .video-box { width: 100%; height: 100%; position: absolute; top: 0; left: 0; z-index: 5; background: #000; }
        .video-box iframe { width: 100% !important; height: 100% !important; border: none; }

        .info { position: absolute; bottom: 0; left: 0; width: 100%; background: linear-gradient(transparent, rgba(0,0,0,0.95)); padding: 20px; z-index: 15; pointer-events: none; transition: 0.3s; }
        .card:hover .info { opacity: 0.1; }
        .info h3 { margin: 0; font-size: 20px; font-weight: 700; }
        .meta-tag { font-size: 12px; color: #e50914; font-weight: bold; margin-bottom: 5px; display: block; }

        .delete-btn { position: absolute; top: 15px; right: 15px; z-index: 20; background: rgba(0,0,0,0.6); color: white; text-decoration: none; padding: 6px 12px; border-radius: 6px; font-size: 11px; opacity: 0; transition: 0.3s; }
        .card:hover .delete-btn { opacity: 1; }
    </style>
</head>
<body>
    <header>
        <a href="#" class="logo">YUSUF<span style="color:white">FLIX</span></a>
        <input type="text" id="searchInput" onkeyup="searchMovies()" class="search-bar" placeholder="Search movies, genres...">
    </header>

    <div class="hero">
        <div class="hero-content">
            <span style="color:#e50914; font-weight:bold; letter-spacing:2px;">FEATURED TRAILER</span>
            <h1>The Batman</h1>
            <p>Unmask the truth. Dive into Yusuf's exclusive collection of cinematic masterpieces. Experience movies like never before.</p>
            <button class="add-btn" onclick="window.scrollTo(0, 600)">Browse Collection</button>
        </div>
    </div>

    <div class="container">
        <div class="add-box">
            <h3 style="margin-top:0; color:#eee;">Manage Library</h3>
            <form action="/add" method="POST" class="input-group">
                <input type="text" name="title" placeholder="Movie Title" required>
                <input type="text" name="director" placeholder="Director" required>
                <input type="text" name="genre" placeholder="Genre">
                <input type="number" name="year" placeholder="Year">
                <input type="text" name="poster" placeholder="Poster URL">
                <input type="text" name="trailer" placeholder="YouTube Link">
                <button type="submit" class="add-btn">ADD TO ARCHIVE</button>
            </form>
        </div>

        <div class="grid" id="movieGrid">
            {% for movie in movies %}
            <div class="card movie-card" onmouseenter="playVid('{{ movie.id }}')" onmouseleave="stopVid('{{ movie.id }}')">
                <a href="/delete/{{ movie.id }}" class="delete-btn" onclick="return confirm('Delete this movie?')">REMOVE</a>
                <img class="poster" src="{{ movie.poster_url if movie.poster_url else 'https://via.placeholder.com/300x450?text=No+Poster' }}">
                <div class="video-box">
                    {% if movie.trailer_url %}
                        {% set v_id = movie.trailer_url.split('v=')[-1].split('&')[0] if 'v=' in movie.trailer_url else movie.trailer_url.split('/')[-1] %}
                        <iframe id="player-{{ movie.id }}" width="100%" height="100%" 
                         src="https://www.youtube.com/embed/{{ v_id }}?enablejsapi=1&controls=1&modestbranding=1&rel=0&autoplay=0&iv_load_policy=3&vq=hd720&mute=1" 
                        frameborder="0" allowfullscreen></iframe>
                    {% endif %}
                </div>
                <div class="info">
                    <span class="meta-tag">{{ movie.genre }} | {{ movie.year }}</span>
                    <h3 class="movie-title">{{ movie.title }}</h3>
                    <p style="margin:0; font-size:13px; color:#aaa;">Dir. {{ movie.director }}</p>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>

    <script>
        // 1. YouTube Control
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

        // 2. Search Logic
        function searchMovies() {
            let input = document.getElementById('searchInput').value.toLowerCase();
            let cards = document.getElementsByClassName('movie-card');

            for (let i = 0; i < cards.length; i++) {
                let title = cards[i].querySelector('.movie-title').innerText.toLowerCase();
                let genre = cards[i].querySelector('.meta-tag').innerText.toLowerCase();
                if (title.includes(input) || genre.includes(input)) {
                    cards[i].style.display = "";
                } else {
                    cards[i].style.display = "none";
                }
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
    except:
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