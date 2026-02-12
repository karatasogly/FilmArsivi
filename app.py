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

connection_string = f"Driver={DRIVER};Server=tcp:{SERVER},1433;Database={DATABASE};Uid={USERNAME};Pwd={PASSWORD};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=120;"
params = urllib.parse.quote_plus(connection_string)
app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=" + params
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
# Bağlantı kopmalarını önlemek için havuz ayarı
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {"pool_pre_ping": True, "pool_recycle": 300}

db = SQLAlchemy(app)


# --- MODEL ---
class Film(db.Model):
    __tablename__ = 'film'
    id = db.Column(db.Integer, primary_key=True)
    isim = db.Column(db.String(100), nullable=False)
    yonetmen = db.Column(db.String(100), nullable=False)
    puan = db.Column(db.Float)
    tur = db.Column(db.String(50))
    afis_url = db.Column(db.String(500))
    fragman_url = db.Column(db.String(500))


with app.app_context():
    # Sütun yapısı değiştiyse (video hover için fragman_url lazım) bir kez çalıştır:
    # db.drop_all()
    db.create_all()

# --- CSS VE JS (HOVER EFFECT) ---
INDEX_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>YusufFlix</title>
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;700;900&display=swap');
        body { background: #080808; color: white; font-family: 'Poppins', sans-serif; margin: 0; }
        .nav { padding: 20px 50px; background: rgba(0,0,0,0.9); display: flex; justify-content: space-between; align-items: center; }
        .container { padding: 40px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 30px; }

        .card { 
            background: #141414; border-radius: 8px; overflow: hidden; 
            position: relative; transition: transform 0.3s; cursor: pointer;
        }
        .card:hover { transform: scale(1.08); z-index: 5; box-shadow: 0 10px 30px rgba(0,0,0,0.8); }

        .media-box { position: relative; width: 100%; height: 380px; background: #000; }
        .poster { width: 100%; height: 100%; object-fit: cover; transition: 0.3s; }
        .video-overlay { 
            position: absolute; top: 0; left: 0; width: 100%; height: 100%; 
            opacity: 0; transition: 0.5s; pointer-events: none;
        }

        .card:hover .poster { opacity: 0; }
        .card:hover .video-overlay { opacity: 1; }

        .info { padding: 15px; }
        .add-form { background: #1a1a1a; padding: 20px; border-radius: 10px; margin-bottom: 30px; display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 10px; }
        input { background: #333; border: none; padding: 10px; color: white; border-radius: 5px; }
        button { background: #e50914; color: white; border: none; padding: 10px; border-radius: 5px; font-weight: bold; cursor: pointer; }
    </style>
</head>
<body>
    <div class="nav">
        <h2 style="color:#e50914; margin:0;">YUSUF<span style="color:white">FLIX</span></h2>
    </div>
    <div class="container">
        <form class="add-form" action="/ekle" method="POST">
            <input type="text" name="isim" placeholder="Film Adı" required>
            <input type="text" name="yonetmen" placeholder="Yönetmen" required>
            <input type="text" name="afis" placeholder="Afiş URL">
            <input type="text" name="fragman" placeholder="YouTube Link">
            <input type="number" step="0.1" name="puan" placeholder="Puan">
            <button type="submit">EKLE</button>
        </form>

        <div class="grid">
            {% for film in filmler %}
            <div class="card" onmouseenter="startPlayer('{{ film.id }}')" onmouseleave="stopPlayer('{{ film.id }}')">
                <div class="media-box">
                    <img class="poster" id="img-{{ film.id }}" src="{{ film.afis_url }}">
                    {% if film.fragman_url %}
                        {% set v_id = film.fragman_url.split('v=')[-1].split('&')[0] if 'v=' in film.fragman_url else film.fragman_url.split('/')[-1] %}
                        <iframe class="video-overlay" id="vid-{{ film.id }}" 
                            src="https://www.youtube.com/embed/{{ v_id }}?enablejsapi=1&mute=1&controls=0&autoplay=0" 
                            frameborder="0"></iframe>
                    {% endif %}
                </div>
                <div class="info">
                    <div style="font-weight:bold;">{{ film.isim }}</div>
                    <div style="font-size:12px; color:#888;">{{ film.yonetmen }} • ★ {{ film.puan }}</div>
                    <a href="/sil/{{ film.id }}" style="color:#444; font-size:10px; text-decoration:none;">SİL</a>
                </div>
            </div>
            {% endfor %}
        </div>
    </div>

    <script>
        function startPlayer(id) {
            var iframe = document.getElementById('vid-' + id);
            if(iframe) {
                iframe.contentWindow.postMessage('{"event":"command","func":"playVideo","args":""}', '*');
            }
        }
        function stopPlayer(id) {
            var iframe = document.getElementById('vid-' + id);
            if(iframe) {
                iframe.contentWindow.postMessage('{"event":"command","func":"pauseVideo","args":""}', '*');
                iframe.contentWindow.postMessage('{"event":"command","func":"seekTo","args":[0, true]}', '*');
            }
        }
    </script>
</body>
</html>
'''


@app.route('/')
def index():
    try:
        # Hatalı olan 'order' kısmı 'order_by' olarak düzeltildi
        filmler = Film.query.order_by(Film.id.desc()).all()
        return render_template_string(INDEX_TEMPLATE, filmler=filmler)
    except Exception as e:
        return f"Veritabanı meşgul, lütfen sayfayı yenile Yusuf! Hata: {str(e)}"


@app.route('/ekle', methods=['POST'])
def ekle():
    yeni = Film(
        isim=request.form.get('isim'),
        yonetmen=request.form.get('yonetmen'),
        afis_url=request.form.get('afis'),
        fragman_url=request.form.get('fragman'),
        puan=request.form.get('puan') or 0
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