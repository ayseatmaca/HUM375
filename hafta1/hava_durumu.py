import pandas as pd

# Veriyi oku (csv dosyasının adını doğru yaz)
df = pd.read_csv('hafta1/seattle-weather.csv')

# 1. Eksik veri kontrolü ve tamamlama
if df.isnull().values.any():
    # Sayısal sütunları ortalama ile doldur
    df.fillna(df.mean(numeric_only=True), inplace=True)
    # Kategorik verileri (weather) en çok tekrar edenle doldur
    df['weather'].fillna(df['weather'].mode()[0], inplace=True)

from sklearn.preprocessing import MinMaxScaler, LabelEncoder

# Özellikleri ve hedef değişkeni ayır
X = df.drop(['date', 'weather'], axis=1) # Tarih ve sonuç sütununu çıkar
y = df['weather'] # Tahmin edilecek sütun

# Min-Max Normalizasyonu
scaler = MinMaxScaler()
X_scaled = scaler.fit_transform(X)

# Hava durumu isimlerini sayıya çevir (Örn: 'sun' -> 0, 'rain' -> 1)
le = LabelEncoder()
y_encoded = le.fit_transform(y)

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier

# Veriyi eğitim ve test olarak böl
X_train, X_test, y_train, y_test = train_test_split(X_scaled, y_encoded, test_size=0.2, random_state=42)

print("Hangi algoritmayı kullanmak istersiniz?")
print("1: Random Forest\n2: SVM\n3: KNN")
secim = input("Seçiminiz (1/2/3): ")

if secim == '1':
    model = RandomForestClassifier()
elif secim == '2':
    model = SVC()
else:
    model = KNeighborsClassifier()

model.fit(X_train, y_train)# Test setindeki son 10 günü alalım
son_10_gun = X_test[-10:]
tahminler = model.predict(son_10_gun)

# Sayıları tekrar kelimelere çevir
sonuclar = le.inverse_transform(tahminler)

print("\nÖnümüzdeki 10 Günlük Hava Tahmini:")
for i, durum in enumerate(sonuclar, 1):
    print(f"Gün {i}: {durum}")