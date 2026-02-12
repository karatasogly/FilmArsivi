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
    tur = db.Column(db.String(50))  # Yeni: Tür
    afis_url = db.Column(db.String(500))
    fragman_url = db.Column(db.String(500))  # Yeni: Fragman
    izlendi = db.Column(db.Boolean, default=False)  # Yeni: İzlenme durumu


with app.app_context():
    db.drop_all()  # ŞİMDİLİK AÇIK - Push sonrası kapatacağız
    db.create_all()

# --- TASARIM ---
BASE_STYLE = '''
<style>
    body { font-family: 'Inter', sans-serif; background-color: #0f0f0f; color: #e5e5e5; margin: 0; padding: 20px; }
    .container { max-width: 1200px; margin: auto; }
    .stats-bar { display: flex; gap: 20px; margin-bottom: 20px; background: #1a1a1a; padding: 15px; border-radius: 10px; border-left: 5px solid #e50914; }
    .stat-item { font-size: 14px; text-transform: uppercase; letter-spacing: 1px; color: #aaa; }
    .stat-value { color: #fff; font-weight: bold; font-size: 18px; }
    .form-box { background: #1a1a1a; padding: 20px; border-radius: 12px; margin-bottom: 30px; display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; }
    input, select { background: #262626; border: 1px solid #333; color: white; padding: 10px; border-radius: 5px; }
    .btn-submit { background: #e50914; color: white; border: none; font-weight: bold; cursor: pointer; border-radius: 5px; }
    .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 25px; }
    .card { background: #1a1a1a; border-radius: 12px; overflow: hidden; position: relative; border: 1px solid #222; transition: 0.3s; }
    .card:hover { transform: translateY(-5px); border-color: #e50914; }
    .card img { width: 100%; height: 320px; object-fit: cover; }
    .card-content { padding: 15px; }
    .badge-puan { position: absolute; top: 10px; left: 10px; background: #e50914; padding: 5px 10px; border-radius: 5px; font-weight: bold; font-size: 12px; }
    .badge-tur { font-size: 11px; background: #333; padding: 3px 8px; border-radius: 10px; color: #ccc; }
    .btn-play { display: block; text-align: center; background: #333; color: white; text-decoration: none; padding: 8px; margin-top: 10px; border-radius: 5px; font-size: 13px; transition: 0.2s; }
    .btn-play:hover { background: #fff; color: black; }
    .delete-x { position: absolute; top: 10px; right: 10px; background: rgba(0,0,0,0.5); color: white; text-decoration: none; width: 25px; height: 25px; border-radius: 50%; text-align: center; }
</style>
'''

INDEX_TEMPLATE = BASE_STYLE + '''
<div class="container">
    <h1 style="color:#e50914">YUSUF CINEMA+</h1>

    <div class="stats-bar">
        <div class="stat-item">Toplam Film: <span class="stat-value">{{ total_count }}</span></div>
        <div class="stat-item">Ortalama Puan: <span class="stat-value">{{ "%.1f"|format(avg_score or 0) }}</span></div>
    </div>

    <form class="form-box" method="POST" action="/ekle">
        <input type="text" name="isim" placeholder="Film Adı" required>
        <input type="text" name="yonetmen" placeholder="Yönetmen" required>
        <input type="number" name="yil" placeholder="Yıl">
        <input type="number" name="puan" placeholder="Puan (0-10)" step="0.1">
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

    <div class="grid">
        {% for film in filmler %}
        <div class="card">
            <a href="{{ url_for('sil', id=film.id) }}" class="delete-x" onclick="return confirm('Silinsin mi?')">×</a>
            <div class="badge-puan">⭐ {{ film.puan }}</div>
            <img src="{{ film.afis_url if film.afis_url else 'https://via.placeholder.com/300x450' }}">
            <div class="card-content">
                <span class="badge-tur">{{ film.tur }}</span>
                <h3 style="margin: 10px 0 5px 0;">{{ film.isim }}</h3>
                <p style="font-size: 13px; color: #888; margin: 0;">{{ film.yonetmen }} | {{ film.yil }}</p>
                {% if film.fragman_url %}
                <a href="{{ film.fragman_url }}" target="_blank" class="btn-play">▶ Fragmanı İzle</a>
                {% endif %}
            </div>
        </div>
        {% endfor %}
    </div>
</div>
'''


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