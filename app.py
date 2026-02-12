import urllib.parse
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
    # NOT: Eğer ilk kez bu sütunlarla kuruyorsan aşağıdaki satırın başındaki # işaretini kaldır.
    # db.drop_all()
    db.create_all()

# --- TASARIM (PREMIUM DARK THEME) ---
BASE_STYLE = '''
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;700&display=swap');

    body { 
        font-family: 'Inter', sans-serif; 
        background: radial-gradient(circle at top, #1a1a1a 0%, #080808 100%); 
        color: #ffffff; 
        margin: 0; 
        min-height: 100vh;
    }

    .navbar {
        background: rgba(0, 0, 0, 0.85);
        backdrop-filter: blur(15px);
        padding: 15px 50px;
        position: sticky;
        top: 0;
        z-index: 1000;
        display: flex;
        justify-content: space-between;
        align-items: center;
        border-bottom: 1px solid #333;
    }

    .container { max-width: 1400px; margin: auto; padding: 40px 20px; }

    .form-section {
        background: rgba(255, 255, 255, 0.03);
        padding: 30px;
        border-radius: 20px;
        margin-bottom: 50px;
        border: 1px solid #222;
        backdrop-filter: blur(5px);
    }

    .form-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
        gap: 12px;
    }

    input, select {
        background: #121212;
        border: 1px solid #333;
        color: white;
        padding: 12px;
        border-radius: 8px;
        transition: 0.3s;
    }

    input:focus { border-color: #e50914; outline: none; }

    .btn-submit {
        background: #e50914;
        color: white;
        border: none;
        padding: 12px;
        border-radius: 8px;
        font-weight: 700;
        cursor: pointer;
        transition: 0.3s;
    }

    .btn-submit:hover { background: #ff1e27; transform: translateY(-2px); }

    .movie-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
        gap: 35px;
    }

    .movie-card {
        background: #111;
        border-radius: 15px;
        overflow: hidden;
        transition: 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        border: 1px solid #222;
    }

    .movie-card:hover {
        transform: scale(1.05);
        border-color: #e50914;
        box-shadow: 0 10px 30px rgba(229, 9, 20, 0.2);
    }

    .movie-poster { width: 100%; height: 380px; object-fit: cover; }

    .rating-tag {
        position: absolute;
        top: 15px;
        right: 15px;
        background: #e50914;
        color: white;
        padding: 5px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 13px;
    }

    .movie-info { padding: 20px; }

    .genre-label {
        color: #e50914;
        font-size: 11px;
        text-transform: uppercase;
        font-weight: 700;
        letter-spacing: 1px;
    }

    .btn-trailer {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        background: #fff;
        color: #000;
        text-decoration: none;
        padding: 10px;
        border-radius: 8px;
        margin-top: 15px;
        font-weight: 700;
        font-size: 13px;
    }

    .btn-trailer:hover { background: #e50914; color: #fff; }

    .delete-btn {
        position: absolute;
        top: 15px;
        left: 15px;
        background: rgba(0,0,0,0.7);
        color: #fff;
        width: 30px;
        height: 30px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        text-decoration: none;
        opacity: 0;
        transition: 0.3s;
    }

    .movie-card:hover .delete-btn { opacity: 1; }
</style>
'''

INDEX_TEMPLATE = BASE_STYLE + '''
<nav class="navbar">
    <div style="font-size: 26px; font-weight: 700; color: #e50914;">YUSUF<span style="color:white">FLIX</span></div>
    <div style="display: flex; gap: 30px;">
        <div style="text-align: center;">
            <div style="font-size: 11px; color: #888;">TOPLAM</div>
            <div style="font-weight: 700;">{{ total_count }}</div>
        </div>
        <div style="text-align: center;">
            <div style="font-size: 11px; color: #888;">ORTALAMA</div>
            <div style="font-weight: 700; color: #e50914;">⭐ {{ "%.1f"|format(avg_score or 0) }}</div>
        </div>
    </div>
</nav>

<div class="container">
    <div class="form-section">
        <h3 style="margin-top:0; margin-bottom:20px; font-weight:400;">Film Kütüphanesine Ekle</h3>
        <form class="form-grid" method="POST" action="/ekle">
            <input type="text" name="isim" placeholder="Film Adı" required>
            <input type="text" name="yonetmen" placeholder="Yönetmen" required>
            <input type="number" name="yil" placeholder="Yıl">
            <input type="number" name="puan" placeholder="Puan" step="0.1">
            <select name="tur">
                <option value="Aksiyon">Aksiyon</option>
                <option value="Komedi">Komedi</option>
                <option value="Dram">Dram</option>
                <option value="Bilim Kurgu">Bilim Kurgu</option>
                <option value="Korku">Korku</option>
            </select>
            <input type="text" name="afis_url" placeholder="Afiş URL">
            <input type="text" name="fragman_url" placeholder="Fragman (YouTube)">
            <button type="submit" class="btn-submit">EKLE</button>
        </form>
    </div>

    <div class="movie-grid">
        {% for film in filmler %}
        <div class="movie-card">
            <a href="{{ url_for('sil', id=film.id) }}" class="delete-btn" onclick="return confirm('Silinsin mi Yusuf?')">✕</a>
            <div class="rating-tag">⭐ {{ film.puan }}</div>
            <img class="movie-poster" src="{{ film.afis_url if film.afis_url else 'https://via.placeholder.com/400x600?text=No+Poster' }}">
            <div class="movie-info">
                <span class="genre-label">{{ film.tur }}</span>
                <h3 style="margin: 10px 0 5px 0; font-size: 20px; letter-spacing: -0.5px;">{{ film.isim }}</h3>
                <div style="font-size: 14px; color: #777;">{{ film.yil }} • {{ film.yonetmen }}</div>

                {% if film.fragman_url %}
                <a href="{{ film.fragman_url }}" target="_blank" class="btn-trailer">▶ FRAGMANI İZLE</a>
                {% endif %}
            </div>
        </div>
        {% endfor %}
    </div>
</div>
'''


# --- ROTALAR ---

@app.route('/')
def index():
    filmler = Film.query.order_by(Film.id.desc()).all()
    total_count = Film.query.count()
    avg_score = db.session.query(func.avg(Film.puan)).scalar()
    return render_template_string(INDEX_TEMPLATE, filmler=filmler, total_count=total_count, avg_score=avg_score)


@app.route('/ekle', methods=['POST'])
def ekle():
    try:
        yeni_film = Film(
            isim=request.form.get('isim'),
            yonetmen=request.form.get('yonetmen'),
            yil=request.form.get('yil'),
            puan=request.form.get('puan') or 0,
            tur=request.form.get('tur'),
            afis_url=request.form.get('afis_url'),
            fragman_url=request.form.get('fragman_url')
        )
        db.session.add(yeni_film)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return str(e)
    return redirect(url_for('index'))


@app.route('/sil/<int:id>')
def sil(id):
    film = Film.query.get(id)
    if film:
        db.session.delete(film)
        db.session.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()