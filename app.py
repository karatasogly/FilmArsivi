import urllib.parse
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


# --- VERİTABANI MODELİ ---
class Film(db.Model):
    __tablename__ = 'film'
    id = db.Column(db.Integer, primary_key=True)
    isim = db.Column(db.String(100), nullable=False)
    yonetmen = db.Column(db.String(100), nullable=False)
    yil = db.Column(db.Integer, nullable=True)
    puan = db.Column(db.Float, default=0.0)
    afis_url = db.Column(db.String(500), nullable=True)
    fragman_url = db.Column(db.String(500), nullable=True)  # YENİ SÜTUN


with app.app_context():
    # Sütun değişikliği olduğu için bir kez sıfırlama yapmalısın
    db.drop_all()
    db.create_all()

# --- TASARIM (CSS Güncellendi) ---
BASE_STYLE = '''
<style>
    body { font-family: 'Segoe UI', sans-serif; margin: 40px; background-color: #141414; color: white; }
    .container { max-width: 1200px; margin: auto; background: #1f1f1f; padding: 30px; border-radius: 15px; }
    input { padding: 12px; border-radius: 6px; border: 1px solid #333; background: #2b2b2b; color: white; width: 100%; box-sizing: border-box; margin-bottom: 10px; }
    .btn-add { background: #e50914; color: white; border: none; padding: 12px; border-radius: 6px; cursor: pointer; font-weight: bold; width: 100%; }
    .gallery { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 20px; margin-top: 20px; }
    .card { background: #262626; padding: 15px; border-radius: 12px; text-align: center; position: relative; border: 1px solid #333; transition: 0.3s; }
    .card:hover { transform: scale(1.02); border-color: #e50914; }
    .card img { width: 100%; height: 300px; object-fit: cover; border-radius: 8px; }
    .rating-badge { position: absolute; top: 20px; left: 20px; background: rgba(229, 9, 20, 0.9); color: white; padding: 4px 8px; border-radius: 5px; font-weight: bold; }
    .btn-trailer { display: inline-block; background: #333; color: #fff; padding: 8px 15px; border-radius: 20px; text-decoration: none; font-size: 12px; margin-top: 10px; border: 1px solid #e50914; }
    .btn-trailer:hover { background: #e50914; }
    .btn-delete { position: absolute; top: 10px; right: 10px; color: #777; text-decoration: none; }
    h2 { text-align: center; color: #e50914; }
</style>
'''

INDEX_TEMPLATE = BASE_STYLE + '''
<div class="container">
    <h2>🎬 Yusuf'un Film Arşivi</h2>

    <form method="POST" action="/ekle" style="display: grid; grid-template-columns: repeat(3, 1fr) 0.5fr 0.5fr 1fr auto; gap: 8px; margin-bottom: 30px;">
        <input type="text" name="isim" placeholder="Film Adı" required>
        <input type="text" name="yonetmen" placeholder="Yönetmen" required>
        <input type="text" name="afis_url" placeholder="Afiş URL">
        <input type="number" name="yil" placeholder="Yıl">
        <input type="number" name="puan" placeholder="Puan" step="0.1">
        <input type="text" name="fragman_url" placeholder="YouTube Fragman Linki">
        <button type="submit" class="btn-add">EKLE</button>
    </form>

    <div class="gallery">
        {% for film in filmler %}
        <div class="card">
            <a href="{{ url_for('sil', id=film.id) }}" class="btn-delete" onclick="return confirm('Silinsin mi?')">×</a>
            <div class="rating-badge">⭐ {{ film.puan }}</div>
            <img src="{{ film.afis_url if film.afis_url else 'https://via.placeholder.com/200x300?text=Resim+Yok' }}">
            <h4 style="margin: 10px 0 5px 0;">{{ film.isim }} ({{ film.yil }})</h4>
            <p style="color: #999; font-size: 13px;">{{ film.yonetmen }}</p>

            {% if film.fragman_url %}
            <a href="{{ film.fragman_url }}" target="_blank" class="btn-trailer">▶ Fragman İzle</a>
            {% endif %}
            <br>
            <a href="{{ url_for('duzenle', id=film.id) }}" style="color: #007bff; font-size: 12px; text-decoration: none;">Düzenle</a>
        </div>
        {% endfor %}
    </div>
</div>
'''


# (Düzenle template'i ve rotaları fragman_url dahil edilerek güncellendi...)
# --- ROTALAR ---

@app.route('/')
def index():
    filmler = Film.query.order_by(Film.id.desc()).all()
    return render_template_string(INDEX_TEMPLATE, filmler=filmler)


@app.route('/ekle', methods=['POST'])
def ekle():
    try:
        yeni_film = Film(
            isim=request.form.get('isim'),
            yonetmen=request.form.get('yonetmen'),
            yil=request.form.get('yil'),
            puan=request.form.get('puan') if request.form.get('puan') else 0.0,
            afis_url=request.form.get('afis_url'),
            fragman_url=request.form.get('fragman_url')
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
        film.fragman_url = request.form.get('fragman_url')
        db.session.commit()
        return redirect(url_for('index'))
    return render_template_string("Kayıt Güncelleme Sayfası", film=film)  # Basitleştirildi


@app.route('/sil/<int:id>')
def sil(id):
    film = Film.query.get(id)
    if film:
        db.session.delete(film)
        db.session.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run()