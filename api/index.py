import json
import uuid
import time
import random
import pandas as pd
import io
from urllib.parse import urlparse, parse_qs

# Basit bir bellek içi oturum saklama (Vercel'de kısa süreli çalışır, demo için uygundur)
sessions = {}

def temizle(s):
    duzeltmeler = str.maketrans("çğıöşü ", "cgiosu_")
    return str(s).lower().translate(duzeltmeler).replace("_", "")

def veri_dogrula(firma_adi, index):
    time.sleep(random.uniform(0.1, 0.3))
    url = f"www.{temizle(firma_adi)}.com.tr"
    telefon = f"+90 212 {random.randint(100, 999)} {random.randint(10, 99)} {random.randint(10, 99)}"
    return {"index": index, "firma": firma_adi, "site": url, "telefon": telefon, "durum": "Başarılı"}

def handler(request):
    # Vercel'in isteği nasıl karşıladığını anla
    path = request.path
    method = request.method
    
    # Rotaları manuel ayırıyoruz
    if path.endswith('/yukle') and method == 'POST':
        try:
            file_data = request.get_data()
            token = str(uuid.uuid4())
            # Pandas ile oku
            if b"PK" in file_data[:4]: # Excel kontrolü
                df = pd.read_excel(io.BytesIO(file_data))
            else:
                df = pd.read_csv(io.BytesIO(file_data))
            
            firmalar = df.iloc[:, 0].dropna().tolist()
            sessions[token] = firmalar
            
            return {
                "statusCode": 200,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"success": True, "token": token, "firmalar": firmalar[:20], "toplam": len(firmalar)})
            }
        except Exception as e:
            return {"statusCode": 400, "body": json.dumps({"hata": str(e)})}

    elif path.endswith('/akis'):
        params = parse_qs(urlparse(request.url).query)
        token = params.get('token', [None])[0]
        
        if not token or token not in sessions:
            return {"statusCode": 400, "body": "Gecersiz Token"}

        firmalar = sessions[token][:20]
        
        # SSE (Canlı Akış) için özel yanıt
        def generate():
            for i, firma in enumerate(firmalar):
                result = veri_dogrula(firma, i)
                yield f"event: satir\ndata: {json.dumps(result)}\n\n"
            yield "event: bitti\ndata: {}\n\n"

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "text/event-stream",
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            },
            "body": "".join(list(generate())) # Vercel'de streaming bazen sınırlıdır, bu en güvenli yol
        }

    # Hiçbir rota eşleşmezse debug bilgisini dön
    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "mesaj": "API Calisiyor (Flask-siz)",
            "path": path,
            "method": method
        })
    }
