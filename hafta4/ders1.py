"""
2D Mühendislik Mesh Uygulaması — Yeniden Tasarım
==================================================
Tasarım: Koyu endüstriyel tema, temiz mesh görselleştirme,
         profesyonel mühendislik yazılımı estetiği.

Kurulum:
    pip install pygame numpy scipy opencv-python
"""

import sys, math
import tkinter as tk
from tkinter import filedialog

import cv2
import numpy as np
import pygame
from scipy.spatial import Delaunay

# ─── RENK PALETİ ──────────────────────────────────────────────────────────────
# Endüstriyel koyu tema
BG          = (13,  17,  23)    # çok koyu lacivert-gri
CANVAS_BG   = (20,  26,  34)    # tuval arka planı
PANEL_BG    = (10,  13,  18)    # alt panel
BORDER      = (30,  40,  55)    # çerçeve çizgisi
ACCENT      = (0,   180, 140)   # teal aksan (ana renk)
ACCENT2     = (255, 180, 40)    # amber (uyarı/vurgu)
TEXT_BRIGHT = (220, 230, 240)   # parlak metin
TEXT_DIM    = (80,  100, 120)   # soluk metin
TEXT_MID    = (140, 160, 180)   # orta metin

# Mesh renkleri
MESH_LINE   = (0,   200, 160)   # teal çizgi
MESH_FILL_A = 18                # fill alfa
MESH_FILL_C = (0,   160, 120)   # fill rengi

# Dış kontur
OUTLINE_C   = (60,  120, 200)   # mavi outline
OUTLINE_W   = 2

# Delik renkleri
HOLE_FILL   = (200, 50,  50,  110)
HOLE_EDGE   = (240, 80,  80)
HOLE_HOVER  = (255, 120, 60)

# ─── AYARLAR ──────────────────────────────────────────────────────────────────
MAX_W, MAX_H   = 920, 620
PANEL_H        = 90
INNER_PTS      = 3200
CONTOUR_STEP   = 0.0012
CIRCLE_PTS     = 52
HOLE_MARGIN    = 4
MIN_HOLE_R     = 4
MAX_HOLE_RATIO = 0.30

# ─── DURUM ────────────────────────────────────────────────────────────────────
detected_holes = []
mesh_tris      = []
is_generated   = False
status_msg     = "Delik secmek icin tikla  |  Mesh icin ENTER"
hover_hole     = -1
mesh_stats_txt = ""

# ─── YARDIMCILAR ──────────────────────────────────────────────────────────────

def open_file():
    root = tk.Tk(); root.withdraw()
    root.attributes("-topmost", True)
    p = filedialog.askopenfilename(
        title="Resim Sec",
        filetypes=[("Resim", "*.png *.jpg *.jpeg *.bmp"), ("Tumu", "*.*")]
    )
    root.destroy()
    return p


def load_image(path):
    with open(path, "rb") as f:
        buf = np.frombuffer(f.read(), dtype=np.uint8)
    img = cv2.imdecode(buf, cv2.IMREAD_COLOR)
    if img is None: raise ValueError("Resim okunamadi.")
    h, w = img.shape[:2]
    scale = min(MAX_W / w, MAX_H / h, 1.0)
    img = cv2.resize(img, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_AREA)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thr = cv2.threshold(blur, 200, 255, cv2.THRESH_BINARY_INV)
    return img, thr


