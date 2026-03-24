import numpy as np
import os

def matris_islem(input_dosyasi, output_dosyasi):
    try:
        # 1. Matrisi dosyadan oku
        # Dosyada sayıların boşlukla ayrıldığını varsayıyoruz
        if not os.path.exists(input_dosyasi):
            print(f"Hata: '{input_dosyasi}' dosyası bulunamadı.")
            return

        matris = np.loadtxt(input_dosyasi)
        
        # Tek satırlık bir matris gelirse boyutunu ayarla
        if len(matris.shape) == 1:
            matris = matris.reshape(1, -1)

        satir_sayisi, sutun_sayisi = matris.shape
        print(f"Okunan Matris ({satir_sayisi}x{sutun_sayisi}):")
        print(matris)

        # 2. Kare matris mi kontrol et
        if satir_sayisi != sutun_sayisi:
            print("UYARI: Bu bir kare matris değildir! Determinant hesaplanamaz.")
            return

        # 3. Determinant hesapla
        determinant = np.linalg.det(matris)
        
        # Sonucu yuvarlayalım (hassasiyet hatalarını önlemek için)
        determinant = round(determinant, 4)
        
        print(f"Determinant hesaplandı: {determinant}")

        # 4. Sonucu yeni dosyaya yazdır
        with open(output_dosyasi, 'w', encoding='utf-8') as f:
            f.write(f"Matris Boyutu: {satir_sayisi}x{sutun_sayisi}\n")
            f.write(f"Matris:\n{matris}\n")
            f.write(f"Determinant Değeri: {determinant}\n")
        
        print(f"Sonuç başarıyla '{output_dosyasi}' dosyasına kaydedildi.")

    except Exception as e:
        print(f"Bir hata oluştu: {e}")

# --- Kullanım ---
# 'matris.txt' adında bir dosyanız olduğunu varsayalım.
# İçeriği şöyle olabilir:
# 1 2
# 3 4

input_file = "matris.txt"
output_file = "sonuc.txt"

# Test için örnek bir dosya oluşturalım (Eğer yoksa)


matris_islem(input_file, output_file)