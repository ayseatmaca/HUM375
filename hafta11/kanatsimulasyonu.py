import sys
import os
import numpy as np
import urllib.request
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QLabel, QSlider, QComboBox, QPushButton, QFileDialog, QMessageBox, 
                             QGroupBox, QFormLayout, QRadioButton, QButtonGroup)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.path import Path

# --- Matplotlib Karanlık Tema (Dark Mode) ---
plt.style.use('dark_background')

class AirfoilGenerator:
    @staticmethod
    def generate_naca4(naca_code, n=100):
        m = int(naca_code[0]) / 100.0
        p = int(naca_code[1]) / 10.0
        t = int(naca_code[2:]) / 100.0
        
        beta = np.linspace(0, np.pi, n)
        x = 0.5 * (1 - np.cos(beta))
        
        yt = 5 * t * (0.2969 * np.sqrt(x) - 0.1260 * x - 0.3516 * x**2 + 0.2843 * x**3 - 0.1015 * x**4)
        
        yc = np.zeros_like(x)
        dyc_dx = np.zeros_like(x)
        if p > 0:
            mask1 = x <= p
            mask2 = x > p
            yc[mask1] = m / (p**2) * (2 * p * x[mask1] - x[mask1]**2)
            yc[mask2] = m / ((1 - p)**2) * ((1 - 2 * p) + 2 * p * x[mask2] - x[mask2]**2)
            dyc_dx[mask1] = 2 * m / (p**2) * (p - x[mask1])
            dyc_dx[mask2] = 2 * m / ((1 - p)**2) * (p - x[mask2])
            
        theta = np.arctan(dyc_dx)
        
        xu = x - yt * np.sin(theta)
        yu = yc + yt * np.cos(theta)
        xl = x + yt * np.sin(theta)
        yl = yc - yt * np.cos(theta)
        
        X = np.concatenate([xl[::-1], xu[1:]])
        Y = np.concatenate([yl[::-1], yu[1:]])
        
        return X, Y

    @staticmethod
    def fetch_uiuc_airfoil(name):
        urls = {
            "Clark Y": "https://m-selig.ae.illinois.edu/ads/coord/clarky.dat",
            "Eppler 420": "https://m-selig.ae.illinois.edu/ads/coord/e420.dat"
        }
        try:
            req = urllib.request.Request(urls[name], headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=5) as response:
                data = response.read().decode('utf-8').splitlines()
            
            coords = []
            for line in data:
                parts = line.strip().split()
                if len(parts) >= 2:
                    try:
                        x, y = float(parts[0]), float(parts[1])
                        if x > 1.0 or x < -0.1: continue
                        coords.append((x, y))
                    except ValueError:
                        pass
            coords = np.array(coords)
            coords = coords[::-1]
            return coords[:, 0], coords[:, 1]
        except Exception as e:
            print(f"Uyarı: {name} profili indirilemedi ({e}). NACA 0012 kullanılıyor.")
            return AirfoilGenerator.generate_naca4("0012")

class Panels:
    def __init__(self, x, y):
        self.x1 = x[:-1]
        self.y1 = y[:-1]
        self.x2 = x[1:]
        self.y2 = y[1:]
        self.xc = (self.x1 + self.x2) / 2
        self.yc = (self.y1 + self.y2) / 2
        
        dx = self.x2 - self.x1
        dy = self.y2 - self.y1
        self.length = np.hypot(dx, dy)
        self.cos_theta = dx / self.length
        self.sin_theta = dy / self.length
        self.N = len(self.x1)

