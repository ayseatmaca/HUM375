"""
Iris Çiçek Veri Seti — MLP Sinir Ağı Sınıflandırması (TensorFlow/Keras)
=========================================================================
• sklearn'den Iris veri seti yüklenir
• %80 eğitim / %20 test ayrımı (stratified)
• 3 katmanlı MLP: Dense(128) → Dense(64) → Dense(3, softmax)
• Eğitim & doğrulama loss/accuracy grafikleri
• Confusion matrix
• Sınıflandırma raporu (precision, recall, F1)

Kurulum:
    pip install tensorflow scikit-learn numpy matplotlib seaborn pandas
"""

import os, warnings
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
warnings.filterwarnings("ignore")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import MaxNLocator
import seaborn as sns

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import (classification_report, confusion_matrix,
                              accuracy_score)

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Input, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.utils import to_categorical

print(f"TensorFlow: {tf.__version__}")

# ─────────────────────────────────────────────
# 1. HİPERPARAMETRELER
# ─────────────────────────────────────────────
HIDDEN1     = 128
HIDDEN2     = 64
DROPOUT     = 0.3
EPOCHS      = 200
BATCH_SIZE  = 16
LR          = 0.001
TEST_SIZE   = 0.20   # %80 eğitim / %20 test
RANDOM_SEED = 42

CLASS_NAMES = ["Setosa", "Versicolor", "Virginica"]

# ─────────────────────────────────────────────
# 2. VERİ YÜKLEME & ÖN İŞLEME
# ─────────────────────────────────────────────

print("\n[VERİ] Iris veri seti yükleniyor...")
iris = load_iris()
X    = iris.data.astype(np.float32)   # (150, 4)
y    = iris.target                     # 0, 1, 2

print(f"[VERİ] Toplam örnek  : {len(X)}")
print(f"[VERİ] Özellikler    : {iris.feature_names}")
print(f"[VERİ] Sınıflar      : {CLASS_NAMES}")
print(f"[VERİ] Sınıf dağılımı: {dict(zip(CLASS_NAMES, np.bincount(y)))}")

# %80 / %20 stratified split (her sınıftan eşit oranda al)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=TEST_SIZE, random_state=RANDOM_SEED, stratify=y
)
print(f"\n[BÖLEM] Eğitim : {len(X_train)} örnek (%{(1-TEST_SIZE)*100:.0f})")
print(f"[BÖLEM] Test   : {len(X_test)} örnek (%{TEST_SIZE*100:.0f})")

# Standardizasyon — sadece train'den fit
scaler  = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test  = scaler.transform(X_test)

# One-hot encoding (softmax çıktısı için)
y_train_oh = to_categorical(y_train, num_classes=3)
y_test_oh  = to_categorical(y_test,  num_classes=3)

# ─────────────────────────────────────────────
# 3. MODEL
# ─────────────────────────────────────────────

def build_model():
    model = Sequential([
        Input(shape=(4,)),

        Dense(HIDDEN1, activation="relu"),
        BatchNormalization(),
        Dropout(DROPOUT),

        Dense(HIDDEN2, activation="relu"),
        BatchNormalization(),
        Dropout(DROPOUT),

        Dense(32, activation="relu"),

        Dense(3, activation="softmax")   # 3 sınıf
    ])
    model.compile(
        optimizer=Adam(LR),
        loss="categorical_crossentropy",
        metrics=["accuracy"]
    )
    return model

model = build_model()
print("\n[MODEL] Mimari:")
model.summary()

# ─────────────────────────────────────────────
# 4. EĞİTİM
# ─────────────────────────────────────────────

callbacks = [
    EarlyStopping(monitor="val_loss", patience=25,
                  restore_best_weights=True, verbose=1, min_delta=1e-4),
    ReduceLROnPlateau(monitor="val_loss", factor=0.5,
                      patience=10, min_lr=1e-6, verbose=1)
]

print("\n[EĞİTİM] Başlıyor...")
history = model.fit(
    X_train, y_train_oh,
    validation_split=0.15,       # train'in %15'i → validation
    epochs=EPOCHS,
    batch_size=BATCH_SIZE,
    callbacks=callbacks,
    shuffle=True,
    verbose=1
)
best_val = min(history.history["val_loss"])
print(f"\n[EĞİTİM] ✓ Tamamlandı. En iyi val_loss: {best_val:.4f}")

