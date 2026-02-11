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


# --- MODEL ---
class Film(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isim = db.Column(db.String(100), nullable=False)
    yonetmen = db.Column(db.String(100), nullable=False)
    afis_url = db.Column(db.String(500), nullable=True)


with app.app_context():
    db.create_all()  # Tablo yapısı değişmediği için drop_all yapmana gerek yok.

# --- ARAYÜZ (Arama Çubuğu Eklendi) ---
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Yusuf Film Galeri</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; margin: 40px; background-color: #1a1a1a; color: white; }
        .container { max-width: 900px; margin: auto; background: #2d2d2d; padding: 30px; border-radius: 15px; }
        .form-group { display: grid; grid-template-columns: 1fr 1fr 1fr auto; gap: 10px; margin-bottom: 20px; }
        .search-group { margin-bottom: 30px; }
        input { padding: 12px; border-radius: 6px; border: none; width: 100%; box-sizing: border-box; }
        .btn-add { background: #e50914; color: white; border: none; padding: 12px; border-radius: 6px; cursor: pointer; font-weight: bold; }
        .gallery { display: grid; grid-template-columns: repeat(auto-fill, minmax(200px, 1fr)); gap: 20px; }
        .card { background: #3d3d3d; padding: 10px; border-radius: 10px; text-align: center; position: relative; transition: 0.3s; }
        .card:hover { transform: scale(1.05); }
        .card img { width: 100%; height: 280px; object-fit: cover; border-radius: 8px; }
        .btn-delete { position: absolute; top: 5px; right: 5px; background: rgba(229, 9, 20, 0.8); color: white; border: none; border-radius: 50%; width: 25px; height: 25px; cursor: pointer; }
        h2 { text-align: center; color: #e50914; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🎬 Yusuf'un Film Galerisi</h2>

        <div class="search-group">
            <form method="GET" action="/">
                <input type="text" name="search" placeholder="Film ara..." value="{{ search_query }}">
            </form>
        </div>

        <form method="POST" action="/ekle" class="form-group">
            <input type="text" name="isim" placeholder="Film Adı" required>
            <input type="text" name="yonetmen" placeholder="Yönetmen" required>
            <input type="text" name="afis_url" placeholder="Afiş Resim URL (Link)">
            <button type="submit" class="btn-add">EKLE</button>
        </form>

        <div class="gallery">
            {% for film in filmler %}
            <div class="card">
                <a href="{{ url_for('sil', id=film.id) }}" class="btn-delete">×</a>
                <img src="{{ film.afis_url if film.afis_url else 'https://via.placeholder.com/200x300?text=Afiş+Yok' }}">
                <h3>{{ film.isim }}</h3>
                <p>{{ film.yonetmen }}</p>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
'''


# --- ROUTES ---
@app.route('/')
def index():
    search_query = request.args.get('search', '')
    if search_query:
        # Veritabanında arama yap (isim içinde geçiyorsa getir)
        filmler = Film.query.filter(Film.isim.contains(search_query)).all()
    else:
        filmler = Film.query.all()
    return render_template_string(HTML_TEMPLATE, filmler=filmler, search_query=search_query)


@app.route('/ekle', methods=['POST'])
def ekle():
    yeni_film = Film(
        isim=request.form.get('isim'),
        yonetmen=request.form.get('yonetmen'),
        afis_url=request.form.get('afis_url')
    )
    db.session.add(yeni_film)
    db.session.commit()
    return redirect(url_for('index'))


@app.route('/sil/<int:id>')
def sil(id):
    film = Film.query.get(id)
    if film:
        db.session.delete(film)
        db.session.commit()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)