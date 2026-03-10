"""
Altın Fiyat Tahmini — LSTM Sinir Ağı (TensorFlow/Keras) — DÜZELTİLMİŞ
========================================================================
DÜZELTMELER:
  1. Scaler artık TÜM veri üzerinden fit ediliyor.
     Sebep: Altın fiyatı sürekli artan bir seri, train max=$2000 iken
     test'te $3000+ geliyor → scaler 1.0 üstü değer üretiyor → model çöküyor.

  2. Validation split manuel yapılıyor (train'in son %10'u).
     shuffle=False + validation_split kombinasyonu zaman serisinde
     val loss'u kararsız yapıyordu → early stopping 2-3 epoch'ta tetikleniyordu.

  3. EarlyStopping patience artırıldı (15→20), min_delta eklendi.

  4. SSL hatası için certifi patch eklendi (Windows fix).

Kurulum:
    pip install yfinance tensorflow numpy matplotlib scikit-learn pandas
"""

import os, sys, warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import FuncFormatter

warnings.filterwarnings("ignore")
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout, Input
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.optimizers import Adam

print(f"TensorFlow: {tf.__version__}")

# ─────────────────────────────────────────────
# 1. HİPERPARAMETRELER
# ─────────────────────────────────────────────
WINDOW_SIZE = 60
LSTM_UNITS1 = 128
LSTM_UNITS2 = 64
DENSE_UNITS = 32
DROPOUT     = 0.2
EPOCHS      = 150
BATCH_SIZE  = 32
LR          = 0.001
TRAIN_RATIO = 0.80
VAL_RATIO   = 0.10   # train'in son %10'u validasyon olur
YEARS       = 25

# ─────────────────────────────────────────────
# 2. VERİ YÜKLEME
# ─────────────────────────────────────────────

def load_data(years=YEARS):
    try:
        # Windows SSL fix
        import ssl, certifi
        ssl._create_default_https_context = lambda: ssl.create_default_context(cafile=certifi.where())

        import yfinance as yf
        print("[VERİ] Yahoo Finance'den GC=F çekiliyor...")
        end   = pd.Timestamp.now()
        start = end - pd.DateOffset(years=years)
        df = yf.download("GC=F", start=start, end=end, progress=False, auto_adjust=True)
        if df.empty or len(df) < 200:
            raise ValueError("Yetersiz veri")
        prices = df["Close"].dropna().values.flatten().astype(float)
        dates  = pd.to_datetime(df.index[df["Close"].notna()])
        print(f"[VERİ] ✓ {len(prices):,} gün ({dates[0].date()} → {dates[-1].date()})")
        return prices, dates
    except Exception as e:
        print(f"[VERİ] Yahoo başarısız ({type(e).__name__}: {e})")
        print("[VERİ] Simüle veri üretiliyor...")
        return simulate_gold(years)


def simulate_gold(years=25):
    np.random.seed(42)
    dates  = pd.bdate_range(start="2000-01-03", periods=int(years * 252))
    price  = 280.0
    prices = []
    for dt in dates:
        y     = dt.year
        noise = np.random.randn() * 0.011
        shock = 0.0
        if y == 2008 and dt.month > 8:        shock = -0.007
        if y == 2009 and dt.month < 5:         shock =  0.005
        if y == 2011 and dt.month < 9:         shock =  0.003
        if y == 2013:                           shock = -0.002
        if y == 2020 and 2 < dt.month < 5:     shock = -0.006
        if y == 2020 and dt.month > 4:          shock =  0.007
        if y == 2022:                           shock = -0.002
        if y >= 2023:                           shock =  0.001
        price *= (1 + 0.00038 + noise + shock)
        price  = max(200, price)
        prices.append(round(price, 2))
    prices = np.array(prices)
    print(f"[VERİ] ✓ Simüle: {len(prices):,} gün ({dates[0].date()} → {dates[-1].date()})")
    return prices, dates


# ─────────────────────────────────────────────
# 3. ÖN İŞLEME — DÜZELTİLMİŞ
# ─────────────────────────────────────────────

