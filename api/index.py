from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import time
import random
import json
import uuid
import pandas as pd
import io

app = Flask(__name__)
CORS(app)

sessions = {}

def temizle(s):
    duzeltmeler = str.maketrans("çğıöşü ", "cgiosu_")
    return str(s).lower().translate(duzeltmeler).replace("_", "")

def veri_dogrula(firma_adi, index):
    time.sleep(random.uniform(0.3, 0.7))
    url = f"www.{temizle(firma_adi)}.com.tr"
    telefon = f"+90 212 {random.randint(100, 999)} {random.randint(10, 99)} {random.randint(10, 99)}"
    return {
        "index": index,
        "firma": firma_adi,
        "site": url,
        "telefon": telefon,
        "durum": "Başarılı"
    }

@app.before_request
def log_request_info():
    print(f"Request: {request.method} {request.path}")
    # print(f"Headers: {dict(request.headers)}")

@app.route('/debug')
def debug():
    return jsonify({
        "path": request.path,
        "full_path": request.full_path,
        "url": request.url,
        "headers": dict(request.headers)
    })

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST', 'OPTIONS'])
def catch_all(path):
    # Vercel'den gelen yolları temizle ve ilgili fonksiyona yönlendir
    clean_path = path.split('/')[-1]
    
    if clean_path == 'yukle':
        return yukle()
    if clean_path == 'akis':
        return akis()
    if clean_path == 'indir':
        return indir()
    if clean_path == 'ping':
        return ping()
    if clean_path == 'debug' or path == '':
        return debug()
    
    return jsonify({
        "error": "Not Found",
        "message": f"'{path}' rotasi Flask tarafindan bulunamadi.",
        "path": path,
        "clean_path": clean_path
    }), 404

@app.route('/api/ping')
def ping():
    return jsonify({"status": "ok", "message": "Server is running"})

def yukle():
    try:
        file_data = request.get_data()
        filename = request.headers.get('X-Dosya-Adi', 'liste.xlsx')
        if filename.endswith('.csv'):
            df = pd.read_csv(io.BytesIO(file_data))
        else:
            df = pd.read_excel(io.BytesIO(file_data))
        firmalar = df.iloc[:, 0].dropna().tolist()
        token = str(uuid.uuid4())
        sessions[token] = firmalar
        return jsonify({
            "success": True, 
            "token": token, 
            "firmalar": firmalar[:20],
            "toplam": len(firmalar),
            "sinir": 20
        })
    except Exception as e:
        return jsonify({"success": False, "hata": str(e)}), 400

def xlsx_uret(sonuclar):
    output = io.BytesIO()
    writer = pd.ExcelWriter(output, engine='openpyxl')
    df = pd.DataFrame(sonuclar)
    df.to_excel(writer, index=False, sheet_name='Sonuçlar')
    writer.close()
    return output.getvalue()

@app.route('/akis')
@app.route('/api/akis')
def akis():
    token = request.args.get('token')
    if not token or token not in sessions:
        return "Hata: Gecersiz Token", 400
    
    firmalar = sessions[token][:20]
    sonuclar = []
    
    def generate():
        for i, firma in enumerate(firmalar):
            result = veri_dogrula(firma, i)
            sonuclar.append(result)
            yield f"event: satir\ndata: {json.dumps(result)}\n\n"
        
        # Sonuçları oturuma kaydet (indirme için)
        sessions[token + "_sonuc"] = sonuclar
        yield "event: bitti\ndata: {}\n\n"
    
    return Response(stream_with_context(generate()), mimetype="text/event-stream")

@app.route('/indir')
@app.route('/api/indir')
def indir():
    token = request.args.get('token')
    sonuclar = sessions.get(token + "_sonuc")
    if not sonuclar:
        return "Dosya bulunamadı", 404
    
    xlsx_data = xlsx_uret(sonuclar)
    return Response(
        xlsx_data,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-disposition": "attachment; filename=firmalar_sonuc.xlsx"}
    )

# Vercel, app nesnesini otomatik olarak bulur.
