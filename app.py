import urllib.parse
from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- CONFIG ---
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

# --- MODEL (Puan Sütunu Eklendi) ---
class Film(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isim = db.Column(db.String(100), nullable=False)
    yonetmen = db.Column(db.String(100), nullable=False)
    afis_url = db.Column(db.String(500), nullable=True)
    puan = db.Column(db.Float, default=0.0) # Yeni Sütun: IMDB Puanı

with app.app_context():
    # DİKKAT: Puan sütunu için tabloyu bir kez sıfırlamalıyız.
    db.drop_all() # <-- Hata alırsan '#' kaldır, bir kez çalıştır, sonra geri koy.
    db.create_all()

# --- TASARIM (Puanlar ve Rozetler Eklendi) ---
BASE_STYLE = '''
<style>
    body { font-family: 'Segoe UI', sans-serif; margin: 40px; background-color: #141414; color: white; }
    .container { max-width: 1000px; margin: auto; background: #1f1f1f; padding: 30px; border-radius: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    input, select { padding: 12px; border-radius: 6px; border: 1px solid #333; background: #2b2b2b; color: white; width: 100%; box-sizing: border-box; margin-bottom: 10px; }
    .btn-add { background: #e50914; color: white; border: none; padding: 12px; border-radius: 6px; cursor: pointer; font-weight: bold; width: 100%; }
    .gallery { display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 25px; margin-top: 20px; }
    .card { background: #262626; padding: 15px; border-radius: 12px; text-align: center; position: relative; border: 1px solid #333; }
    .card img { width: 100%; height: 300px; object-fit: cover; border-radius: 8px; margin-bottom: 10px; }
    .rating-badge { position: absolute; top: 20px; left: 20px; background: rgba(229, 9, 20, 0.9); color: white; padding: 5px 10px; border-radius: 5px; font-weight: bold; font-size: 14px; }
    .btn-delete { position: absolute; top: 10px; right: 10px; color: #777; text-decoration: none; font-size: 20px; }
    .btn-delete:hover { color: #e50914; }
    .btn-edit { display: inline-block; margin-top: 10px; color: #007bff; text-decoration: none; font-size: 14px; }
    h2 { text-align: center; color: #e50914; text-transform: uppercase; letter-spacing: 2px; }
</style>
'''

INDEX_TEMPLATE = BASE_STYLE + '''
<div class="container">
    <h2>Yusuf'un Film Arşivi</h2>
    <form method="GET" action="/" style="margin-bottom: 20px;">
        <input type="text" name="search" placeholder="Film veya yönetmen ara..." value="{{ search_query }}">
    </form>
    <form method="POST" action="/ekle" style="display: grid; grid-template-columns: 2fr 1.5fr 1.5fr 0.8fr auto; gap: 10px; margin-bottom: 30px;">
        <input type="text" name="isim" placeholder="Film Adı" required>
        <input type="text" name="yonetmen" placeholder="Yönetmen" required>
        <input type="text" name="afis_url" placeholder="Afiş Link">
        <input type="number" name="puan" placeholder="Puan" step="0.1" min="0" max="10">
        <button type="submit" class="btn-add">EKLE</button>
    </form>
    <div class="gallery">
        {% for film in filmler %}
        <div class="card">
            <a href="{{ url_for('sil', id=film.id) }}" class="btn-delete" onclick="return confirm('Sileyim mi Yusuf?')">×</a>
            <div class="rating-badge">⭐ {{ film.puan }}</div>
            <img src="{{ film.afis_url if film.afis_url else 'https://via.placeholder.com/200x300?text=Afiş+Yok' }}">
            <h4 style="margin: 10px 0 5px 0;">{{ film.isim }}</h4>
            <p style="color: #999; font-size: 13px; margin: 0;">{{ film.yonetmen }}</p>
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
        <input type="text" name="isim" value="{{ film.isim }}" required>
        <input type="text" name="yonetmen" value="{{ film.yonetmen }}" required>
        <input type="text" name="afis_url" value="{{ film.afis_url }}">
        <input type="number" name="puan" value="{{ film.puan }}" step="0.1" min="0" max="10">
        <button type="submit" class="btn-add">BİLGİLERİ GÜNCELLE</button>
        <a href="/" style="display: block; text-align: center; color: #777; margin-top: 15px; text-decoration: none;">İptal Et</a>
    </form>
</div>
'''

# --- ROUTES ---
@app.route('/')
def index():
    search_query = request.args.get('search', '')
    if search_query:
        filmler = Film.query.filter((Film.isim.contains(search_query)) | (Film.yonetmen.contains(search_query))).all()
    else:
        filmler = Film.query.order_by(Film.puan.desc()).all() # Puanı yüksek olan en üstte
    return render_template_string(INDEX_TEMPLATE, filmler=filmler, search_query=search_query)

@app.route('/ekle', methods=['POST'])
def ekle():
    puan_val = request.form.get('puan')
    yeni_film = Film(
        isim=request.form.get('isim'),
        yonetmen=request.form.get('yonetmen'),
        afis_url=request.form.get('afis_url'),
        puan=float(puan_val) if puan_val else 0.0
    )
    db.session.add(yeni_film)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/duzenle/<int:id>', methods=['GET', 'POST'])
def duzenle(id):
    film = Film.query.get_or_404(id)
    if request.method == 'POST':
        film.isim = request.form.get('isim')
        film.yonetmen = request.form.get('yonetmen')
        film.afis_url = request.form.get('afis_url')
        puan_val = request.form.get('puan')
        film.puan = float(puan_val) if puan_val else 0.0
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
    app.run(debug=True)