import urllib.parse
import random
from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)

# --- VERİTABANI AYARLARI ---
SERVER = 'yusuf-film-server-sweden.database.windows.net'
DATABASE = 'yusuf-film-server-sweden'
USERNAME = 'Yusuf2323'
PASSWORD = 'yusuf.2323'
DRIVER = '{ODBC Driver 17 for SQL Server}'

connection_string = f"Driver={DRIVER};Server=tcp:{SERVER},1433;Database={DATABASE};Uid={USERNAME};Pwd={PASSWORD};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
params = urllib.parse.quote_plus(connection_string)
app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=" + params
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# --- VERİTABANI MODELİ ---
class Film(db.Model):
    __tablename__ = 'film'
    id = db.Column(db.Integer, primary_key=True)
    isim = db.Column(db.String(100), nullable=False)
    yonetmen = db.Column(db.String(100), nullable=False)
    yil = db.Column(db.Integer)
    puan = db.Column(db.Float)
    tur = db.Column(db.String(50))
    afis_url = db.Column(db.String(500))
    fragman_url = db.Column(db.String(500))


with app.app_context():
    # Sütunlarda bir değişiklik yoksa drop_all'a gerek yok, ama garanti olsun dersen açabilirsin.
    # db.drop_all()
    db.create_all()

# --- TASARIM (JS DESTEKLİ ULTRA PREMİUM) ---
BASE_STYLE = '''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');

    :root { --primary: #e50914; --bg: #080808; --card-bg: #111; --text: #fff; }
    .light-mode { --bg: #f5f5f7; --card-bg: #fff; --text: #1d1d1f; }

    body { 
        font-family: 'Poppins', sans-serif; 
        background-color: var(--bg); 
        color: var(--text); 
        margin: 0; 
        transition: 0.5s ease;
        overflow-x: hidden;
    }

    #bg-blur {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background-size: cover; background-position: center;
        filter: blur(80px) brightness(0.3);
        z-index: -1; transition: 0.8s;
    }

    .navbar {
        background: rgba(0,0,0,0.7); backdrop-filter: blur(20px);
        padding: 15px 50px; position: sticky; top: 0; z-index: 1000;
        display: flex; justify-content: space-between; align-items: center;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }

    .container { max-width: 1400px; margin: auto; padding: 30px; }

    .btn-action {
        background: var(--primary); color: white; border: none;
        padding: 10px 20px; border-radius: 30px; font-weight: 600;
        cursor: pointer; transition: 0.3s; text-decoration: none; font-size: 13px;
    }
    .btn-action:hover { transform: scale(1.05); box-shadow: 0 0 20px var(--primary); }

    .filter-bar { display: flex; gap: 10px; margin-bottom: 30px; overflow-x: auto; padding-bottom: 10px; }
    .filter-tag { 
        background: rgba(255,255,255,0.1); padding: 8px 18px; border-radius: 20px; 
        font-size: 12px; cursor: pointer; border: 1px solid transparent; transition: 0.3s;
    }
    .filter-tag:hover, .filter-tag.active { border-color: var(--primary); background: rgba(229,9,20,0.2); }

    .movie-card {
        background: var(--card-bg); border-radius: 20px; overflow: hidden;
        position: relative; transition: 0.5s cubic-bezier(0.2, 1, 0.3, 1);
        border: 1px solid rgba(255,255,255,0.05);
    }
    .movie-card:hover { transform: scale(1.03) translateY(-10px); }

    .movie-poster { width: 100%; height: 400px; object-fit: cover; }

    .movie-info { padding: 20px; background: linear-gradient(to top, var(--card-bg) 80%, transparent); margin-top: -50px; position: relative; }

    .rating-badge {
        position: absolute; top: -180px; right: 15px;
        background: var(--primary); padding: 5px 12px; border-radius: 10px; font-weight: 800;
    }

    /* Modal Styles */
    #randomModal {
        display: none; position: fixed; z-index: 2000; top:0; left:0; width:100%; height:100%;
        background: rgba(0,0,0,0.9); align-items: center; justify-content: center;
    }
</style>
'''

