import urllib.parse
from flask import Flask, render_template_string, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- AYARLAR (Görüntündeki Bilgiler) ---
SERVER = 'yusuf-film-server-sweden.database.windows.net'
DATABASE = 'yusuf-film-server-sweden'
USERNAME = 'Yusuf2323'
PASSWORD = 'yusuf.2323' # Azure'da belirlediğin şifre
DRIVER = '{ODBC Driver 17 for SQL Server}'

# Bağlantı dizesi
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

# --- TABLO SIFIRLAMA VE OLUŞTURMA ---
with app.app_context():
    try:
        # ProgrammingError almamak için eski tabloyu silip yenisini kuruyoruz
        db.drop_all()
        db.create_all()
        print("\n🚀 Veritabanı tabloları başarıyla güncellendi!")
    except Exception as e:
        print(f"\n❌ Tablo oluşturma hatası: {e}")

# --- ARAYÜZ (HTML) ---
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Yusuf Film Arşivi</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; margin: 40px; background-color: #e9ecef; }
        .container { max-width: 600px; margin: auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        h2 { color: #343a40; text-align: center; }
        input { width: 90%; padding: 12px; margin: 10px 0; border: 1px solid #ced4da; border-radius: 6px; }
        button { width: 95%; padding: 12px; background: #28a745; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 16px; }
        button:hover { background: #218838; }
        table { width: 100%; margin-top: 30px; border-collapse: collapse; }
        th, td { padding: 12px; border-bottom: 1px solid #dee2e6; text-align: left; }
        th { background-color: #007bff; color: white; border-radius: 4px 4px 0 0; }
        tr:hover { background-color: #f8f9fa; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🎬 Film Arşivi (Azure SQL)</h2>
        <form method="POST" action="/ekle">
            <input type="text" name="isim" placeholder="Film Adı" required>
            <input type="text" name="yonetmen" placeholder="Yönetmen" required>
            <button type="submit">Listeye Ekle</button>
        </form>

        <table>
            <thead>
                <tr>
                    <th>Film Adı</th>
                    <th>Yönetmen</th>
                </tr>
            </thead>
            <tbody>
                {% for film in filmler %}
                <tr>
                    <td>{{ film.isim }}</td>
                    <td>{{ film.yonetmen }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>
'''

# --- YOLLAR (ROUTES) ---
@app.route('/')
def index():
    filmler = Film.query.all()
    return render_template_string(HTML_TEMPLATE, filmler=filmler)

@app.route('/ekle', methods=['POST'])
def ekle():
    yeni_film = Film(
        isim=request.form.get('isim'),
        yonetmen=request.form.get('yonetmen')
    )
    db.session.add(yeni_film)
    db.session.commit()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)