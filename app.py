import urllib.parse
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- CONFIGURATION (Görüntüye Göre Tam İsabet) ---
SERVER = 'yusuf-film-server-sweden.database.windows.net'
# DATABASE ismini görüntündeki gerçek isimle değiştirdim:
DATABASE = 'yusuf-film-server-sweden'
USERNAME = 'Yusuf2323'
PASSWORD = 'yusuf.2323'
DRIVER = '{ODBC Driver 17 for SQL Server}'

# Bağlantı dizesini hatasız kuruyoruz
connection_string = (
    f"Driver={DRIVER};"
    f"Server=tcp:{SERVER},1433;"
    f"Database={DATABASE};"
    f"Uid={USERNAME};"
    f"Pwd={PASSWORD};"
    f"Encrypt=yes;"
    f"TrustServerCertificate=no;"
    f"Connection Timeout=30;"
)

params = urllib.parse.quote_plus(connection_string)
app.config['SQLALCHEMY_DATABASE_URI'] = "mssql+pyodbc:///?odbc_connect=" + params
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- MODEL ---
class Film(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isim = db.Column(db.String(100), nullable=False)

# --- BAĞLANTIYI TEST ET ---
with app.app_context():
    try:
        db.create_all()
        print("\n" + "🚀" * 15)
        print("BAŞARILI! Veritabanı ismi düzeltildi ve bağlantı kuruldu.")
        print("🚀" * 15 + "\n")
    except Exception as e:
        print("\n" + "❌" * 15)
        print(f"Hala bir pürüz var: {e}")
        print("❌" * 15 + "\n")

@app.route('/')
def index():
    return "<h1>Azure SQL Bağlantısı Tamam Yusuf!</h1>"

if __name__ == '__main__':
    app.run(debug=True)