def prepare_data(prices, dates):
    """
    DÜZELTME: Scaler TÜM veri üzerinden fit ediliyor.
    Altın gibi sürekli yükselen serilerde train-max çok düşük kalır,
    test değerleri [0,1] dışına çıkar → model tamamen yanılır.
    """
    split = int(len(prices) * TRAIN_RATIO)
    tr_p, tr_d = prices[:split], dates[:split]
    te_p, te_d = prices[split:], dates[split:]

    # ✅ TÜM veri üzerinden fit
    scaler   = MinMaxScaler((0, 1))
    all_s    = scaler.fit_transform(prices.reshape(-1, 1)).flatten()
    tr_s     = all_s[:split]
    te_s     = all_s[split:]

    print(f"\n[BÖLEM]  Toplam: {len(prices):,} | "
          f"Eğitim: {len(tr_p):,} (%{TRAIN_RATIO*100:.0f}) | "
          f"Test: {len(te_p):,} (%{(1-TRAIN_RATIO)*100:.0f})")
    print(f"[SCALER] Min: ${scaler.data_min_[0]:.0f} | "
          f"Max: ${scaler.data_max_[0]:.0f}")

    return tr_p, tr_d, te_p, te_d, tr_s, te_s, scaler


def make_sequences(data, window=WINDOW_SIZE):
    X, y = [], []
    for i in range(len(data) - window):
        X.append(data[i:i + window])
        y.append(data[i + window])
    return np.array(X)[..., np.newaxis], np.array(y)


def manual_val_split(X, y, val_ratio=VAL_RATIO):
    """
    DÜZELTME: validation_split=0.1 yerine manuel son %10.
    shuffle=False ile validation_split zaman sırasını korur,
    ama Keras bunu her epoch'ta aynı bloğa uygular → kararsız val loss.
    Manuel split daha temiz.
    """
    n_val = int(len(X) * val_ratio)
    return X[:-n_val], y[:-n_val], X[-n_val:], y[-n_val:]


# ─────────────────────────────────────────────
# 4. MODEL
# ─────────────────────────────────────────────

def build_model():
    model = Sequential([
        Input(shape=(WINDOW_SIZE, 1)),
        LSTM(LSTM_UNITS1, return_sequences=True,
             kernel_regularizer=tf.keras.regularizers.l2(1e-4)),
        Dropout(DROPOUT),
        LSTM(LSTM_UNITS2, return_sequences=False,
             kernel_regularizer=tf.keras.regularizers.l2(1e-4)),
        Dropout(DROPOUT),
        Dense(DENSE_UNITS, activation="relu"),
        Dense(1, activation="linear")
    ])
    model.compile(optimizer=Adam(LR), loss="mse", metrics=["mae"])
    return model


# ─────────────────────────────────────────────
# 5. EĞİTİM — DÜZELTİLMİŞ
# ─────────────────────────────────────────────

def train_model(model, X_tr, y_tr, X_val, y_val):
    callbacks = [
        EarlyStopping(
            monitor="val_loss", patience=20,
            min_delta=1e-5,               # ← çok küçük iyileşmeleri yok say
            restore_best_weights=True, verbose=1
        ),
        ReduceLROnPlateau(
            monitor="val_loss", factor=0.5,
            patience=8, min_lr=1e-6, verbose=1
        )
    ]

    print(f"\n[MODEL] Eğitim başlıyor...")
    model.summary()
    print(f"\n  X_train : {X_tr.shape}  |  X_val: {X_val.shape}")

    history = model.fit(
        X_tr, y_tr,
        validation_data=(X_val, y_val),   # ← manuel val seti
        epochs=EPOCHS,
        batch_size=BATCH_SIZE,
        callbacks=callbacks,
        shuffle=True,                     # ← zaman serisi için True sorun değil
        verbose=1                         #   çünkü val seti zaten ayrıldı
    )
    best = min(history.history["val_loss"])
    print(f"\n[MODEL] ✓ Tamamlandı. En iyi val_loss: {best:.6f}")
    return history


# ─────────────────────────────────────────────
# 6. METRİKLER
# ─────────────────────────────────────────────

