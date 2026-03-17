# 🗺️ Gelişmiş Harita Uygulaması

Python + Flask + Leaflet.js ile yapılmış tam özellikli interaktif harita uygulaması.

## 🚀 Kurulum ve Çalıştırma

```bash
# 1. Gereksinimleri yükle
pip install -r requirements.txt

# 2. Uygulamayı başlat
python app.py

# 3. Tarayıcıda aç
# http://localhost:5000
```

## ✨ Özellikler

### 🖱️ Gezinme
- **Sürükleme**: Sol tık + sürükle ile haritayı gez
- **Zoom**: Fare tekerleği veya +/- tuşları
- **Çift tık**: Belirli noktaya zoom yap

### 📍 İşaretçi Yönetimi
- **Sağ tık** → "İşaretçi Ekle" → Başlık, açıklama ve renk seç
- **Sürükle & Bırak**: İşaretçileri taşı
- **Popup silme**: İşaretçiye tıkla → "Sil" butonu
- **Sidebar silme**: Sol panelden tek tek veya toplu sil
- **Renk seçenekleri**: 8 farklı renk (kırmızı, mavi, yeşil, turuncu, mor, pembe, camgöbeği, beyaz)

### 🗂️ Katman Sistemi (Sağ üst panel)
- **Standart**: OpenStreetMap klasik görünüm
- **Uydu**: ESRI uydu görüntüsü
- **Topografik**: Yükseklik/arazi haritası
- **Karanlık**: Gece modu harita

### 🔍 Arama
- Şehir, adres veya yer adı arama (Nominatim API)
- Enter tuşu veya buton ile arama

### 📡 GPS / Konum
- "Konumum" butonu ile cihaz konumunu bul
- Mavi daire ile gösterim

### 🛤️ Rota (Sağ tık menüsü)
- Başlangıç noktası belirle
- Bitiş noktası belirle
- Kuş uçuşu mesafe hesaplama

### 📏 Mesafe Ölçümü
- "Ölçüm" butonu → Haritaya tıklayarak noktalar ekle
- Gerçek zamanlı toplam mesafe hesabı
- "Ölçümü Bitir" ile temizle

### 🖱️ Sağ Tık Menüsü
- İşaretçi ekle
- Rota başlat / bitir
- Koordinatları panoya kopyala
- Google Street View'de aç

### 💾 Veri Kalıcılığı
- İşaretçiler Flask sunucusunda saklanır
- Sayfa yenilemede kaybolmaz

## 📁 Dosya Yapısı
```
harita_uygulamasi/
├── app.py              # Flask backend
├── requirements.txt    # Python gereksinimleri
├── README.md
└── templates/
    └── index.html      # Tüm frontend kodu
```