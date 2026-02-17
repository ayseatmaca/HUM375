import cv2
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk, ImageOps
import numpy as np

class KenarUygulaması:
    def __init__(self, pencere):
        self.pencere = pencere
        self.pencere.title("EdgeVision AI")
        self.pencere.geometry("980x700")
        self.pencere.configure(bg="#F1F8E9")

        self.threshold_var = tk.DoubleVar(value=100.0)
        self.threshold_text = tk.StringVar(value="100")
        self.resim_bgr = None

        # Üst Başlık (AppBar)
        self.baslik = tk.Frame(pencere, bg="#F1F8E9")
        self.baslik.pack(fill="x", padx=20, pady=(16, 8))

        self.baslik_etiket = tk.Label(
            self.baslik,
            text="EdgeVision AI",
            font=("Arial", 16, "bold"),
            fg="#2E7D32",
            bg="#F1F8E9",
        )
        self.baslik_etiket.pack()

        # İçerik Alanı
        self.icerik = tk.Frame(pencere, bg="#F1F8E9")
        self.icerik.pack(expand=True, fill="both", padx=20, pady=8)

        # Yükleme Kartı
        self.kart = tk.Frame(self.icerik, bg="white", highlightbackground="#C8E6C9", highlightthickness=1)
        self.kart.pack(fill="x", pady=(0, 16))

        self.kart_icerik = tk.Frame(self.kart, bg="white")
        self.kart_icerik.pack(padx=16, pady=20)

        self.btn_sec = tk.Button(
            self.kart_icerik,
            text="Resim Seçmek İçin Dokunun",
            command=self.resim_sec,
            padx=20,
            pady=12,
            bg="#4CAF50",
            fg="white",
            activebackground="#43A047",
            activeforeground="white",
            borderwidth=0,
            font=("Arial", 10, "bold"),
        )
        self.btn_sec.pack()

        # Resimlerin Görüntüleneceği Alan
        self.resim_paneli = tk.Frame(self.icerik, bg="#F1F8E9")
        self.resim_paneli.pack(expand=True, fill="both")

        self.lbl_orjinal = tk.Label(
            self.resim_paneli,
            text="ORİJİNAL RESİM",
            font=("Arial", 9, "bold"),
            fg="#2E7D32",
            bg="#F1F8E9",
        )
        self.lbl_orjinal.grid(row=0, column=0, sticky="w", padx=6, pady=(0, 6))

        self.lbl_kenar = tk.Label(
            self.resim_paneli,
            text="KENAR ALGILANMIŞ (CANNY)",
            font=("Arial", 9, "bold"),
            fg="#2E7D32",
            bg="#F1F8E9",
        )
        self.lbl_kenar.grid(row=0, column=1, sticky="w", padx=6, pady=(0, 6))

        self.panel_size = (440, 260)

        self.panel_frame_orjinal = tk.Frame(self.resim_paneli, bg="white", width=self.panel_size[0], height=self.panel_size[1], bd=1, relief="solid")
        self.panel_frame_orjinal.grid(row=1, column=0, padx=6, pady=(0, 16), sticky="nsew")
        self.panel_frame_orjinal.grid_propagate(False)

        self.panel_frame_kenar = tk.Frame(self.resim_paneli, bg="white", width=self.panel_size[0], height=self.panel_size[1], bd=1, relief="solid")
        self.panel_frame_kenar.grid(row=1, column=1, padx=6, pady=(0, 16), sticky="nsew")
        self.panel_frame_kenar.grid_propagate(False)

        self.panel_orjinal = tk.Label(self.panel_frame_orjinal, bg="white")
        self.panel_orjinal.place(relx=0.5, rely=0.5, anchor="center")

        self.panel_kenar = tk.Label(self.panel_frame_kenar, bg="white")
        self.panel_kenar.place(relx=0.5, rely=0.5, anchor="center")

        self.resim_paneli.grid_columnconfigure(0, weight=1)
        self.resim_paneli.grid_columnconfigure(1, weight=1)

        # Kontrol Paneli
        self.kontrol = tk.Frame(self.icerik, bg="white", highlightbackground="#E0E0E0", highlightthickness=1)
        self.kontrol.pack(fill="x", pady=(0, 16))

        self.kontrol_icerik = tk.Frame(self.kontrol, bg="white")
        self.kontrol_icerik.pack(fill="x", padx=16, pady=16)

        self.kontrol_baslik = tk.Label(
            self.kontrol_icerik,
            text="Hassasiyet Eşiği",
            font=("Arial", 10, "bold"),
            fg="#212121",
            bg="white",
        )
        self.kontrol_baslik.pack(side="left")

        self.kontrol_deger = tk.Label(
            self.kontrol_icerik,
            textvariable=self.threshold_text,
            font=("Arial", 10, "bold"),
            fg="#2E7D32",
            bg="white",
        )
        self.kontrol_deger.pack(side="right")

        self.kontrol_slider = tk.Scale(
            self.kontrol,
            from_=0,
            to=255,
            orient="horizontal",
            variable=self.threshold_var,
            bg="white",
            highlightthickness=0,
            troughcolor="#E8F5E9",
            activebackground="#4CAF50",
            command=self.esik_degisti,
        )
        self.kontrol_slider.pack(fill="x", padx=16, pady=(0, 16))

        # Alt Bar
        self.alt_bar = tk.Frame(pencere, bg="white", height=56)
        self.alt_bar.pack(fill="x", side="bottom")

        self.btn_gecmis = tk.Button(self.alt_bar, text="⟲", bg="white", fg="#9E9E9E", bd=0, font=("Arial", 12))
        self.btn_gecmis.pack(side="left", expand=True)

        self.btn_kamera = tk.Button(
            self.alt_bar,
            text="＋",
            command=self.resim_sec,
            bg="#4CAF50",
            fg="white",
            bd=0,
            font=("Arial", 12, "bold"),
            width=4,
            height=1,
        )
        self.btn_kamera.pack(side="left", expand=True, pady=10)

        self.btn_ayar = tk.Button(self.alt_bar, text="⚙", bg="white", fg="#9E9E9E", bd=0, font=("Arial", 12))
        self.btn_ayar.pack(side="left", expand=True)

    def resim_sec(self):
        # Dosya seçme diyaloğu
        dosya_yolu = filedialog.askopenfilename(filetypes=[("Resim Dosyaları", "*.jpg *.jpeg *.png *.bmp")])
        
        if not dosya_yolu:
            return

        # OpenCV ile resmi oku (Unicode/özel karakter içeren yollar için güvenli)
        self.resim_bgr = self.imread_unicode(dosya_yolu)
        if self.resim_bgr is None:
            messagebox.showerror("Hata", "Resim yüklenemedi!")
            return

        # 1. Orijinal Resmi Hazırla (Görüntüleme için boyutlandır)
        resim_rgb = cv2.cvtColor(self.resim_bgr, cv2.COLOR_BGR2RGB)
        orj_pil = self.boyutlandir(Image.fromarray(resim_rgb), self.panel_size)
        orj_tk = ImageTk.PhotoImage(orj_pil)

        # 2. Canny Kenar Algılama İşlemi
        self.guncelle_kenar()

        # Panelleri güncelle
        self.panel_orjinal.config(image=orj_tk)
        self.panel_orjinal.image = orj_tk
        
        self.panel_kenar.config(image=self.kenar_tk)
        self.panel_kenar.image = self.kenar_tk

    def esik_degisti(self, _=None):
        self.threshold_text.set(str(int(self.threshold_var.get())))
        if self.resim_bgr is not None:
            self.guncelle_kenar()

    def guncelle_kenar(self):
        gri = cv2.cvtColor(self.resim_bgr, cv2.COLOR_BGR2GRAY)
        alt_esik = int(self.threshold_var.get())
        ust_esik = min(255, alt_esik + 100)
        kenarlar = cv2.Canny(gri, alt_esik, ust_esik)

        # Kenar resmini Pillow formatına ve ardından TK formatına çevir
        kenar_pil = self.boyutlandir(Image.fromarray(kenarlar), self.panel_size)
        self.kenar_tk = ImageTk.PhotoImage(kenar_pil)

    def boyutlandir(self, img, maks_boyut):
        # Resimleri alana tam sığacak şekilde orantılı kırpıp büyütür
        return ImageOps.fit(img, maks_boyut, Image.Resampling.LANCZOS)

    def imread_unicode(self, path):
        try:
            data = np.fromfile(path, dtype=np.uint8)
            if data.size == 0:
                return None
            return cv2.imdecode(data, cv2.IMREAD_COLOR)
        except Exception:
            return None

# Uygulamayı başlat
root = tk.Tk()
uygulama = KenarUygulaması(root)
root.mainloop()