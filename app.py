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

# Artık tabloların hazır olduğu için drop_all() yapmana gerek yok.
with app.app_context():
    db.create_all()

# --- ARAYÜZ (Silme Butonu Eklendi) ---
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Yusuf Film Arşivi</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; margin: 40px; background-color: #f8f9fa; }
        .container { max-width: 700px; margin: auto; background: white; padding: 30px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); }
        h2 { color: #333; text-align: center; }
        .form-group { display: flex; gap: 10px; margin-bottom: 20px; }
        input { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 6px; }
        .btn-add { background: #28a745; color: white; border: none; padding: 12px 20px; border-radius: 6px; cursor: pointer; }
        .btn-delete { background: #dc3545; color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer; text-decoration: none; font-size: 13px; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 12px; border-bottom: 1px solid #eee; text-align: left; }
        th { background: #007bff; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <h2>🎬 Film Arşivi (Azure SQL)</h2>
        <form method="POST" action="/ekle" class="form-group">
            <input type="text" name="isim" placeholder="Film Adı" required>
            <input type="text" name="yonetmen" placeholder="Yönetmen" required>
            <button type="submit" class="btn-add">Ekle</button>
        </form>

        <table>
            <thead>
                <tr>
                    <th>Film</th>
                    <th>Yönetmen</th>
                    <th>İşlem</th>
                </tr>
            </thead>
            <tbody>
                {% for film in filmler %}
                <tr>
                    <td>{{ film.isim }}</td>
                    <td>{{ film.yonetmen }}</td>
                    <td>
                        <a href="{{ url_for('sil', id=film.id) }}" class="btn-delete" onclick="return confirm('Emin misin?')">Sil</a>
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</body>
</html>
'''

# --- ROUTES ---
@app.route('/')
def index():
    filmler = Film.query.all()
    return render_template_string(HTML_TEMPLATE, filmler=filmler)

@app.route('/ekle', methods=['POST'])
def ekle():
    yeni_film = Film(isim=request.form.get('isim'), yonetmen=request.form.get('yonetmen'))
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