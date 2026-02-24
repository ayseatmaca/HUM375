from pathlib import Path

import matplotlib.pyplot as plt


def verileri_oku(dosya_yolu: Path) -> list[float]:
	veriler = []

	with dosya_yolu.open("r", encoding="utf-8") as dosya:
		for satir_no, satir in enumerate(dosya, start=1):
			temiz_satir = satir.strip()

			if not temiz_satir:
				continue

			try:
				veriler.append(float(temiz_satir))
			except ValueError:
				print(f"Uyarı: {satir_no}. satır sayı değil, atlandı -> {temiz_satir}")

	return veriler


def grafigi_ciz(veriler: list[float]) -> None:
	if not veriler:
		print("Grafik çizilecek veri bulunamadı.")
		return

	x_degerleri = list(range(1, len(veriler) + 1))

	plt.figure(figsize=(10, 5))
	plt.stem(x_degerleri, veriler, linefmt="blue", markerfmt="bo", basefmt=" ")
	plt.axhline(0, color="gray", linewidth=0.5, linestyle="--")
	plt.title("Veri Stem Grafiği")
	plt.xlabel("Ay Sayısı")
	plt.ylabel("Gelir(*1000 TL)")
	plt.xticks(x_degerleri)
	plt.grid(True, linestyle="--", alpha=0.5)
	plt.tight_layout()
	plt.show()


if __name__ == "__main__":
	dosya = Path(__file__).with_name("ad.txt")

	if not dosya.exists():
		print(f"Dosya bulunamadı: {dosya}")
	else:
		veri_listesi = verileri_oku(dosya)
		grafigi_ciz(veri_listesi)