def calc_influence(x_pts, y_pts, panels):
    shape = x_pts.shape
    x_pts = x_pts.ravel()[:, None]
    y_pts = y_pts.ravel()[:, None]
    
    x1 = panels.x1[None, :]
    y1 = panels.y1[None, :]
    ct = panels.cos_theta[None, :]
    st = panels.sin_theta[None, :]
    l = panels.length[None, :]
    
    dx = x_pts - x1
    dy = y_pts - y1
    x_star = dx * ct + dy * st
    y_star = -dx * st + dy * ct
    
    y_star[np.abs(y_star) < 1e-8] = 1e-8
    
    r1_sq = x_star**2 + y_star**2
    r2_sq = (x_star - l)**2 + y_star**2
    
    th1 = np.arctan2(y_star, x_star)
    th2 = np.arctan2(y_star, x_star - l)
    
    us_star = 1.0 / (4 * np.pi) * np.log(r2_sq / r1_sq)
    vs_star = 1.0 / (2 * np.pi) * (th2 - th1)
    
    uv_star = 1.0 / (2 * np.pi) * (th2 - th1)
    vv_star = -1.0 / (4 * np.pi) * np.log(r2_sq / r1_sq)
    
    us = us_star * ct - vs_star * st
    vs = us_star * st + vs_star * ct
    
    uv = uv_star * ct - vv_star * st
    vv = uv_star * st + vv_star * ct
    
    return us.reshape(shape + (panels.N,)), vs.reshape(shape + (panels.N,)), \
           uv.reshape(shape + (panels.N,)), vv.reshape(shape + (panels.N,))

class AeroSolver:
    def __init__(self, x, y):
        self.panels = Panels(x, y)
        self.X_airfoil = x
        self.Y_airfoil = y
        self.solve_matrix()
        
    def solve_matrix(self):
        N = self.panels.N
        us, vs, uv, vv = calc_influence(self.panels.xc, self.panels.yc, self.panels)
        
        nx = -self.panels.sin_theta
        ny = self.panels.cos_theta
        tx = self.panels.cos_theta
        ty = self.panels.sin_theta
        
        A = us * nx[:, None] + vs * ny[:, None]
        B = uv * nx[:, None] + vv * ny[:, None]
        At = us * tx[:, None] + vs * ty[:, None]
        Bt = uv * tx[:, None] + vv * ty[:, None]
        
        i = np.arange(N)
        A[i, i] = 0.5
        At[i, i] = 0.0
        B[i, i] = 0.0
        Bt[i, i] = 0.5
        
        M = np.zeros((N+1, N+1))
        M[:N, :N] = A
        M[:N, N] = np.sum(B, axis=1)
        
        M[N, :N] = At[0, :] + At[-1, :]
        M[N, N] = np.sum(Bt[0, :] + Bt[-1, :])
        
        self.M = M
        self.nx = nx
        self.ny = ny
        self.tx = tx
        self.ty = ty
        self.At = At
        self.Bt = Bt
        
    def calculate_flow(self, V_inf, alpha_deg):
        alpha_rad = np.radians(alpha_deg)
        U_nx = V_inf * np.cos(alpha_rad)
        U_ny = V_inf * np.sin(alpha_rad)
        
        rhs = np.zeros(self.panels.N + 1)
        rhs[:self.panels.N] = -(U_nx * self.nx + U_ny * self.ny)
        rhs[self.panels.N] = -(U_nx * (self.tx[0] + self.tx[-1]) + U_ny * (self.ty[0] + self.ty[-1]))
        
        sol = np.linalg.solve(self.M, rhs)
        self.sigma = sol[:self.panels.N]
        self.gamma = sol[self.panels.N]
        
        Vt = np.dot(self.At, self.sigma) + np.sum(self.Bt, axis=1) * self.gamma + (U_nx * self.tx + U_ny * self.ty)
        self.Cp = 1.0 - (Vt / V_inf)**2
        
        # Kaldırma Katsayısı (Cl) ve Toplam Sirkülasyon
        c = 1.0 # normalize chord length
        self.total_gamma = self.gamma * np.sum(self.panels.length)
        self.Cl = 2.0 * self.total_gamma / (V_inf * c)
        
        return self.Cp
        
    def calculate_velocity_field(self, X_grid, Y_grid, V_inf, alpha_deg):
        alpha_rad = np.radians(alpha_deg)
        U_nx = V_inf * np.cos(alpha_rad)
        U_ny = V_inf * np.sin(alpha_rad)
        
        us, vs, uv, vv = calc_influence(X_grid, Y_grid, self.panels)
        
        u = np.sum(us * self.sigma, axis=-1) + np.sum(uv * self.gamma, axis=-1) + U_nx
        v = np.sum(vs * self.sigma, axis=-1) + np.sum(vv * self.gamma, axis=-1) + U_ny
        
        path = Path(np.column_stack((self.X_airfoil, self.Y_airfoil)))
        pts = np.column_stack((X_grid.ravel(), Y_grid.ravel()))
        inside = path.contains_points(pts).reshape(X_grid.shape)
        
        u[inside] = np.nan
        v[inside] = np.nan
        
        return u, v

