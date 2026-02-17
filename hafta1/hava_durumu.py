import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score

# ==========================================
# 1. VERİYİ YÜKLEME VE EKSİK VERİ TAMAMLAMA
# ==========================================
try:
    df = pd.read_csv('hafta1/seattle-weather.csv')
    print("✅ Veri seti yüklendi.")
except:
    print("❌ 'seattle-weather.csv' bulunamadı! Lütfen dosyanın adını kontrol et.")
    exit()

# Eksik veri kontrolü ve tamamlama (Ödev Madde 1)
if df.isnull().values.any():
    df.fillna(df.mean(numeric_only=True), inplace=True)
    df['weather'].fillna(df['weather'].mode()[0], inplace=True)
    print("-> Eksik veriler başarıyla tamamlandı.")
else:
    print("-> Veride eksik parça yok, temiz.")

# ==========================================
# 2. VERİ NORMALİZASYONU (Ödev Madde 2)
# ==========================================
# Özellikleri ve hedefi ayır (tarih tahminde kullanılmaz)
X = df.drop(['date', 'weather'], axis=1)
y = df['weather']

# Min-Max Normalizasyonu (Veriyi 0 ile 1 arasına ölçekler)
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

# Hava durumu isimlerini bilgisayarın anlaması için sayıya çevir
le = LabelEncoder()
y_encoded = le.fit_transform(y)

# ==========================================
# 3. ALGORİTMA SEÇİMİ (Ödev Madde 3)
# ==========================================
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_encoded, test_size=0.2, random_state=42)

print("\n--- TAHMİN ALGORİTMASI SEÇİN ---")
print("1 - Random Forest")
print("2 - SVM (Support Vector Machine)")
print("3 - KNN (K-Nearest Neighbors)")
secim = input("Seçiminiz (1/2/3): ")

if secim == '1':
    model = RandomForestClassifier()
    isim = "Random Forest"
elif secim == '2':
    model = SVC()
    isim = "SVM"
else:
    model = KNeighborsClassifier()
    isim = "KNN"

model.fit(X_train, y_train)
print(f"\nSeçilen {isim} modeli eğitildi.")

# ==========================================
# 4. 10 GÜNLÜK TAHMİN VE KARŞILAŞTIRMA (Ödev Madde 4)
# ==========================================
print(f"\n--- SON 10 GÜN KARŞILAŞTIRMALI TAHMİN SONUÇLARI ({isim}) ---")
print(f"{'Gün':<5} | {'Tahmin Edilen':<15} | {'Gerçek Durum':<15} | {'Sonuç'}")
print("-" * 55)

# Test setinden son 10 günü alıyoruz
son_10_X = X_test[-10:]
son_10_y_gercek = y_test[-10:]

tahminler = model.predict(son_10_X)

# Sayıları tekrar kelimelere (snow, rain, sun vb.) çevir
tahmin_isimler = le.inverse_transform(tahminler)
gercek_isimler = le.inverse_transform(son_10_y_gercek)

# Türkçe çeviri sözlüğü
tr = {'drizzle': 'Çiseliyor', 'rain': 'Yağmurlu', 'sun': 'Güneşli', 'snow': 'Karlı', 'fog': 'Sisli'}

dogru_sayısı = 0
for i in range(10):
    t = tr.get(tahmin_isimler[i], tahmin_isimler[i])
    g = tr.get(gercek_isimler[i], gercek_isimler[i])
    
    check = "✅ DOĞRU" if t == g else "❌ YANLIŞ"
    if t == g: dogru_sayısı += 1
    
    print(f"{i+1:<5} | {t:<15} | {g:<15} | {check}")

print("-" * 55)
print(f"Toplam Başarı: 10 günde {dogru_sayısı} doğru tahmin.")