import urllib.parse
import os
from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

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


# --- VERİTABANI MODELİ (yil sütunu eklendi) ---
class Film(db.Model):
    __tablename__ = 'film'
    id = db.Column(db.Integer, primary_key=True)
    isim = db.Column(db.String(100), nullable=False)
    yonetmen = db.Column(db.String(100), nullable=False)
    yil = db.Column(db.Integer, nullable=True)  # Hocanın istediği sütun
    afis_url = db.Column(db.String(500), nullable=True)
    puan = db.Column(db.Float, default=0.0)


with app.app_context():
    # Yeni sütun eklendiği için bir kez sıfırlamak gerekebilir
    db.drop_all()
    db.create_all()

# --- TASARIM (CSS Güncellendi) ---
BASE_STYLE = '''
<style>
    body { font-family: 'Segoe UI', sans-serif; margin: 40px; background-color: #141414; color: white; }
    .container { max-width: 1100px; margin: auto; background: #1f1f1f; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    input { padding: 12px; border-radius: 6px; border: 1px solid #333; background: #2b2b2b; color: white; width: 100%; box-sizing: border-box; margin-bottom: 10px; }
    .btn-add { background: #e50914; color: white; border: none; padding: 12px; border-radius: 6px; cursor: pointer; font-weight: bold; width: 100%; transition: 0.3s; }
    .btn-add:hover { background: #b20710; }
    .gallery { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 20px; margin-top: 20px; }
    .card { background: #262626; padding: 15px; border-radius: 12px; text-align: center; position: relative; border: 1px solid #333; }
    .card img { width: 100%; height: 280px; object-fit: cover; border-radius: 8px; margin-bottom: 10px; }
    .rating-badge { position: absolute; top: 20px; left: 20px; background: rgba(229, 9, 20, 0.9); color: white; padding: 4px 8px; border-radius: 5px; font-weight: bold; font-size: 12px; }
    .year-badge { background: #444; color: #ddd; padding: 2px 6px; border-radius: 4px; font-size: 12px; margin-left: 5px; }
    .btn-delete { position: absolute; top: 10px; right: 10px; color: #777; text-decoration: none; font-size: 20px; }
    .btn-edit { display: inline-block; margin-top: 10px; color: #007bff; text-decoration: none; font-size: 13px; }
    h2 { text-align: center; color: #e50914; text-transform: uppercase; letter-spacing: 2px; }
</style>
'''

INDEX_TEMPLATE = BASE_STYLE + '''
<div class="container">
    <h2>🎬 Yusuf'un Film Arşivi</h2>

    <form method="GET" action="/" style="margin-bottom: 20px;">
        <input type="text" name="search" placeholder="Film veya yönetmen ara..." value="{{ search_query }}">
    </form>

    <form method="POST" action="/ekle" style="display: grid; grid-template-columns: 2fr 1.5fr 1fr 0.8fr 0.8fr auto; gap: 8px; margin-bottom: 30px;">
        <input type="text" name="isim" placeholder="Film Adı" required>
        <input type="text" name="yonetmen" placeholder="Yönetmen" required>
        <input type="number" name="yil" placeholder="Yıl">
        <input type="number" name="puan" placeholder="Puan" step="0.1">
        <input type="text" name="afis_url" placeholder="Afiş URL">
        <button type="submit" class="btn-add">EKLE</button>
    </form>

    <div class="gallery">
        {% for film in filmler %}
        <div class="card">
            <a href="{{ url_for('sil', id=film.id) }}" class="btn-delete" onclick="return confirm('Silinsin mi?')">×</a>
            <div class="rating-badge">⭐ {{ film.puan }}</div>
            <img src="{{ film.afis_url if film.afis_url else 'https://via.placeholder.com/200x300?text=Resim+Yok' }}">
            <h4 style="margin: 5px 0;">{{ film.isim }} <span class="year-badge">{{ film.yil if film.yil else '' }}</span></h4>
            <p style="color: #999; font-size: 12px; margin: 0;">{{ film.yonetmen }}</p>
            <a href="{{ url_for('duzenle', id=film.id) }}" class="btn-edit">Düzenle</a>
        </div>
        {% endfor %}
    </div>
</div>
'''

EDIT_TEMPLATE = BASE_STYLE + '''
<div class="container">
    <h2>✏️ Kaydı Güncelle</h2>
    <form method="POST">
        <label>Film Adı:</label><input type="text" name="isim" value="{{ film.isim }}" required>
        <label>Yönetmen:</label><input type="text" name="yonetmen" value="{{ film.yonetmen }}" required>
        <label>Yıl:</label><input type="number" name="yil" value="{{ film.yil }}">
        <label>Puan:</label><input type="number" name="puan" value="{{ film.puan }}" step="0.1">
        <label>Afiş URL:</label><input type="text" name="afis_url" value="{{ film.afis_url }}">
        <button type="submit" class="btn-add">GÜNCELLE</button>
        <a href="/" style="display: block; text-align: center; color: #777; margin-top: 15px; text-decoration: none;">İptal</a>
    </form>
</div>
'''


# --- ROTALAR ---

@app.route('/')
def index():
    search_query = request.args.get('search', '')
    if search_query:
        filmler = Film.query.filter((Film.isim.contains(search_query)) | (Film.yonetmen.contains(search_query))).all()
    else:
        filmler = Film.query.order_by(Film.id.desc()).all()
    return render_template_string(INDEX_TEMPLATE, filmler=filmler, search_query=search_query)


@app.route('/ekle', methods=['POST'])
def ekle():
    try:
        yeni_film = Film(
            isim=request.form.get('isim'),
            yonetmen=request.form.get('yonetmen'),
            yil=request.form.get('yil'),
            afis_url=request.form.get('afis_url'),
            puan=request.form.get('puan') if request.form.get('puan') else 0.0
        )
        db.session.add(yeni_film)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return f"Hata: {e}"
    return redirect(url_for('index'))


@app.route('/duzenle/<int:id>', methods=['GET', 'POST'])
def duzenle(id):
    film = Film.query.get_or_404(id)
    if request.method == 'POST':
        film.isim = request.form.get('isim')
        film.yonetmen = request.form.get('yonetmen')
        film.yil = request.form.get('yil')
        film.puan = request.form.get('puan')
        film.afis_url = request.form.get('afis_url')
        db.session.commit()
        return redirect(url_for('index'))
    return render_template_string(EDIT_TEMPLATE, film=film)


@app.route('/sil/<int:id>')
def sil(id):
    film = Film.query.get(id)
    if film:
        db.session.delete(film)
        db.session.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()