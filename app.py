from flask import Flask, request, render_template_string
import os
import psycopg2

app = Flask(__name__)

def connect_db():
    DATABASE_URL = os.environ.get('DATABASE_URL')
    return psycopg2.connect(DATABASE_URL, sslmode='require')

HTML_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Ziyaretçi Defteri</title>
    <style>
        body { font-family: sans-serif; max-width: 500px; margin: 50px auto; line-height: 1.6; background-color: #f4f4f4; }
        .container { background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        input, textarea { width: 100%; padding: 10px; margin: 5px 0; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        button { background: #28a745; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; width: 100%; }
        .mesaj-kutusu { border-bottom: 1px solid #eee; padding: 15px 0; }
        .mesaj-kutusu:last-child { border-bottom: none; }
    </style>
</head>
<body>
    <div class="container">
        <h2>Ziyaretçi Defteri</h2>
        <form method="POST">
            <input type="text" name="isim" placeholder="Adınız" required>
            <textarea name="mesaj" placeholder="Mesajınız" required></textarea>
            <button type="submit">Mesajı Paylaş</button>
        </form>
        <hr>
        <h3>Gelen Mesajlar</h3>
        {% for isim, mesaj in mesajlar %}
            <div class="mesaj-kutusu">
                <strong>{{ isim }}:</strong> {{ mesaj }}
            </div>
        {% endfor %}
    </div>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    conn = connect_db()
    cur = conn.cursor()
    
    # 1. Tabloyu oluştur
    cur.execute("CREATE TABLE IF NOT EXISTS mesajlar (id SERIAL PRIMARY KEY, isim TEXT, mesaj TEXT);")
    
    # 2. TEMİZLİK SATIRI: Gemini ismindeki eski test verilerini siler
    cur.execute("DELETE FROM mesajlar WHERE isim = 'Gemini';")
    conn.commit()
    
    if request.method == 'POST':
        isim = request.form.get('isim')
        mesaj = request.form.get('mesaj')
        if isim and mesaj:
            cur.execute("INSERT INTO mesajlar (isim, mesaj) VALUES (%s, %s)", (isim, mesaj))
            conn.commit()

    # Mesajları en yeniden en eskiye çek
    cur.execute("SELECT isim, mesaj FROM mesajlar ORDER BY id DESC;")
    tum_mesajlar = cur.fetchall()
    
    cur.close()
    conn.close()
    
    return render_template_string(HTML_TEMPLATE, mesajlar=tum_mesajlar)

if __name__ == '__main__':
    app.run(debug=True)
