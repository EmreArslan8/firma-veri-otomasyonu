import pandas as pd
import time
import random
from concurrent.futures import ThreadPoolExecutor

class FirmaOtomasyonu:
    def __init__(self, max_threads=5):
        self.max_threads = max_threads

    def veri_dogrula(self, firma_adi):
        """
        Firma bilgilerini bulma ve doğrulama simülasyonu.
        Gerçek uygulamada burada requests ve BeautifulSoup kullanılır.
        """
        # İşlem süresi simülasyonu (0.5 - 1.5 saniye)
        time.sleep(random.uniform(0.5, 1.5))
        
        # Domain oluşturma mantığı
        tr_chars = str.maketrans("çğıöşü ", "cgiosu_")
        clean_name = firma_adi.lower().translate(tr_chars).replace("_", "")
        url = f"www.{clean_name}.com.tr"
        
        # Rastgele telefon ve başarı durumu
        telefon = f"+90 212 {random.randint(100, 999)} {random.randint(10, 99)} {random.randint(10, 99)}"
        durum = "Başarılı" if random.random() > 0.1 else "Manuel Kontrol"
        
        return {
            "Firma Adı": firma_adi,
            "Web Sitesi": url,
            "Telefon": telefon,
            "Durum": durum,
            "Doğruluk Skoru": f"%{random.randint(85, 99)}"
        }

    def calistir(self, firma_listesi):
        print(f"[*] {len(firma_listesi)} firma işleniyor (Threads: {self.max_threads})...")
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            sonuclar = list(executor.map(self.veri_dogrula, firma_listesi))
            
        end_time = time.time()
        print(f"[✓] İşlem {end_time - start_time:.2f} saniyede tamamlandı.\n")
        return pd.DataFrame(sonuclar)

if __name__ == "__main__":
    test_firmalari = [
        "Aselsan", "Turkcell", "Eti Gıda", "Arçelik", "Tusaş",
        "Miteyna Teknoloji", "Socar Türkiye", "Botaş", "Hayat Kimya", "Koleksiyon Mobilya"
    ]
    
    otomasyon = FirmaOtomasyonu(max_threads=5)
    df_sonuc = otomasyon.calistir(test_firmalari)
    
    # Sonuçları ekrana yazdır
    print(df_sonuc.to_string(index=False))