class CalcThread(QThread):
    finished_signal = pyqtSignal(np.ndarray, np.ndarray, np.ndarray, np.ndarray, float, float)
    
    def __init__(self, solver, V_inf, alpha_deg):
        super().__init__()
        self.solver = solver
        self.V_inf = V_inf
        self.alpha_deg = alpha_deg
        
    def run(self):
        Cp = self.solver.calculate_flow(self.V_inf, self.alpha_deg)
        
        x_min, x_max = -0.5, 1.5
        y_min, y_max = -0.6, 0.6
        # Çözünürlüğü artırdık (contourf için)
        x_vals = np.linspace(x_min, x_max, 120)
        y_vals = np.linspace(y_min, y_max, 120)
        X_grid, Y_grid = np.meshgrid(x_vals, y_vals)
        
        u, v = self.solver.calculate_velocity_field(X_grid, Y_grid, self.V_inf, self.alpha_deg)
        
        self.finished_signal.emit(X_grid, Y_grid, u, v, self.solver.Cl, self.solver.total_gamma)

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CFD Kanat Profili Simülatörü - Advanced")
        self.setGeometry(100, 100, 1300, 850)
        
        self.solver = None
        self.current_cp = None
        self.is_simulating = False
        self.cbar = None
        self.pending_update = False
        self.current_calc_alpha = None
        self.current_calc_vel = None
        
        self.init_ui()
        self.update_airfoil()
        
    def init_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QHBoxLayout(main_widget)
        
        # --- Sol Panel (Kontroller) ---
        control_panel = QWidget()
        control_layout = QVBoxLayout(control_panel)
        control_panel.setFixedWidth(320)
        
        # Profil Seçimi
        group_airfoil = QGroupBox("Profil Ayarları")
        form_airfoil = QFormLayout()
        self.cb_airfoil = QComboBox()
        self.cb_airfoil.addItems(["NACA 0012", "NACA 2412", "NACA 4412", "Clark Y", "Eppler 420"])
        self.cb_airfoil.currentIndexChanged.connect(self.update_airfoil)
        form_airfoil.addRow("Kanat Profili:", self.cb_airfoil)
        group_airfoil.setLayout(form_airfoil)
        control_layout.addWidget(group_airfoil)
        
        # Akış Parametreleri
        group_params = QGroupBox("Akış Parametreleri")
        form_params = QFormLayout()
        
        self.slider_aoa = QSlider(Qt.Orientation.Horizontal)
        self.slider_aoa.setMinimum(-5)
        self.slider_aoa.setMaximum(20)
        self.slider_aoa.setValue(5)
        self.lbl_aoa = QLabel("5 °")
        self.slider_aoa.valueChanged.connect(self.update_params)
        form_params.addRow("Hücum Açısı:", self.lbl_aoa)
        form_params.addRow(self.slider_aoa)
        
        self.slider_vel = QSlider(Qt.Orientation.Horizontal)
        self.slider_vel.setMinimum(10)
        self.slider_vel.setMaximum(100)
        self.slider_vel.setValue(50)
        self.lbl_vel = QLabel("50 m/s")
        self.slider_vel.valueChanged.connect(self.update_params)
        form_params.addRow("Rüzgar Hızı:", self.lbl_vel)
        form_params.addRow(self.slider_vel)
        
        group_params.setLayout(form_params)
        control_layout.addWidget(group_params)
        
        # Gösterim Seçenekleri
        group_view = QGroupBox("Arka Plan Gösterimi")
        view_layout = QVBoxLayout()
        self.radio_vel = QRadioButton("Hız Dağılımı (Velocity)")
        self.radio_vel.setChecked(True)
        self.radio_press = QRadioButton("Basınç Katsayısı (Cp)")
        
        self.btn_group = QButtonGroup()
        self.btn_group.addButton(self.radio_vel)
        self.btn_group.addButton(self.radio_press)
        
        self.radio_vel.toggled.connect(self.update_params)
        self.radio_press.toggled.connect(self.update_params)
        
        view_layout.addWidget(self.radio_vel)
        view_layout.addWidget(self.radio_press)
        group_view.setLayout(view_layout)
        control_layout.addWidget(group_view)
        
        # Canlı Analiz Sonuçları (Dijital Panel)
        group_res = QGroupBox("Canlı Analiz Sonuçları")
        res_layout = QFormLayout()
        
        font_res = QFont()
        font_res.setBold(True)
        font_res.setPointSize(12)
        
        self.lbl_res_cl = QLabel("0.0000")
        self.lbl_res_cl.setFont(font_res)
        self.lbl_res_cl.setStyleSheet("color: #00e676;")
        
        self.lbl_res_gamma = QLabel("0.0000")
        self.lbl_res_gamma.setFont(font_res)
        self.lbl_res_gamma.setStyleSheet("color: #00b0ff;")
        
        res_layout.addRow("Kaldırma Katsayısı ($C_l$):", self.lbl_res_cl)
        res_layout.addRow(r"Toplam Girdap ($\Gamma$):", self.lbl_res_gamma)
        group_res.setLayout(res_layout)
        control_layout.addWidget(group_res)
        
        # Butonlar
        self.btn_simulate = QPushButton("Simülasyonu Başlat")
        self.btn_simulate.clicked.connect(self.toggle_simulation)
        self.btn_simulate.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; font-weight: bold;")
        control_layout.addWidget(self.btn_simulate)
        
        self.btn_export = QPushButton("Verileri Dışa Aktar")
        self.btn_export.clicked.connect(self.export_data)
        self.btn_export.setEnabled(False)
        control_layout.addWidget(self.btn_export)
        
        control_layout.addStretch()
        layout.addWidget(control_panel)
        
        # --- Sağ Panel (Grafikler) ---
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)
        
        self.ax_flow = self.figure.add_subplot(211)
        self.ax_cp = self.figure.add_subplot(212)
        
        self.figure.tight_layout(pad=4.0)
        
    def update_params(self):
        self.lbl_aoa.setText(f"{self.slider_aoa.value()} °")
        self.lbl_vel.setText(f"{self.slider_vel.value()} m/s")
        if self.is_simulating:
            self.run_calculation()
            
    def update_airfoil(self):
        name = self.cb_airfoil.currentText()
        if "NACA" in name:
            x, y = AirfoilGenerator.generate_naca4(name.split(" ")[1])
        else:
            x, y = AirfoilGenerator.fetch_uiuc_airfoil(name)
            
        self.solver = AeroSolver(x, y)
        self.plot_initial()
        if self.is_simulating:
            self.run_calculation()
            
    def toggle_simulation(self):
        self.is_simulating = not self.is_simulating
        if self.is_simulating:
            self.btn_simulate.setText("Simülasyonu Durdur")
            self.btn_simulate.setStyleSheet("background-color: #f44336; color: white; padding: 10px; font-weight: bold;")
            self.btn_export.setEnabled(True)
            self.run_calculation()
        else:
            self.btn_simulate.setText("Simülasyonu Başlat")
            self.btn_simulate.setStyleSheet("background-color: #4CAF50; color: white; padding: 10px; font-weight: bold;")
            
    def plot_initial(self):
        if self.cbar:
            try:
                self.cbar.remove()
            except Exception:
                pass
            self.cbar = None
            
        self.ax_flow.clear()
        self.ax_flow.plot(self.solver.X_airfoil, self.solver.Y_airfoil, 'w-', linewidth=2)
        self.ax_flow.fill(self.solver.X_airfoil, self.solver.Y_airfoil, color='#333333')
        self.ax_flow.set_aspect('equal')
        self.ax_flow.set_xlim(-0.5, 1.5)
        self.ax_flow.set_ylim(-0.6, 0.6)
        self.ax_flow.set_title("Kanat Profili ve Akış Çizgileri")
        self.ax_flow.set_xlabel("x")
        self.ax_flow.set_ylabel("y")
        self.ax_flow.grid(True, color='#444444')
        
        self.ax_cp.clear()
        self.ax_cp.set_title("Yüzey Basınç Katsayısı ($C_p$) Dağılımı")
        self.ax_cp.set_xlabel("x/c")
        self.ax_cp.set_ylabel("$C_p$")
        self.ax_cp.grid(True, color='#444444')
        
        self.lbl_res_cl.setText("0.0000")
        self.lbl_res_gamma.setText("0.0000")
        
        self.canvas.draw()
        
    def run_calculation(self):
        if hasattr(self, 'calc_thread') and self.calc_thread.isRunning():
            self.pending_update = True
            return
            
        alpha = self.slider_aoa.value()
        v_inf = self.slider_vel.value()
        
        self.current_calc_alpha = alpha
        self.current_calc_vel = v_inf
        
        self.calc_thread = CalcThread(self.solver, v_inf, alpha)
        self.calc_thread.finished_signal.connect(self.update_plots)
        self.calc_thread.start()
        
    def update_plots(self, X_grid, Y_grid, u, v, Cl, total_gamma):
        self.lbl_res_cl.setText(f"{Cl:.4f}")
        self.lbl_res_gamma.setText(f"{total_gamma:.4f}")
        
        if self.cbar:
            try:
                self.cbar.remove()
            except Exception:
                pass
            self.cbar = None
            
        self.ax_flow.clear()
            
        speed = np.sqrt(u**2 + v**2)
        
        # Contour Plot (Arka Plan Isı Haritası)
        if self.radio_vel.isChecked():
            contour = self.ax_flow.contourf(X_grid, Y_grid, speed, levels=60, cmap='inferno')
            self.cbar = self.figure.colorbar(contour, ax=self.ax_flow)
            self.cbar.set_label('Hız Dağılımı (m/s)', color='white')
        else:
            cp_grid = 1.0 - (speed / self.slider_vel.value())**2
            # Cp dağılımı için coolwarm uygun (mavi yüksek basınç/yavaş, kırmızı düşük basınç/hızlı)
            contour = self.ax_flow.contourf(X_grid, Y_grid, cp_grid, levels=60, cmap='coolwarm')
            self.cbar = self.figure.colorbar(contour, ax=self.ax_flow)
            self.cbar.set_label('Basınç Katsayısı ($C_p$)', color='white')
            
        self.cbar.ax.yaxis.set_tick_params(color='white')
        plt.setp(plt.getp(self.cbar.ax.axes, 'yticklabels'), color='white')

        # Akış Çizgileri (Streamlines)
        self.ax_flow.streamplot(X_grid, Y_grid, u, v, color='cyan', linewidth=1.0, density=1.2, arrowsize=1.5, zorder=4)
        
        # Profili Çiz (Siyah dolgu, beyaz kenar)
        self.ax_flow.plot(self.solver.X_airfoil, self.solver.Y_airfoil, 'w-', linewidth=2.5, zorder=6)
        self.ax_flow.fill(self.solver.X_airfoil, self.solver.Y_airfoil, color='black', alpha=1.0, zorder=5)
        
        self.ax_flow.set_aspect('equal')
        self.ax_flow.set_xlim(-0.5, 1.5)
        self.ax_flow.set_ylim(-0.6, 0.6)
        self.ax_flow.set_title(f"CFD Analizi (Hücum Açısı: {self.slider_aoa.value()}°, Hız: {self.slider_vel.value()} m/s)", color='white')
        self.ax_flow.set_xlabel("x", color='white')
        self.ax_flow.set_ylabel("y", color='white')
        self.ax_flow.tick_params(colors='white')
        
        # Cp Grafiğini Güncelle
        self.ax_cp.clear()
        Cp = self.solver.Cp
        xc = self.solver.panels.xc
        
        N = self.solver.panels.N
        mid = N // 2
        
        self.ax_cp.plot(xc[:mid], Cp[:mid], color='#00b0ff', linestyle='-', label='Alt Yüzey (Lower)', linewidth=2.5)
        self.ax_cp.plot(xc[mid:], Cp[mid:], color='#ff3d00', linestyle='-', label='Üst Yüzey (Upper)', linewidth=2.5)
        
        self.ax_cp.invert_yaxis()
        self.ax_cp.set_title("Yüzey Basınç Katsayısı ($C_p$) Dağılımı", color='white')
        self.ax_cp.set_xlabel("x/c", color='white')
        self.ax_cp.set_ylabel("$C_p$", color='white')
        self.ax_cp.legend(facecolor='#2b2b2b', edgecolor='white', labelcolor='white')
        self.ax_cp.grid(True, color='#444444', linestyle='--')
        self.ax_cp.tick_params(colors='white')
        
        self.current_cp = Cp
        self.canvas.draw()
        
        # Eğer bekleyen bir güncelleme varsa (kullanıcı slider'ı kaydırmaya devam ettiyse)
        if self.pending_update:
            self.pending_update = False
            if self.slider_aoa.value() != self.current_calc_alpha or self.slider_vel.value() != self.current_calc_vel:
                self.run_calculation()
        
    def export_data(self):
        if self.current_cp is None:
            QMessageBox.warning(self, "Hata", "Önce simülasyonu çalıştırın!")
            return
            
        options = QFileDialog.Options()
        filename, _ = QFileDialog.getSaveFileName(self, "Verileri Kaydet", "cfd_data.csv", "CSV Dosyaları (*.csv)", options=options)
        if filename:
            try:
                data = np.column_stack((self.solver.panels.xc, self.solver.panels.yc, self.current_cp))
                np.savetxt(filename, data, delimiter=',', header='x_c,y_c,Cp', comments='', fmt='%.6f')
                QMessageBox.information(self, "Başarılı", f"Veriler kaydedildi:\n{filename}")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Dosya kaydedilemedi:\n{e}")

    # Çıkış anında Thread'in çökmesini engelleyen metod
    def closeEvent(self, event):
        if hasattr(self, 'calc_thread') and self.calc_thread.isRunning():
            self.calc_thread.terminate()
            self.calc_thread.wait()
        event.accept()

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    
    dark_stylesheet = """
    QMainWindow {
        background-color: #2b2b2b;
    }
    QWidget {
        background-color: #2b2b2b;
        color: #e0e0e0;
        font-size: 14px;
        font-family: 'Segoe UI', Arial, sans-serif;
    }
    QGroupBox {
        border: 1px solid #555;
        border-radius: 6px;
        margin-top: 20px;
        font-weight: bold;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        left: 15px;
        padding: 0 5px;
        color: #ff9800; /* Turuncu başlıklar */
    }
    QPushButton {
        background-color: #424242;
        border: 1px solid #666;
        border-radius: 4px;
        padding: 8px;
    }
    QPushButton:hover {
        background-color: #616161;
    }
    QPushButton:disabled {
        background-color: #222;
        color: #555;
    }
    QComboBox, QSlider {
        background-color: #424242;
        border: 1px solid #555;
        border-radius: 3px;
        padding: 2px;
    }
    QComboBox::drop-down {
        border: 0px;
    }
    QRadioButton {
        padding: 4px;
    }
    QRadioButton::indicator {
        width: 16px;
        height: 16px;
        border-radius: 8px;
        border: 1px solid #888;
        background-color: #2b2b2b;
    }
    QRadioButton::indicator:checked {
        background-color: #ff9800;
        border: 2px solid #2b2b2b;
    }
    """
    app.setStyleSheet(dark_stylesheet)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
