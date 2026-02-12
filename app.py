import urllib.parse
from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- VERİTABANI BAĞLANTISI (Uyanma Süresi Optimize Edildi) ---
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


# --- FİLM MODELİ ---
class Film(db.Model):
    __tablename__ = 'film'
    id = db.Column(db.Integer, primary_key=True)
    isim = db.Column(db.String(100), nullable=False)
    yonetmen = db.Column(db.String(100), nullable=False)
    puan = db.Column(db.Float)
    afis_url = db.Column(db.String(500))
    fragman_url = db.Column(db.String(500))


with app.app_context():
    db.create_all()

# --- TEK SAYFA TASARIMI (YouTube Arayüzü ve Hover Efekti) ---
INDEX_TEMPLATE = '''
<!DOCTYPE html>
<html lang="tr">
<head>
    <meta charset="UTF-8">
    <title>YusufFlix - Orijinal Film Arşivi</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;700;900&display=swap');
        body { background: #080808; color: white; font-family: 'Poppins', sans-serif; margin: 0; padding: 20px; }
        .logo { color: #e50914; font-size: 40px; font-weight: 900; text-align: center; margin-bottom: 30px; }

        .container { max-width: 1200px; margin: auto; }

        /* Film Ekleme Formu */
        .add-box { background: #141414; padding: 25px; border-radius: 12px; margin-bottom: 40px; border: 1px solid #333; }
        .input-group { display: flex; flex-wrap: wrap; gap: 10px; }
        input { background: #222; border: 1px solid #444; padding: 12px; color: white; border-radius: 6px; flex: 1; min-width: 150px; }
        button { background: #e50914; color: white; border: none; padding: 12px 25px; border-radius: 6px; font-weight: bold; cursor: pointer; transition: 0.3s; }
        button:hover { background: #b2070f; }

        /* Film Kartları Grid Yapısı */
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 30px; }

        .card { 
            background: #111; border-radius: 15px; overflow: hidden; 
            position: relative; height: 480px; transition: transform 0.3s ease;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        }
        .card:hover { transform: scale(1.02); }

        /* Katmanlar: Afiş üstte, Video altta */
        .poster { 
            width: 100%; height: 100%; object-fit: cover; 
            position: absolute; top: 0; left: 0; z-index: 10; 
            transition: opacity 0.5s ease; 
        }
        .card:hover .poster { opacity: 0; pointer-events: none; }

        .video-box { 
            width: 100%; height: 100%; position: absolute; top: 0; left: 0; z-index: 5; 
            background: #000;
        }

        /* Film Bilgileri */
        .info { 
            position: absolute; bottom: 0; left: 0; width: 100%; 
            background: linear-gradient(transparent, rgba(0,0,0,0.95)); 
            padding: 20px; z-index: 15; pointer-events: none; 
        }
        .info h3 { margin: 0; font-size: 20px; }
        .info p { margin: 5px 0 0; color: #aaa; font-size: 14px; }

        .delete-link { 
            position: absolute; top: 10px; left: 10px; z-index: 20;
            background: rgba(0,0,0,0.6); color: #888; text-decoration: none; 
            padding: 5px 10px; border-radius: 5px; font-size: 11px;
        }
        .delete-link:hover { background: red; color: white; }
    </style>
</head>
<body>
    <div class="logo">YUSUF<span style="color:white">FLIX</span></div>

    <div class="container">
        <div class="add-box">
            <h4 style="margin-top:0; color:#aaa;">Yeni Film Ekle</h4>
            <form action="/ekle" method="POST" class="input-group">
                <input type="text" name="isim" placeholder="Film Adı" required>
                <input type="text" name="yonetmen" placeholder="Yönetmen" required>
                <input type="text" name="afis" placeholder="Afiş (Resim) URL">
                <input type="text" name="fragman" placeholder="YouTube Fragman Linki">
                <button type="submit">LİSTEYE EKLE</button>
            </form>
        </div>

        <div class="grid">
            {% for film in filmler %}
            <div class="card">
                <a href="/sil/{{ film.id }}" class="delete-link">SİL</a>
                <img class="poster" src="{{ film.afis_url if film.afis_url else 'https://via.placeholder.com/300x450?text=Afiş+Yok' }}">

                <div class="video-box">
                    {% if film.fragman_url %}
                        {% set v_id = film.fragman_url.split('v=')[-1].split('&')[0] if 'v=' in film.fragman_url else film.fragman_url.split('/')[-1] %}
                        {# controls=1 ve mute=0 ile YouTube'un orijinal halini getirdik #}
                        <iframe width="100%" height="100%" 
                            src="https://www.youtube.com/embed/{{ v_id }}?controls=1&modestbranding=0&rel=0&autoplay=0" 
                            frameborder="0" allowfullscreen>
                        </iframe>
                    {% else %}
                        <div style="padding:100px 20px; text-align:center; color:#444;">Video Bulunamadı</div>
                    {% endif %}
                </div>

                <div class="info">
                    <h3>{{ film.isim }}</h3>
                    <p>{{ film.yonetmen }}</p>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
'''


@app.route('/')
def index():
    try:
        # En son eklenen en üstte görünsün (Düzeltilmiş order_by)
        filmler = Film.query.order_by(Film.id.desc()).all()
        return render_template_string(INDEX_TEMPLATE, filmler=filmler)
    except Exception as e:
        return f"<h3>Veritabanı uyanıyor... Lütfen sayfayı yenile!</h3><p>{e}</p>"


@app.route('/ekle', methods=['POST'])
def ekle():
    yeni = Film(
        isim=request.form.get('isim'),
        yonetmen=request.form.get('yonetmen'),
        afis_url=request.form.get('afis'),
        fragman_url=request.form.get('fragman'),
        puan=8.0
    )
    db.session.add(yeni)
    db.session.commit()
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