def find_main_contour(thr):
    cnts, _ = cv2.findContours(thr, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return max(cnts, key=cv2.contourArea) if cnts else None


def find_inner_contours(thr, main_cnt):
    cnts, _ = cv2.findContours(thr, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    H, W = thr.shape
    max_r = min(W, H) * MAX_HOLE_RATIO
    inner = []
    for c in cnts:
        if cv2.contourArea(c) < math.pi * MIN_HOLE_R**2: continue
        (cx, cy), r = cv2.minEnclosingCircle(c)
        if r >= max_r: continue
        if np.array_equal(c, main_cnt): continue
        if cv2.pointPolygonTest(main_cnt, (float(cx), float(cy)), False) > 0:
            inner.append((c, float(cx), float(cy), float(r)))
    return inner


def point_near_hole(px, py, holes, tol=6):
    return any(math.hypot(px-hx, py-hy) < hr+tol for hx, hy, hr in holes)


def generate_mesh(main_cnt, holes, W, H):
    pts = []
    peri   = cv2.arcLength(main_cnt, True)
    approx = cv2.approxPolyDP(main_cnt, CONTOUR_STEP * peri, True)
    for p in approx: pts.append(p[0].astype(float))

    for hx, hy, hr in holes:
        for i in range(CIRCLE_PTS):
            a = 2 * math.pi * i / CIRCLE_PTS
            r = hr + HOLE_MARGIN
            pts.append([hx + r*math.cos(a), hy + r*math.sin(a)])

    rng = np.random.default_rng(42)
    added = attempts = 0
    while added < INNER_PTS and attempts < INNER_PTS * 14:
        attempts += 1
        rx, ry = rng.uniform(0, W), rng.uniform(0, H)
        if cv2.pointPolygonTest(main_cnt, (float(rx), float(ry)), False) < 0: continue
        if any(math.hypot(rx-hx, ry-hy) <= hr+HOLE_MARGIN for hx, hy, hr in holes): continue
        pts.append([rx, ry]); added += 1

    points = np.array(pts, dtype=float)
    tri    = Delaunay(points)
    valid  = []
    for s in tri.simplices:
        v = points[s]; cx, cy = float(v[:,0].mean()), float(v[:,1].mean())
        if cv2.pointPolygonTest(main_cnt, (cx, cy), False) < 0: continue
        if any(math.hypot(cx-hx, cy-hy) <= hr for hx, hy, hr in holes): continue
        valid.append(v)
    return valid


def tri_area(t):
    a, b, c = t
    return abs((b[0]-a[0])*(c[1]-a[1]) - (c[0]-a[0])*(b[1]-a[1])) / 2


def draw_rounded_rect(surf, color, rect, radius=8, width=0):
    pygame.draw.rect(surf, color, rect, width, border_radius=radius)


def img_to_surface(img_bgr):
    rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
    return pygame.image.fromstring(rgb.tobytes(), (rgb.shape[1], rgb.shape[0]), "RGB")


# ─── BADGE ÇİZİCİ ─────────────────────────────────────────────────────────────
def draw_badge(surf, font, key_str, label_str, x, y, active=True):
    """[KEY] Label şeklinde pill badge çizer."""
    key_col   = ACCENT  if active else TEXT_DIM
    label_col = TEXT_BRIGHT if active else TEXT_DIM

    k = font["key"].render(f" {key_str} ", True, BG)
    l = font["sm"].render(f" {label_str} ", True, label_col)

    kw, kh = k.get_size()
    lw     = l.get_width()
    pad    = 4
    total_w = kw + lw + pad

    # key kutusu
    key_bg = pygame.Surface((kw, kh), pygame.SRCALPHA)
    key_bg.fill((*key_col, 255))
    surf.blit(key_bg, (x, y))
    surf.blit(k,      (x, y))

    # label
    surf.blit(l, (x + kw + pad, y + 1))

    return total_w + 16


# ─── ANA PROGRAM ──────────────────────────────────────────────────────────────
def main():
    global detected_holes, mesh_tris, is_generated, status_msg, hover_hole, mesh_stats_txt

    path = open_file()
    if not path: sys.exit()

    try:
        orig_img, thresh = load_image(path)
    except Exception as e:
        print(f"Hata: {e}"); sys.exit()

    H_img, W_img = orig_img.shape[:2]
    main_cnt     = find_main_contour(thresh)
    if main_cnt is None: print("Kontur bulunamadi."); sys.exit()

    inner_contours = find_inner_contours(thresh, main_cnt)

    pygame.init()

    # Pencere boyutu: canvas + sol sidebar (240px) + sağ boşluk
    SIDEBAR    = 220
    WIN_W      = W_img + SIDEBAR
    WIN_H      = H_img + PANEL_H
    CANVAS_X   = SIDEBAR   # canvas solda değil, sağda

    win = pygame.display.set_mode((WIN_W, WIN_H))
    pygame.display.set_caption("Mesh Studio")

    # Orijinal resim yüzeyi
    bg_surf = img_to_surface(orig_img)

    # Fontlar — Courier New mühendislik estetiği için
    fonts = {
        "title": pygame.font.SysFont("Courier New", 16, bold=True),
        "key":   pygame.font.SysFont("Courier New", 13, bold=True),
        "md":    pygame.font.SysFont("Courier New", 13, bold=True),
        "sm":    pygame.font.SysFont("Courier New", 12),
        "tiny":  pygame.font.SysFont("Courier New", 11),
        "mono":  pygame.font.SysFont("Courier New", 12),
    }

    overlay     = pygame.Surface((WIN_W, WIN_H), pygame.SRCALPHA)
    mesh_surf   = None
    clock       = pygame.time.Clock()

    # Izgara pattern (canvas arka plan için)
    def make_grid(w, h, step=24):
        s = pygame.Surface((w, h))
        s.fill(CANVAS_BG)
        for x in range(0, w, step):
            pygame.draw.line(s, BORDER, (x, 0), (x, h))
        for y in range(0, h, step):
            pygame.draw.line(s, BORDER, (0, y), (w, y))
        return s

    grid_surf = make_grid(W_img, H_img)

    def rebuild_mesh_surf():
        nonlocal mesh_surf
        if not mesh_tris:
            mesh_surf = None; return
        s = pygame.Surface((W_img, H_img), pygame.SRCALPHA)
        fill_col = (*MESH_FILL_C, MESH_FILL_A)
        line_col = (*MESH_LINE, 180)
        for t in mesh_tris:
            pts_i = [(int(p[0]), int(p[1])) for p in t]
            pygame.draw.polygon(s, fill_col, pts_i)
            pygame.draw.polygon(s, line_col, pts_i, 1)
        mesh_surf = s

    while True:
        mx_raw, my_raw = pygame.mouse.get_pos()
        # Canvas koordinatlarına çevir
        mx = mx_raw - CANVAS_X
        my = my_raw

        hover_hole = -1
        if 0 <= mx < W_img and 0 <= my < H_img:
            for i, (hx, hy, hr) in enumerate(detected_holes):
                if math.hypot(mx - hx, my - hy) <= hr + 8:
                    hover_hole = i; break

        # ── OLAYLAR ──────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    status_msg = "Hesaplaniyor..."
                    win.fill(BG); pygame.display.flip()
                    mesh_tris    = generate_mesh(main_cnt, detected_holes, W_img, H_img)
                    is_generated = True
                    rebuild_mesh_surf()
                    areas = [tri_area(t) for t in mesh_tris]
                    mesh_stats_txt = (f"{len(mesh_tris)} eleman  |  "
                                      f"ort {np.mean(areas):.0f} px2  |  "
                                      f"min {np.min(areas):.0f}  max {np.max(areas):.0f}")
                    status_msg = "Mesh hazir."

                elif event.key == pygame.K_c:
                    detected_holes = []; mesh_tris = []
                    is_generated = False; mesh_surf = None
                    mesh_stats_txt = ""; status_msg = "Temizlendi."

                elif event.key == pygame.K_r:
                    if detected_holes:
                        detected_holes.pop()
                        is_generated = False; mesh_surf = None
                        status_msg = "Son delik silindi."

                elif event.key == pygame.K_s:
                    fname = "mesh_output.png"
                    pygame.image.save(win, fname)
                    status_msg = f"Kaydedildi: {fname}"

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if CANVAS_X <= mx_raw < CANVAS_X + W_img and my_raw < H_img:
                    if hover_hole >= 0:
                        detected_holes.pop(hover_hole)
                        is_generated = False; mesh_surf = None
                        status_msg = "Delik kaldirildi."
                    else:
                        for (c, cx, cy, r) in inner_contours:
                            if cv2.pointPolygonTest(c, (float(mx), float(my)), False) >= 0:
                                if not point_near_hole(cx, cy, detected_holes, tol=r):
                                    detected_holes.append((cx, cy, r))
                                    is_generated = False; mesh_surf = None
                                    status_msg = f"Delik eklendi — r={r:.0f}px  |  Toplam: {len(detected_holes)}"
                                break

        # ── ÇİZİM ────────────────────────────────────────────
        win.fill(BG)
        overlay.fill((0, 0, 0, 0))

        # ── SOL SİDEBAR ──────────────────────────────────────
        # Arka plan
        pygame.draw.rect(win, (16, 21, 30), (0, 0, SIDEBAR, WIN_H))
        pygame.draw.line(win, BORDER, (SIDEBAR-1, 0), (SIDEBAR-1, WIN_H), 1)

        # Başlık
        pygame.draw.rect(win, (8, 12, 20), (0, 0, SIDEBAR, 56))
        pygame.draw.line(win, (*ACCENT, 255), (0, 55), (SIDEBAR, 55), 1)

        title1 = fonts["title"].render("MESH", True, ACCENT)
        title2 = fonts["title"].render("STUDIO", True, TEXT_BRIGHT)
        win.blit(title1,  (14, 12))
        win.blit(title2,  (14 + title1.get_width() + 6, 12))
        ver = fonts["tiny"].render("v2.0  2D FEM", True, TEXT_DIM)
        win.blit(ver, (14, 33))

        # Bilgi kutuları
        def info_box(label, value, y, col=ACCENT):
            pygame.draw.rect(win, (22, 29, 40), (10, y, SIDEBAR-20, 42), border_radius=4)
            pygame.draw.rect(win, BORDER,       (10, y, SIDEBAR-20, 42), 1, border_radius=4)
            lbl = fonts["tiny"].render(label.upper(), True, TEXT_DIM)
            val = fonts["md"].render(str(value), True, col)
            win.blit(lbl, (18, y + 6))
            win.blit(val, (18, y + 21))

        info_box("Boyut",    f"{W_img} x {H_img} px", 68)
        info_box("Delikler", str(len(detected_holes)),  118, ACCENT2 if detected_holes else TEXT_MID)
        info_box("Elemanlar",str(len(mesh_tris)) if is_generated else "—", 168,
                 ACCENT if is_generated else TEXT_MID)

        # Ayırıcı
        pygame.draw.line(win, BORDER, (10, 220), (SIDEBAR-10, 220), 1)

        # Tuş rehberi
        key_y = 230
        lbl = fonts["tiny"].render("KISAYOLLAR", True, TEXT_DIM)
        win.blit(lbl, (14, key_y)); key_y += 18

        shortcuts = [
            ("ENTER", "Mesh uret"),
            ("C",     "Temizle"),
            ("R",     "Son deligi sil"),
            ("S",     "PNG kaydet"),
        ]
        for k, desc in shortcuts:
            # key pill
            k_s = fonts["key"].render(k, True, BG)
            kw, kh = k_s.get_width() + 10, k_s.get_height() + 4
            pygame.draw.rect(win, ACCENT, (14, key_y, kw, kh), border_radius=3)
            win.blit(k_s, (19, key_y + 2))
            d_s = fonts["sm"].render(desc, True, TEXT_MID)
            win.blit(d_s, (14 + kw + 8, key_y + 3))
            key_y += kh + 6

        # Ayırıcı
        pygame.draw.line(win, BORDER, (10, key_y + 4), (SIDEBAR-10, key_y + 4), 1)

        # Delik listesi
        hole_y = key_y + 14
        lbl2 = fonts["tiny"].render("DELIKLER", True, TEXT_DIM)
        win.blit(lbl2, (14, hole_y)); hole_y += 16
        for i, (hx, hy, hr) in enumerate(detected_holes):
            col = ACCENT2 if i == hover_hole else TEXT_MID
            txt = fonts["tiny"].render(f"#{i+1}  ({int(hx)},{int(hy)})  r={int(hr)}", True, col)
            win.blit(txt, (14, hole_y))
            hole_y += 16
            if hole_y > WIN_H - 80: break

        # ── CANVAS ───────────────────────────────────────────
        # Izgara arka plan
        win.blit(grid_surf, (CANVAS_X, 0))

        # Orijinal resim (yarı şeffaf, mesh varsa)
        if is_generated:
            bg_alpha = pygame.Surface((W_img, H_img), pygame.SRCALPHA)
            bg_alpha.blit(bg_surf, (0, 0))
            bg_alpha.set_alpha(60)
            win.blit(bg_alpha, (CANVAS_X, 0))
        else:
            win.blit(bg_surf, (CANVAS_X, 0))

        # Mesh
        if mesh_surf:
            win.blit(mesh_surf, (CANVAS_X, 0))

        # Ana kontur
        if main_cnt is not None:
            pts_c = [(int(p[0][0]) + CANVAS_X, int(p[0][1])) for p in main_cnt]
            if len(pts_c) > 2:
                pygame.draw.lines(win, (*OUTLINE_C, 200), True, pts_c, OUTLINE_W)

        # Delikler
        for i, (hx, hy, hr) in enumerate(detected_holes):
            scx = int(hx) + CANVAS_X
            scy = int(hy)
            r   = max(1, int(hr))
            is_hov = (i == hover_hole)

            # Fill
            hole_fill_s = pygame.Surface((r*2+4, r*2+4), pygame.SRCALPHA)
            fill_col = (255, 100, 60, 130) if is_hov else (200, 50, 50, 90)
            pygame.draw.circle(hole_fill_s, fill_col, (r+2, r+2), r)
            win.blit(hole_fill_s, (scx - r - 2, scy - r - 2))

            # Edge — çift çizgi efekti
            edge_col = HOLE_HOVER if is_hov else HOLE_EDGE
            pygame.draw.circle(win, edge_col, (scx, scy), r, 2)
            pygame.draw.circle(win, (*edge_col[:3], 80), (scx, scy), r+3, 1)

            # Merkez nokta
            pygame.draw.circle(win, edge_col, (scx, scy), 3)

            # Numaralı etiket (delik dışında, üstte)
            badge = fonts["tiny"].render(f"#{i+1}", True, BG)
            bw, bh = badge.get_size()
            badge_x = scx - bw//2 - 3
            badge_y = scy - r - bh - 6
            pygame.draw.rect(win, edge_col,
                             (badge_x-2, badge_y-2, bw+8, bh+4), border_radius=3)
            win.blit(badge, (badge_x+2, badge_y))

            if is_hov:
                tip = fonts["tiny"].render("tikla: kaldir", True, ACCENT2)
                win.blit(tip, (scx - tip.get_width()//2, scy - r - 28))

        # Canvas kenarlığı
        pygame.draw.rect(win, (*ACCENT[:3], 60),
                         (CANVAS_X, 0, W_img, H_img), 2)

        # ── ALT PANEL ────────────────────────────────────────
        panel_y = H_img
        pygame.draw.rect(win, PANEL_BG, (0, panel_y, WIN_W, PANEL_H))
        pygame.draw.line(win, ACCENT, (0, panel_y), (WIN_W, panel_y), 1)

        # Durum mesajı
        dot_col = ACCENT if not is_generated else (80, 200, 100)
        pygame.draw.circle(win, dot_col, (SIDEBAR + 16, panel_y + 22), 5)
        st = fonts["md"].render(status_msg, True, TEXT_BRIGHT)
        win.blit(st, (SIDEBAR + 28, panel_y + 14))

        # Mesh istatistikleri
        if mesh_stats_txt:
            ms = fonts["mono"].render(mesh_stats_txt, True, TEXT_DIM)
            win.blit(ms, (SIDEBAR + 28, panel_y + 36))

        # FPS (sağ köşe)
        fps_txt = fonts["tiny"].render(f"{clock.get_fps():.0f} fps", True, TEXT_DIM)
        win.blit(fps_txt, (WIN_W - fps_txt.get_width() - 12, panel_y + 10))

        # Koordinat göstergesi (canvas üzerindeyse)
        if CANVAS_X <= mx_raw < CANVAS_X + W_img and my_raw < H_img:
            coord = fonts["tiny"].render(f"x={mx}  y={my}", True, TEXT_DIM)
            win.blit(coord, (WIN_W - coord.get_width() - 12, panel_y + 28))

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main()