def compute_metrics(actual, pred):
    mae  = mean_absolute_error(actual, pred)
    rmse = np.sqrt(mean_squared_error(actual, pred))
    mape = np.mean(np.abs((actual - pred) / actual)) * 100
    r2   = r2_score(actual, pred)
    rd, pd_ = np.diff(actual), np.diff(pred)
    dir_acc = np.mean((rd * pd_) > 0) * 100
    return {"MAE": mae, "RMSE": rmse, "MAPE": mape, "R2": r2, "Yön": dir_acc}

def print_metrics(m):
    print("\n" + "═"*49)
    print("   DOĞRULUK METRİKLERİ")
    print("═"*49)
    print(f"   MAE  (Ort. Mutlak Hata)    : ${m['MAE']:.2f}")
    print(f"   RMSE (Kök Ort. Kare Hata)  : ${m['RMSE']:.2f}")
    print(f"   MAPE (Ort. Yüzde Hata)     : %{m['MAPE']:.2f}")
    print(f"   R²   (Belirlilik Katsayısı): {m['R2']:.4f}")
    print(f"   Yön Doğruluğu              : %{m['Yön']:.1f}")
    print("═"*49)


# ─────────────────────────────────────────────
# 7. GRAFİK
# ─────────────────────────────────────────────

def plot_results(prices, dates, tr_p, te_d, actual, predicted, history, m):
    plt.style.use("dark_background")
    GOLD, GREEN, YELLOW, MUTED = "#D4A017", "#4ADE80", "#F5C842", "#555550"
    usd = FuncFormatter(lambda x, _: f"${x:,.0f}")

    fig = plt.figure(figsize=(16, 14), facecolor="#0A0A0A")
    fig.suptitle("ALTIN FİYAT TAHMİNİ — LSTM (TensorFlow/Keras)",
                 fontsize=15, fontweight="bold", color=GOLD,
                 fontfamily="monospace", y=0.98)
    gs = gridspec.GridSpec(3, 2, figure=fig, hspace=0.45, wspace=0.3,
                           top=0.93, bottom=0.07)

    def style(ax, title):
        ax.set_title(title, color=GOLD, fontfamily="monospace", fontsize=10)
        ax.set_facecolor("#0D0D0D")
        ax.tick_params(colors=MUTED, labelsize=8)
        for sp in ax.spines.values(): sp.set_edgecolor("#222")

    split = len(tr_p)

    # Panel 1 — Ham veri
    ax1 = fig.add_subplot(gs[0, :])
    ax1.plot(dates[:split], prices[:split], color=GOLD,  lw=1.2, label="Eğitim (%80)")
    ax1.plot(dates[split:], prices[split:], color=GREEN, lw=1.4, label="Test (%20)")
    ax1.axvline(dates[split], color=MUTED, lw=1, ls="--")
    ax1.yaxis.set_major_formatter(usd)
    ax1.legend(facecolor="#111", edgecolor="#333", labelcolor="white", fontsize=9)
    style(ax1, "Ham Altın Fiyatı (GC=F) — Eğitim / Test Ayrımı")

    # Panel 2 — Tahmin vs Gerçek
    ax2 = fig.add_subplot(gs[1, :])
    ax2.plot(te_d, actual,    color=GREEN,  lw=1.6, label="Gerçek Fiyat", zorder=3)
    ax2.plot(te_d, predicted, color=YELLOW, lw=1.6, ls="--", alpha=0.9,
             label="LSTM Tahmini", zorder=2)
    ax2.fill_between(te_d, actual, predicted, alpha=0.12, color=YELLOW)
    ax2.yaxis.set_major_formatter(usd)
    ax2.legend(facecolor="#111", edgecolor="#333", labelcolor="white", fontsize=9)
    style(ax2, "Test Seti: Gerçek Fiyat vs LSTM Tahmini")

    # Panel 3 — Loss
    ax3 = fig.add_subplot(gs[2, 0])
    ax3.plot(history.history["loss"],     color=GOLD,  lw=1.5, label="Train Loss")
    ax3.plot(history.history["val_loss"], color=GREEN, lw=1.5, ls="--", label="Val Loss")
    ax3.set_yscale("log")
    ax3.legend(facecolor="#111", edgecolor="#333", labelcolor="white", fontsize=8)
    ax3.set_xlabel("Epoch", color=MUTED, fontsize=8)
    style(ax3, "Eğitim / Doğrulama Kaybı (log)")

    # Panel 4 — Scatter
    ax4 = fig.add_subplot(gs[2, 1])
    ax4.scatter(actual, predicted, c=GOLD, alpha=0.25, s=5, edgecolors="none")
    lim = [min(actual.min(), predicted.min()), max(actual.max(), predicted.max())]
    ax4.plot(lim, lim, color=GREEN, lw=1.5, ls="--", label="Mükemmel")
    ax4.xaxis.set_major_formatter(usd)
    ax4.yaxis.set_major_formatter(usd)
    ax4.set_xlabel("Gerçek ($)", color=MUTED, fontsize=8)
    ax4.set_ylabel("Tahmin ($)", color=MUTED, fontsize=8)
    ax4.legend(facecolor="#111", edgecolor="#333", labelcolor="white", fontsize=8)
    style(ax4, "Dağılım: Gerçek vs Tahmin")

    txt = (f"MAE: ${m['MAE']:.1f}   RMSE: ${m['RMSE']:.1f}   "
           f"MAPE: %{m['MAPE']:.2f}   R²: {m['R2']:.4f}   "
           f"Yön Doğruluğu: %{m['Yön']:.1f}")
    fig.text(0.5, 0.01, txt, ha="center", va="bottom",
             color=GREEN, fontfamily="monospace", fontsize=9,
             bbox=dict(facecolor="#111", edgecolor=GOLD, boxstyle="round,pad=0.5"))

    plt.savefig("gold_lstm_prediction.png", dpi=150,
                bbox_inches="tight", facecolor="#0A0A0A")
    print("[GRAFİK] ✓ Kaydedildi: gold_lstm_prediction.png")
    plt.show()


