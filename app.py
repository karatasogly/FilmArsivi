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
    # Yeni sütunların Azure'da oluşması için bu iki satır önemli!
    db.drop_all()
    db.create_all()

# --- TASARIM VE ARAYÜZ ---
BASE_STYLE = '''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;800&display=swap');
    :root { --primary: #e50914; --bg: #080808; --text: #fff; }
    body { font-family: 'Poppins', sans-serif; background: var(--bg); color: var(--text); margin: 0; transition: 0.5s; }
    #bg-blur { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background-size: cover; filter: blur(60px) brightness(0.2); z-index: -1; transition: 0.7s; }
    .navbar { background: rgba(0,0,0,0.8); backdrop-filter: blur(15px); padding: 15px 50px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #222; position: sticky; top:0; z-index:100; }
    .container { max-width: 1300px; margin: auto; padding: 30px; }
    .btn-action { background: var(--primary); color: white; border: none; padding: 10px 20px; border-radius: 30px; font-weight: 600; cursor: pointer; text-decoration: none; }
    .movie-card { background: #111; border-radius: 15px; overflow: hidden; position: relative; transition: 0.4s; border: 1px solid #222; }
    .movie-card:hover { transform: translateY(-10px); border-color: var(--primary); }
    .movie-poster { width: 100%; height: 380px; object-fit: cover; }
    .movie-info { padding: 15px; }
    .rating-badge { position: absolute; top: 15px; right: 15px; background: var(--primary); padding: 4px 10px; border-radius: 8px; font-weight: bold; }
    input, select { background: #222; color: white; border: none; padding: 10px; border-radius: 5px; width: 100%; }
</style>
'''

INDEX_TEMPLATE = BASE_STYLE + '''
<div id="bg-blur"></div>
<nav class="navbar">
    <div style="font-size: 24px; font-weight: 800; color: var(--primary);">YUSUF<span style="color:white">FLIX</span></div>
    <button onclick="pickRandom()" class="btn-action" style="background:#fff; color:#000;">🎲 NE İZLESEM?</button>
</nav>
<div class="container">
    <form action="/ekle" method="POST" style="background:#111; padding:20px; border-radius:15px; margin-bottom:40px; display:grid; grid-template-columns:repeat(auto-fit, minmax(140px, 1fr)); gap:10px; align-items: center;">
        <input type="text" name="isim" placeholder="Film Adı" required>
        <input type="text" name="yonetmen" placeholder="Yönetmen" required>
        <input type="number" name="puan" placeholder="Puan (0-10)" step="0.1">
        <select name="tur">
            <option value="Aksiyon">Aksiyon</option>
            <option value="Dram">Dram</option>
            <option value="Bilim Kurgu">Bilim Kurgu</option>
            <option value="Komedi">Komedi</option>
            <option value="Korku">Korku</option>
        </select>
        <input type="text" name="afis_url" placeholder="Afiş Linki">
        <input type="text" name="fragman_url" placeholder="Fragman Linki">
        <button type="submit" class="btn-action">EKLE</button>
    </form>

    <div style="display:grid; grid-template-columns:repeat(auto-fill, minmax(260px, 1fr)); gap:30px;">
        {% for film in filmler %}
        <div class="movie-card" onmouseover="document.getElementById('bg-blur').style.backgroundImage='url({{ film.afis_url }})'">
            <div class="rating-badge">⭐ {{ film.puan }}</div>
            <img class="movie-poster" src="{{ film.afis_url if film.afis_url else 'https://via.placeholder.com/300x450' }}">
            <div class="movie-info">
                <div style="color:var(--primary); font-size:11px; font-weight:700;">{{ film.tur }}</div>
                <h3 style="margin:5px 0;">{{ film.isim }}</h3>
                <p style="font-size:12px; color:#888;">{{ film.yonetmen }}</p>
                {% if film.fragman_url %}
                <a href="{{ film.fragman_url }}" target="_blank" style="text-decoration:none; color:white; font-size:12px; font-weight:bold;">▶ FRAGMAN</a>
                {% endif %}
                <a href="/sil/{{ film.id }}" style="float:right; color:#555; text-decoration:none; font-size:12px;">SİL</a>
            </div>
        </div>
        {% endfor %}
    </div>
</div>

<script>
    const movies = [{% for film in filmler %}"{{ film.isim }}",{% endfor %}];
    function pickRandom() {
        if(movies.length === 0) return alert("Kütüphane boş!");
        const r = movies[Math.floor(Math.random() * movies.length)];
        alert("Yusuf'un Seçimi: " + r);
    }
</script>
'''

@app.route('/')
def index():
    filmler = Film.query.order_by(Film.id.desc()).all()
    return render_template_string(INDEX_TEMPLATE, filmler=filmler)

@app.route('/ekle', methods=['POST'])
def ekle():
    try:
        yeni = Film(
            isim=request.form.get('isim'),
            yonetmen=request.form.get('yonetmen'),
            puan=request.form.get('puan') or 0,
            tur=request.form.get('tur'),
            afis_url=request.form.get('afis_url'),
            fragman_url=request.form.get('fragman_url')
        )
        db.session.add(yeni)
        db.session.commit()
    except:
        db.session.rollback()
    return redirect('/')

@app.route('/sil/<int:id>')
def sil(id):
    f = Film.query.get(id)
    if f:
        db.session.delete(f)
        db.session.commit()
    return redirect('/')

if __name__ == '__main__':
    app.run()