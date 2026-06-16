from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import json
import uuid
import time
import random
import pandas as pd
import io

# Vercel'in hata vermemesi için "app" nesnesi şart
app = Flask(__name__)
CORS(app)

sessions = {}

def temizle(s):
    duzeltmeler = str.maketrans("çğıöşü ", "cgiosu_")
    return str(s).lower().translate(duzeltmeler).replace("_", "")

def veri_dogrula(firma_adi, index):
    time.sleep(random.uniform(0.1, 0.3))
    url = f"www.{temizle(firma_adi)}.com.tr"
    telefon = f"+90 212 {random.randint(100, 999)} {random.randint(10, 99)} {random.randint(10, 99)}"
    return {"index": index, "firma": firma_adi, "site": url, "telefon": telefon, "durum": "Başarılı"}

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST', 'OPTIONS'])
def catch_all(path):
    if request.method == 'OPTIONS': return '', 200
    
    # Yolun sonuna bakarak nereye gideceğine karar ver
    if path.endswith('yukle'): return yukle()
    if path.endswith('akis'): return akis()
    if path.endswith('ping'): return ping()
    
    return jsonify({
        "status": "online",
        "received_path": path,
        "message": "Firma Otomasyon API Calisiyor. Gecerli uclar: /yukle, /akis, /ping"
    })

def yukle():
    try:
        file_data = request.get_data()
        token = str(uuid.uuid4())
        if b"PK" in file_data[:4]: # Excel
            df = pd.read_excel(io.BytesIO(file_data))
        else:
            df = pd.read_csv(io.BytesIO(file_data))
        
        firmalar = df.iloc[:, 0].dropna().tolist()
        sessions[token] = firmalar
        return jsonify({"success": True, "token": token, "firmalar": firmalar[:20], "toplam": len(firmalar)})
    except Exception as e:
        return jsonify({"success": False, "hata": str(e)}), 400

@app.route('/api/ping')
def ping():
    return jsonify({"status": "ok", "message": "Vercel API Calisiyor"})

def akis():
    token = request.args.get('token')
    if not token or token not in sessions:
        return "Hata: Gecersiz Token", 400

    firmalar = sessions[token][:20]
    def generate():
        for i, firma in enumerate(firmalar):
            result = veri_dogrula(firma, i)
            yield f"event: satir\ndata: {json.dumps(result)}\n\n"
        yield "event: bitti\ndata: {}\n\n"

    return Response(stream_with_context(generate()), mimetype="text/event-stream")

# Vercel için app nesnesini dışa aktarıyoruz
if __name__ == "__main__":
    app.run()