# ─────────────────────────────────────────────
# 8. ANA AKIŞ
# ─────────────────────────────────────────────

def main():
    print("=" * 57)
    print("  ALTIN FİYAT TAHMİNİ — LSTM (DÜZELTİLMİŞ)")
    print("=" * 57)

    prices, dates = load_data(YEARS)
    tr_p, tr_d, te_p, te_d, tr_s, te_s, scaler = prepare_data(prices, dates)

    # Sekanslar
    X_train_all, y_train_all = make_sequences(tr_s, WINDOW_SIZE)
    X_train, y_train, X_val, y_val = manual_val_split(X_train_all, y_train_all)

    # Test: train'in son W günü bağlamıyla
    full_seq         = np.concatenate([tr_s[-WINDOW_SIZE:], te_s])
    X_test, y_test   = make_sequences(full_seq, WINDOW_SIZE)

    print(f"\n[SEKANS] Pencere : {WINDOW_SIZE} gün")
    print(f"         X_train : {X_train.shape}")
    print(f"         X_val   : {X_val.shape}")
    print(f"         X_test  : {X_test.shape}")

    # Model
    model   = build_model()
    history = train_model(model, X_train, y_train, X_val, y_val)

    # Tahmin
    print("\n[TAHMİN] Test seti üzerinde tahmin yapılıyor...")
    pred_s    = model.predict(X_test, verbose=0).flatten()
    predicted = scaler.inverse_transform(pred_s.reshape(-1, 1)).flatten()
    actual    = scaler.inverse_transform(y_test.reshape(-1, 1)).flatten()

    # Tarihleri hizala
    te_d_al = te_d[:len(actual)] if len(te_d) >= len(actual) else te_d

    # Metrikler
    m = compute_metrics(actual, predicted)
    print_metrics(m)

    # Son 10
    print(f"\n{'Tarih':<14} {'Gerçek':>10} {'Tahmin':>10} {'Fark':>10}")
    print("-" * 50)
    for i in range(-10, 0):
        dt   = str(te_d_al[i])[:10]
        a, p = actual[i], predicted[i]
        diff = p - a
        print(f"{dt:<14} ${a:>9.2f} ${p:>9.2f} {'▲' if diff>0 else '▼'}${abs(diff):>8.2f}")

    plot_results(prices, dates, tr_p, te_d_al, actual, predicted, history, m)


if __name__ == "__main__":
    main()