INDEX_TEMPLATE = BASE_STYLE + '''
<div id="bg-blur"></div>

<nav class="navbar">
    <div style="font-size: 28px; font-weight: 800; color: var(--primary);">YUSUF<span style="color:var(--text)">FLIX</span></div>
    <div style="display: flex; gap: 15px; align-items: center;">
        <button onclick="pickRandom()" class="btn-action" style="background: #fff; color: #000;">🎲 NE İZLESEM?</button>
        <button onclick="toggleTheme()" id="themeBtn" class="btn-action" style="background: #333;">🌙</button>
    </div>
</nav>

<div class="container">
    <div class="filter-bar">
        <a href="/" class="filter-tag active">Tümü</a>
        <a href="/?filter=top" class="filter-tag">⭐ En Yüksek Puanlılar</a>
        <a href="/?filter=Aksiyon" class="filter-tag">Aksiyon</a>
        <a href="/?filter=Bilim Kurgu" class="filter-tag">Bilim Kurgu</a>
        <a href="/?filter=Komedi" class="filter-tag">Komedi</a>
    </div>

    <div style="background: rgba(255,255,255,0.03); padding: 25px; border-radius: 20px; margin-bottom: 40px;">
        <form action="/ekle" method="POST" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 10px;">
            <input type="text" name="isim" placeholder="Film Adı" required style="padding:10px; border-radius:10px; border:none; background:#222; color:white;">
            <input type="text" name="yonetmen" placeholder="Yönetmen" required style="padding:10px; border-radius:10px; border:none; background:#222; color:white;">
            <input type="number" name="puan" placeholder="Puan" step="0.1" style="padding:10px; border-radius:10px; border:none; background:#222; color:white;">
            <select name="tur" style="padding:10px; border-radius:10px; border:none; background:#222; color:white;">
                <option value="Aksiyon">Aksiyon</option>
                <option value="Bilim Kurgu">Bilim Kurgu</option>
                <option value="Dram">Dram</option>
                <option value="Komedi">Komedi</option>
            </select>
            <input type="text" name="afis_url" placeholder="Afiş URL" style="padding:10px; border-radius:10px; border:none; background:#222; color:white;">
            <input type="text" name="fragman_url" placeholder="YouTube Link" style="padding:10px; border-radius:10px; border:none; background:#222; color:white;">
            <button type="submit" class="btn-action">EKLE</button>
        </form>
    </div>

    <div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 30px;">
        {% for film in filmler %}
        <div class="movie-card" onmouseover="changeBg('{{ film.afis_url }}')" onmouseout="changeBg('')">
            <div class="rating-badge">⭐ {{ film.puan }}</div>
            <img class="movie-poster" src="{{ film.afis_url if film.afis_url else 'https://via.placeholder.com/400x600' }}">
            <div class="movie-info">
                <div style="color:var(--primary); font-size:11px; font-weight:700;">{{ film.tur }}</div>
                <h3 style="margin: 5px 0;">{{ film.isim }}</h3>
                <div style="font-size: 12px; opacity: 0.7;">{{ film.yonetmen }} • {{ film.yil }}</div>
                {% if film.fragman_url %}
                <a href="{{ film.fragman_url }}" target="_blank" style="display:block; margin-top:15px; text-decoration:none; color:var(--text); font-weight:bold; font-size:13px;">▶ FRAGMANI İZLE</a>
                {% endif %}
                <a href="/sil/{{ film.id }}" style="color:red; font-size:10px; text-decoration:none; position:absolute; bottom:10px; right:10px;">SİL</a>
            </div>
        </div>
        {% endfor %}
    </div>
</div>

<div id="randomModal" onclick="this.style.display='none'">
    <div id="randomContent" style="text-align:center; color:white;">
        <h1 style="color:var(--primary)">YUSUF SENİN İÇİN SEÇTİ!</h1>
        <div id="chosenMovieName" style="font-size: 40px; font-weight: 800;"></div>
    </div>
</div>

<script>
    function changeBg(url) {
        const bg = document.getElementById('bg-blur');
        if(url) {
            bg.style.backgroundImage = `url('${url}')`;
        } else {
            bg.style.backgroundImage = 'none';
        }
    }

    function toggleTheme() {
        document.body.classList.toggle('light-mode');
        const btn = document.getElementById('themeBtn');
        btn.innerHTML = document.body.classList.contains('light-mode') ? '🌙' : '☀️';
    }

    const movies = [{% for film in filmler %}"{{ film.isim }}",{% endfor %}];
    function pickRandom() {
        if(movies.length == 0) return alert("Önce film ekle Yusuf!");
        const chosen = movies[Math.floor(random() * movies.length)];
        document.getElementById('chosenMovieName').innerText = chosen;
        document.getElementById('randomModal').style.display = 'flex';
    }
</script>
'''


@app.route('/')
def index():
    filter_type = request.args.get('filter')
    if filter_type == 'top':
        filmler = Film.query.filter(Film.puan >= 8.0).order_by(Film.puan.desc()).all()
    elif filter_type:
        filmler = Film.query.filter_by(tur=filter_type).all()
    else:
        filmler = Film.query.order