# ─────────────────────────────────────────────
# 5. SONUÇLAR
# ─────────────────────────────────────────────

print("\n[TAHMİN] Test seti değerlendiriliyor...")
y_pred_prob = model.predict(X_test, verbose=0)
y_pred      = np.argmax(y_pred_prob, axis=1)

acc = accuracy_score(y_test, y_pred)
cm  = confusion_matrix(y_test, y_pred)
cr  = classification_report(y_test, y_pred, target_names=CLASS_NAMES)

print("\n" + "═"*55)
print("  TEST SONUÇLARI")
print("═"*55)
print(f"  Genel Doğruluk (Accuracy): %{acc*100:.2f}")
print("═"*55)
print("\n  Sınıflandırma Raporu:\n")
print(cr)

# Confusion matrix detayı
print("  Confusion Matrix:")
print(f"  {'':12}", end="")
for cn in CLASS_NAMES: print(f"{cn:>12}", end="")
print()
for i, row in enumerate(cm):
    print(f"  {CLASS_NAMES[i]:<12}", end="")
    for val in row: print(f"{val:>12}", end="")
    print()

# ─────────────────────────────────────────────
# 6. GRAFİKLER
# ─────────────────────────────────────────────

plt.style.use("dark_background")
GOLD   = "#D4A017"
GREEN  = "#4ADE80"
TEAL   = "#2DD4BF"
RED    = "#F87171"
PURPLE = "#A78BFA"
MUTED  = "#4B5563"

fig = plt.figure(figsize=(18, 12), facecolor="#0A0A0A")
fig.suptitle("IRIS VERİ SETİ — MLP SİNİR AĞI  (TensorFlow/Keras)",
             fontsize=15, fontweight="bold", color=GOLD,
             fontfamily="monospace", y=0.98)

gs = gridspec.GridSpec(2, 3, figure=fig, hspace=0.45, wspace=0.35,
                       top=0.93, bottom=0.07)

def style_ax(ax, title):
    ax.set_title(title, color=GOLD, fontfamily="monospace", fontsize=10, pad=10)
    ax.set_facecolor("#0D0D0D")
    ax.tick_params(colors=MUTED, labelsize=8)
    for sp in ax.spines.values(): sp.set_edgecolor("#222")

# ── Panel 1: Eğitim / Val Loss ─────────────────────────────
ax1 = fig.add_subplot(gs[0, 0])
ep = range(1, len(history.history["loss"]) + 1)
ax1.plot(ep, history.history["loss"],     color=GOLD,  lw=1.8, label="Train Loss")
ax1.plot(ep, history.history["val_loss"], color=TEAL, lw=1.8, ls="--", label="Val Loss")
ax1.legend(facecolor="#111", edgecolor="#333", labelcolor="white", fontsize=8)
ax1.set_xlabel("Epoch", color=MUTED, fontsize=8)
ax1.xaxis.set_major_locator(MaxNLocator(integer=True))
style_ax(ax1, "Eğitim / Doğrulama Kaybı")

# ── Panel 2: Eğitim / Val Accuracy ────────────────────────
ax2 = fig.add_subplot(gs[0, 1])
ax2.plot(ep, [v*100 for v in history.history["accuracy"]],
         color=GREEN, lw=1.8, label="Train Acc")
ax2.plot(ep, [v*100 for v in history.history["val_accuracy"]],
         color=PURPLE, lw=1.8, ls="--", label="Val Acc")
ax2.set_ylim(0, 105)
ax2.set_ylabel("Doğruluk (%)", color=MUTED, fontsize=8)
ax2.legend(facecolor="#111", edgecolor="#333", labelcolor="white", fontsize=8)
ax2.xaxis.set_major_locator(MaxNLocator(integer=True))
style_ax(ax2, "Eğitim / Doğrulama Doğruluğu")

