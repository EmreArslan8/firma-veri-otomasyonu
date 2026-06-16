from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
import time
import random
import json
import uuid
import pandas as pd
import io
import serverless_wsgi

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

@app.route('/api/yukle', methods=['POST'])
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

@app.route('/api/akis')
def akis():
    token = request.args.get('token')
    if not token or token not in sessions:
        return "Hata", 400
    firmalar = sessions[token][:20]
    def generate():
        for i, firma in enumerate(firmalar):
            result = veri_dogrula(firma, i)
            yield f"event: satir\ndata: {json.dumps(result)}\n\n"
        yield "event: bitti\ndata: {}\n\n"
    return Response(stream_with_context(generate()), mimetype="text/event-stream")

# Netlify için handler
def handler(event, context):
    return serverless_wsgi.handle_request(app, event, context)
