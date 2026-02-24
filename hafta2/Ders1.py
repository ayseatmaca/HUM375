import tkinter as tk
from tkinter import messagebox


def islem_sembolunu_guncelle():
	islem_haritasi = {
		"toplama": "+",
		"cikarma": "-",
		"carpma": "×",
		"bolme": "÷",
	}
	islem_label.config(text=islem_haritasi[secilen_islem.get()])


def hesapla():
	try:
		sayi1 = float(girdi1.get())
		sayi2 = float(girdi2.get())
		islem = secilen_islem.get()

		if islem == "toplama":
			sonuc = sayi1 + sayi2
		elif islem == "cikarma":
			sonuc = sayi1 - sayi2
		elif islem == "carpma":
			sonuc = sayi1 * sayi2
		elif islem == "bolme":
			if sayi2 == 0:
				messagebox.showerror("Hata", "Bölen sayı 0 olamaz.")
				return
			sonuc = sayi1 / sayi2
		else:
			messagebox.showerror("Hata", "Geçersiz işlem seçimi.")
			return

		sonuc_var.set(str(sonuc))
	except ValueError:
		messagebox.showerror("Hata", "Lütfen kutulara geçerli sayı girin.")


pencere = tk.Tk()
pencere.title("Kutu Kutu Hesap Makinesi")
pencere.geometry("500x250")
pencere.resizable(False, False)

baslik = tk.Label(pencere, text="Kutu İşlemi = Sonuç", font=("Arial", 14, "bold"))
baslik.pack(pady=10)

cerceve = tk.Frame(pencere)
cerceve.pack(pady=8)

girdi1 = tk.Entry(cerceve, width=10, font=("Arial", 16), justify="center")
girdi1.grid(row=0, column=0, padx=6)

islem_label = tk.Label(cerceve, text="+", font=("Arial", 16, "bold"))
islem_label.grid(row=0, column=1)

girdi2 = tk.Entry(cerceve, width=10, font=("Arial", 16), justify="center")
girdi2.grid(row=0, column=2, padx=6)

esittir = tk.Label(cerceve, text="=", font=("Arial", 16, "bold"))
esittir.grid(row=0, column=3)

sonuc_var = tk.StringVar()
sonuc_kutusu = tk.Entry(
	cerceve,
	width=10,
	font=("Arial", 16),
	justify="center",
	textvariable=sonuc_var,
	state="readonly",
)
sonuc_kutusu.grid(row=0, column=4, padx=6)

islem_cercevesi = tk.LabelFrame(pencere, text="Yapılacak İşlem", padx=12, pady=8)
islem_cercevesi.pack(pady=8)

secilen_islem = tk.StringVar(value="toplama")

toplama_rb = tk.Radiobutton(
	islem_cercevesi,
	text="Toplama",
	variable=secilen_islem,
	value="toplama",
	command=islem_sembolunu_guncelle,
)
toplama_rb.grid(row=0, column=0, padx=8)

cikarma_rb = tk.Radiobutton(
	islem_cercevesi,
	text="Çıkarma",
	variable=secilen_islem,
	value="cikarma",
	command=islem_sembolunu_guncelle,
)
cikarma_rb.grid(row=0, column=1, padx=8)

carpma_rb = tk.Radiobutton(
	islem_cercevesi,
	text="Çarpma",
	variable=secilen_islem,
	value="carpma",
	command=islem_sembolunu_guncelle,
)
carpma_rb.grid(row=0, column=2, padx=8)

bolme_rb = tk.Radiobutton(
	islem_cercevesi,
	text="Bölme",
	variable=secilen_islem,
	value="bolme",
	command=islem_sembolunu_guncelle,
)
bolme_rb.grid(row=0, column=3, padx=8)

buton = tk.Button(pencere, text="Hesapla", font=("Arial", 12, "bold"), command=hesapla)
buton.pack(pady=8)

pencere.mainloop()