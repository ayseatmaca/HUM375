import numpy as np
import pandas as pd
from pathlib import Path


def matris_exceldan_oku(dosya_yolu):
    """Excel dosyasından matrisi okur ve NumPy array'e çevirir."""
    try:
        df = pd.read_excel(dosya_yolu, header=None)
        matris = df.to_numpy(dtype=float)
        return matris
    except FileNotFoundError:
        print(f"Hata: Dosya bulunamadı -> {dosya_yolu}")
        return None
    except Exception as e:
        print(f"Hata: Excel dosyası okunurken sorun oluştu -> {e}")
        return None


def matris_yazdir(matris, ad):
    """Matrisi güzel formatla ekrana yazdırır."""
    print(f"\n{ad}:")
    print(matris)


def matris_topla(matris1, matris2):
    """İki matrisi toplar."""
    return matris1 + matris2


def matris_carp(matris1, matris2):
    """İki matrisi çarpar (matris çarpımı)."""
    return np.dot(matris1, matris2)


if __name__ == "__main__":
    # Dosya yolları
    matris1_dosya = Path(__file__).parent / "matris1.xlsx"
    matris2_dosya = Path(__file__).parent / "matris2.xlsx"

    # Matrisler Excel dosyalarından okunuyor
    matris1 = matris_exceldan_oku(matris1_dosya)
    matris2 = matris_exceldan_oku(matris2_dosya)

    if matris1 is None or matris2 is None:
        print("Matrisler okunurken hata oluştu!")
        exit()

    print("=" * 50)
    print("MATRİS İŞLEMLERİ")
    print("=" * 50)

    # Matrisleri göster
    matris_yazdir(matris1, "Matris 1")
    matris_yazdir(matris2, "Matris 2")

    # Toplama işlemi
    toplam = matris_topla(matris1, matris2)
    matris_yazdir(toplam, "Matris 1 + Matris 2 = Toplam")

    # Çarpma işlemi
    carpim = matris_carp(matris1, matris2)
    matris_yazdir(carpim, "Matris 1 × Matris 2 = Çarpım")

    print("\n" + "=" * 50)
