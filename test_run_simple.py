import time
import random
import csv
from concurrent.futures import ThreadPoolExecutor

class FirmaOtomasyonu:
    def __init__(self, max_threads=5):
        self.max_threads = max_threads

    def veri_dogrula(self, firma_adi):
        # İşlem süresi simülasyonu
        time.sleep(random.uniform(0.3, 0.8))
        
        # Domain oluşturma (Türkçe karakter düzeltme)
        def temizle(s):
            duzeltmeler = str.maketrans("çğıöşü ", "cgiosu_")
            return s.lower().translate(duzeltmeler).replace("_", "")

        url = f"www.{temizle(firma_adi)}.com.tr"
        telefon = f"+90 212 {random.randint(100, 999)} {random.randint(10, 99)} {random.randint(10, 99)}"
        durum = "Başarılı" if random.random() > 0.1 else "Manuel Kontrol"
        skor = f"%{random.randint(85, 99)}"
        
        return [firma_adi, url, telefon, durum, skor]

    def calistir(self, firma_listesi):
        print("-" * 85)
        print(f"{'Firma Adı':<25} | {'Web Sitesi':<25} | {'Telefon':<15} | {'Durum':<15} | {'Skor'}")
        print("-" * 85)
        
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            sonuclar = list(executor.map(self.veri_dogrula, firma_listesi))
            
        for s in sonuclar:
            print(f"{s[0]:<25} | {s[1]:<25} | {s[2]:<15} | {s[3]:<15} | {s[4]}")
            
        end_time = time.time()
        print("-" * 85)
        print(f"[✓] 10 firma toplam {end_time - start_time:.2f} saniyede işlendi.")

if __name__ == "__main__":
    test_firmalari = [
        "Aselsan", "Turkcell", "Eti Gıda", "Arçelik", "Tusaş",
        "Miteyna Teknoloji", "Socar Türkiye", "Botaş", "Hayat Kimya", "Koleksiyon Mobilya"
    ]
    
    otomasyon = FirmaOtomasyonu(max_threads=5)
    otomasyon.calistir(test_firmalari)
