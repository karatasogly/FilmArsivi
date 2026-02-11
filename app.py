import urllib
from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# --- AZURE SQL BAGLANTI AYARI ---
# Kopyaladığın ADO.NET kodunu buraya tırnak içine yapıştır.
# Password={your_password} kısmını silip kendi şifreni yazmayı UNUTMA!
raw_db_url = "Server=tcp:yusuf-film-server-sweden.database.windows.net,1433;Initial Catalog=free-sql-db-7161867;Persist Security Info=False;User ID=Yusuf2323;Password=BURAYA_KENDI_SIFRENI_YAZ;MultipleActiveResultSets=False;Encrypt=True;TrustServerCertificate=False;Connection Timeout=30;"

# Azure ve Python arasındaki bağlantı köprüsü
params = urllib.parse.quote_plus(raw_db_url)
app.config['SQLALCHEMY_DATABASE_URI'] = f"mssql+pyodbc:///?odbc_connect={params}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# --- VERITABANI MODELI (ORNEK) ---
class Film(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    isim = db.Column(db.String(100), nullable=False)
    yonetmen = db.Column(db.String(100), nullable=False)

# Veritabanı tablolarını oluşturur (Azure'da tablo yoksa oluşturur)
with app.app_context():
    db.create_all()

# --- ROUTE'LAR (SAYFALAR) ---
@app.route('/')
def index():
    filmler = Film.query.all()
    return f"Azure SQL Baglantisi Basarili! Toplam Film Sayisi: {len(filmler)}"

if __name__ == '__main__':
    app.run(debug=True)