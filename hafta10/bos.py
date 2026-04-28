import tkinter as tk

def secimi_goster():
    secilen = secim_var.get()
    
    if secilen:
        mesaj_label.config(text="Seçtiğiniz: " + secilen)
    else:
        mesaj_label.config(text="Hiçbir seçim yapmadınız.")

pencere = tk.Tk()
pencere.title("Seçim Ekranı")
pencere.geometry("400x300")

# Soru etiketi
soru_label = tk.Label(pencere, text="En Sevdiğiniz Hobiyi Seçiniz:", font=("Arial", 14))
soru_label.pack(pady=15)

# Tüm Radiobuttonların ortak kullanacağı tek değişken
secim_var = tk.StringVar()
secim_var.set("") # Başlangıçta hiçbiri seçili olmasın

# Yuvarlak Seçenek Kutuları (Radiobutton)
rb_sinema = tk.Radiobutton(pencere, text="Sinema", variable=secim_var, value="Sinema", font=("Arial", 12))
rb_sinema.pack(anchor=tk.W, padx=140)

rb_televizyon = tk.Radiobutton(pencere, text="Televizyon", variable=secim_var, value="Televizyon", font=("Arial", 12))
rb_televizyon.pack(anchor=tk.W, padx=140)

rb_tiyatro = tk.Radiobutton(pencere, text="Tiyatro", variable=secim_var, value="Tiyatro", font=("Arial", 12))
rb_tiyatro.pack(anchor=tk.W, padx=140)

# Buton
buton = tk.Button(pencere, text="Seçimi Göster", font=("Arial", 14), command=secimi_goster)
buton.pack(pady=20)

# Sonuç etiketi
mesaj_label = tk.Label(pencere, text="", font=("Arial", 12), fg="blue")
mesaj_label.pack(pady=10)

pencere.mainloop()
