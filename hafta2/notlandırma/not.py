def harf_notuna_cevir(not_degeri):
    """Sayısal notu harf notuna çevirir (A, B, C, D, F sistemi)."""
    if not_degeri >= 85:
        return "A"
    elif not_degeri >= 70:
        return "B"
    elif not_degeri >= 55:
        return "C"
    elif not_degeri >= 40:
        return "D"
    else:
        return "F"


def notlari_goster(ogrenciler_dict):
    """Öğrenci not bilgilerini ekrana yazdırır (Vize, Final, Genel Not, Harf Notu)."""
    print("\n" + "=" * 80)
    print("ÖĞRENCI NOT VE HARF NOTU LİSTESİ")
    print("=" * 80)
    print(f"{'Ad':25} | {'Vize':8} | {'Final':8} | {'Genel Not':10} | {'Harf':6}")
    print("-" * 80)
    
    for ad, notlar in ogrenciler_dict.items():
        vize = notlar['vize']
        final = notlar['final']
        genel_not = ortalamayi_hesapla(vize, final)
        harf_notu = harf_notuna_cevir(genel_not)
        print(f"{ad:25} | {vize:8.2f} | {final:8.2f} | {genel_not:10.2f} | {harf_notu:6}")
    
    print("=" * 80 + "\n")


def notlari_dosyadan_oku(dosya_yolu):
    """Excel veya CSV dosyasından notları okur."""
    notlar = {}
    try:
        with open(dosya_yolu, "r", encoding="utf-8") as dosya:
            for satir in dosya:
                temiz_satir = satir.strip()
                if temiz_satir and ":" in temiz_satir:
                    ogrenci, not_str = temiz_satir.split(":")
                    ogrenci = ogrenci.strip()
                    not_degeri = float(not_str.strip())
                    notlar[ogrenci] = not_degeri
        return notlar
    except FileNotFoundError:
        print(f"Hata: {dosya_yolu} dosyası bulunamadı!")
        return None


def ortalamayi_hesapla(vize, final):
    """Vize ve Final notunun ortalamasını hesaplar."""
    return (vize + final) / 2


def en_yuksek_en_dusuk_bul(notlar_dict):
    """En yüksek ve en düşük notu bulur."""
    if not notlar_dict:
        return None, None
    
    en_yuksek = max(notlar_dict.values())
    en_dusuk = min(notlar_dict.values())
    return en_yuksek, en_dusuk


if __name__ == "__main__":
    ogrenciler = {}
    
    print("\n" + "🎓 " * 15)
    print("ÖĞRENCI VİZE - FİNAL - HARF NOTU SİSTEMİ")
    print("🎓 " * 15)
    print("\nGenel Not = (Vize + Final) / 2\n")
    print("Notları girmeye başlayın. Çıkmak için 'çıkış' yazıp Enter'e basın.\n")
    
    while True:
        ad = input("Öğrenci adı: ").strip()
        
        if ad.lower() == "çıkış":
            break
        
        if not ad:
            print("Lütfen geçerli bir ad girin!\n")
            continue
        
        try:
            vize = float(input(f"{ad} için Vize notunu giriniz (0-100): "))
            
            if not (0 <= vize <= 100):
                print("Vize notu 0-100 arasında olmalıdır!\n")
                continue
            
            final = float(input(f"{ad} için Final notunu giriniz (0-100): "))
            
            if not (0 <= final <= 100):
                print("Final notu 0-100 arasında olmalıdır!\n")
                continue
            
            ogrenciler[ad] = {'vize': vize, 'final': final}
            print("✓ Notlar kaydedildi.\n")
        
        except ValueError:
            print("Hata: Lütfen sayı girin!\n")
    
    if not ogrenciler:
        print("\nHiç not girilmedi!")
    else:
        # Notları ve harf notlarını göster
        notlari_goster(ogrenciler)
        
        # Sınıf istatistikleri
        genel_notlar = [ortalamayi_hesapla(ogrenciler[ad]['vize'], ogrenciler[ad]['final']) for ad in ogrenciler]
        sinif_ortalaması = sum(genel_notlar) / len(genel_notlar)
        
        print(f"Sınıf Genel Ortalaması: {sinif_ortalaması:.2f}")
        print(f"Sınıf Ortalaması Harf Notu: {harf_notuna_cevir(sinif_ortalaması)}\n")
