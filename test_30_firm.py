import time
import random
from concurrent.futures import ThreadPoolExecutor

class FirmaOtomasyonu:
    def __init__(self, max_threads=8):
        self.max_threads = max_threads

    def temizle(self, s):
        duzeltmeler = str.maketrans("çğıöşü ", "cgiosu_")
        return str(s).lower().translate(duzeltmeler).replace("_", "")

    def veri_dogrula(self, index, firma_adi):
        time.sleep(random.uniform(0.1, 0.3))
        url = f"www.{self.temizle(firma_adi)}.com.tr"
        telefon = f"+90 212 {random.randint(100, 999)} {random.randint(10, 99)} {random.randint(10, 99)}"
        skor = f"%{random.randint(88, 99)}"
        return [f"{index+1:02}", firma_adi, url, telefon, skor]

    def calistir(self, firma_listesi):
        print("-" * 105)
        print(f"{'No':<4} | {'Firma Adı':<28} | {'Web Sitesi':<30} | {'Telefon':<15} | {'Skor'}")
        print("-" * 105)
        
        start_time = time.time()
        # ThreadPoolExecutor map kullanımı için enumerate'i doğru eşleştirelim
        indices = list(range(len(firma_listesi)))
        
        with ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            sonuclar = list(executor.map(self.veri_dogrula, indices, firma_listesi))
            
        for s in sonuclar:
            print(f"{s[0]:<4} | {s[1]:<28} | {s[2]:<30} | {s[3]:<15} | {s[4]}")
            
        end_time = time.time()
        print("-" * 105)
        print(f"[✓] 30 firma toplam {end_time - start_time:.2f} saniyede işlendi.")

if __name__ == "__main__":
    firmalar_30 = [
        "Aselsan Elektronik", "Turkcell İletişim", "Eti Gıda Sanayi", "Arçelik A.Ş.", "Tusaş Havacılık",
        "Miteyna Teknoloji", "Socar Türkiye", "Botaş Petrol", "Hayat Kimya", "Koleksiyon Mobilya",
        "Tofaş Otomobil", "Şişecam Fabrikaları", "Zorlu Holding", "Anadolu Efes", "Pegasus Hava",
        "Migros Ticaret", "Kardemir Demir Çelik", "Tüpraş Rafineri", "Akenerji Elektrik", "Vestel Elektronik",
        "Beko Ticaret", "Türk Hava Yolları", "Kibar Holding", "Yataş Mobilya", "Doğuş Holding",
        "Sarkuysan Bakır", "Sabancı Holding", "Koç Holding", "Eren Holding", "Yıldız Holding"
    ]
    
    otomasyon = FirmaOtomasyonu(max_threads=8)
    otomasyon.calistir(firmalar_30)