# ── Panel 3: Confusion Matrix ──────────────────────────────
ax3 = fig.add_subplot(gs[0, 2])
sns.heatmap(
    cm, annot=True, fmt="d", cmap="YlOrRd",
    xticklabels=CLASS_NAMES, yticklabels=CLASS_NAMES,
    ax=ax3, linewidths=0.5, linecolor="#222",
    cbar_kws={"shrink": 0.8},
    annot_kws={"size": 13, "weight": "bold", "color": "white"}
)
ax3.set_xlabel("Tahmin", color=MUTED, fontsize=8)
ax3.set_ylabel("Gerçek",  color=MUTED, fontsize=8)
ax3.tick_params(colors=MUTED, labelsize=8, rotation=0)
style_ax(ax3, "Confusion Matrix")

# ── Panel 4: Sınıf bazlı doğruluk ─────────────────────────
ax4 = fig.add_subplot(gs[1, 0])
class_acc = [cm[i, i] / cm[i].sum() * 100 for i in range(3)]
bars = ax4.bar(CLASS_NAMES, class_acc,
               color=[GREEN, TEAL, PURPLE], width=0.5, edgecolor="#222")
for bar, val in zip(bars, class_acc):
    ax4.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
             f"%{val:.1f}", ha="center", color="white",
             fontsize=10, fontweight="bold", fontfamily="monospace")
ax4.set_ylim(0, 115)
ax4.set_ylabel("Doğruluk (%)", color=MUTED, fontsize=8)
style_ax(ax4, "Sınıf Bazlı Doğruluk")

# ── Panel 5: Olasılık dağılımı (test seti) ────────────────
ax5 = fig.add_subplot(gs[1, 1])
colors_c = [GREEN, TEAL, PURPLE]
for i, (cls, col) in enumerate(zip(CLASS_NAMES, colors_c)):
    mask = y_test == i
    ax5.scatter(y_pred_prob[mask, i],
                np.full(mask.sum(), i) + np.random.uniform(-0.2, 0.2, mask.sum()),
                c=col, alpha=0.7, s=40, edgecolors="none", label=cls)
ax5.set_yticks([0, 1, 2])
ax5.set_yticklabels(CLASS_NAMES, color=MUTED, fontsize=8)
ax5.set_xlabel("Tahmin Olasılığı", color=MUTED, fontsize=8)
ax5.axvline(0.5, color=GOLD, lw=1, ls="--", alpha=0.5)
ax5.legend(facecolor="#111", edgecolor="#333", labelcolor="white", fontsize=8)
style_ax(ax5, "Tahmin Olasılıkları (Test Seti)")

# ── Panel 6: Metrik özeti ──────────────────────────────────
ax6 = fig.add_subplot(gs[1, 2])
ax6.axis("off")
style_ax(ax6, "Model Özeti")

from sklearn.metrics import precision_score, recall_score, f1_score
prec   = precision_score(y_test, y_pred, average="weighted") * 100
recall = recall_score(y_test, y_pred, average="weighted") * 100
f1     = f1_score(y_test, y_pred, average="weighted") * 100

summary = [
    ("Accuracy",          f"%{acc*100:.2f}",    GREEN),
    ("Precision (w.avg)", f"%{prec:.2f}",        TEAL),
    ("Recall (w.avg)",    f"%{recall:.2f}",       PURPLE),
    ("F1 Score (w.avg)",  f"%{f1:.2f}",           GOLD),
    ("─────────────",     "─────────",            MUTED),
    ("Eğitim Örneği",     str(len(X_train)),      TEXT := "#94A3B8"),
    ("Test Örneği",       str(len(X_test)),        TEXT),
    ("Özellik Sayısı",    "4",                    TEXT),
    ("Sınıf Sayısı",      "3",                    TEXT),
    ("Toplam Parametre",  f"{model.count_params():,}", TEXT),
    ("Epoch (gerçek)",    str(len(ep)),            TEXT),
]

y_pos = 0.96
for label, val, col in summary:
    ax6.text(0.05, y_pos, label, transform=ax6.transAxes,
             color=MUTED, fontsize=9, fontfamily="monospace")
    ax6.text(0.65, y_pos, val,  transform=ax6.transAxes,
             color=col,  fontsize=9, fontfamily="monospace", fontweight="bold")
    y_pos -= 0.085

plt.savefig("iris_mlp_results.png", dpi=150,
            bbox_inches="tight", facecolor="#0A0A0A")
print("\n[GRAFİK] ✓ Kaydedildi: iris_mlp_results.png")
plt.show()