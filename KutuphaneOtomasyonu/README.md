# 📚 Kütüphane Otomasyon Sistemi

Bu proje, Python (Flask) ve Vanilla JavaScript kullanılarak geliştirilmiş, modern ve kapsamlı bir Kütüphane Yönetim Sistemidir. Kitapların, üyelerin ve ödünç alma/iade işlemlerinin takip edilmesini sağlayan ilişkisel bir SQLite veritabanı altyapısına sahiptir.

## 🚀 Projenin Temel Özellikleri

### 1. 📖 Kitap Yönetimi
- **Kitap Ekleme/Düzenleme/Silme:** Başlık, yazar, basım yılı, tür, ISBN gibi bilgileriyle sisteme kitap kaydedebilirsiniz.
- **OpenLibrary API Entegrasyonu:** ISBN numarasını girerek kitabın bilgilerini internet üzerinden otomatik çekebilirsiniz. Ayrıca "Kitap Ara" kısmından isim veya yazarla arama yapıp, sonuçları kapak fotoğraflarıyla birlikte görebilir ve tek tıkla sisteme aktarabilirsiniz.
- **Dinamik Listeleme ve Arama:** Tablolar üzerinden anlık filtreleme, arama ve sıralama yapılabilir.

### 2. 👥 Üye Yönetimi
- Sisteme kütüphane üyelerini (Ad Soyad, Telefon, E-posta bilgileri ile) ekleyebilir, güncelleyebilir ve silebilirsiniz.
- **Güvenlik ve Validasyon:** Aynı telefon numarası veya e-posta adresiyle birden fazla kayıt oluşturulması engellenmiştir. Telefon numarası formatı kontrol edilmektedir (örn: `05XX XXX XX XX`).

### 3. 🔄 Ödünç Verme ve İade Sistemi (Transactions)
- Sisteme kayıtlı kitapları, yine sisteme kayıtlı olan üyelere ödünç verebilirsiniz.
- Kitapların durumu "Müsait" veya "Ödünçte" olarak anlık güncellenir.

### 4. 🕰 Geçmiş Takibi (History)
- Yapılan tüm ödünç alma ve iade etme işlemleri saniye saniye veritabanına kaydedilir.
- **Kitap Geçmişi:** Bir kitabın daha önce hangi tarihlerde kimler tarafından alınıp teslim edildiğini görebilirsiniz.
- **Üye Geçmişi:** Bir üyenin kütüphaneden geçmişte hangi kitapları aldığına ve halihazırda elinde hangi kitapların olduğuna dair detaylı liste alabilirsiniz.

---

## 🛠️ Kullanılan Teknolojiler

- **Backend (Sunucu):** Python, Flask
- **Veritabanı:** SQLite (İlişkisel Veritabanı Mimarisi)
- **Frontend (Arayüz):** HTML5, CSS3, Vanilla JavaScript, Fetch API
- **Harici API:** OpenLibrary (Kitap kapağı ve detaylarını otomatik çekmek için)

---

## 🗄️ Veritabanı Mimarisi (library.db)

Sistem 3 ana tablodan oluşur:

1. **`books` (Kitaplar):** `id`, `title`, `author`, `year`, `isbn`, `genre`, `cover`, `status`
2. **`members` (Üyeler):** `id`, `full_name`, `phone`, `email`, `join_date`
3. **`transactions` (İşlemler):** `id`, `book_id`, `member_id`, `borrow_date`, `return_date`, `status`

*Not: Eğer eski sürümdeki `database.json` dosyası mevcutsa, sistem ilk açılışta içindeki verileri otomatik olarak SQLite'a göç ettirir (Migration) ve veri kaybını önler.*

---

## 📂 Proje Dosyası Yapısı

- `app.py`: Backend iş mantığının, veritabanı oluşturma işlemlerinin ve REST API endpoint'lerinin bulunduğu ana Flask dosyası.
- `kutuphane.html`: Tüm arayüz kodlarının, CSS stillerinin ve Frontend JavaScript mantığının (App sınıfı) barındırıldığı dosya.
- `library.db`: Çalışma zamanında (runtime) otomatik olarak oluşturulan ve tüm verilerin tutulduğu SQLite veritabanı dosyası.

---

## ⚙️ Kurulum ve Çalıştırma

**1. Gerekli kütüphaneyi yükleyin:**
Eğer bilgisayarınızda Flask yüklü değilse, terminale aşağıdaki komutu girin:
```bash
pip install flask
```

**2. Uygulamayı başlatın:**
Aynı dizinde terminal (cmd/powershell) üzerinden şu komutu çalıştırın:
```bash
python app.py
```

**3. Tarayıcıda açın:**
Sunucu çalıştıktan sonra tarayıcınızın adres çubuğuna giderek arayüze ulaşabilirsiniz:
```text
http://127.0.0.1:5000/
```
