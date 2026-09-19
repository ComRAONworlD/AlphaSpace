import sys
import os
import ctypes

def excepthook(exc_type, exc_value, exc_traceback):
    import traceback
    err_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    try:
        log_dir = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
        with open(os.path.join(log_dir, "crash.log"), "w", encoding="utf-8") as f:
            f.write(err_msg)
    except Exception:
        pass
    sys.__excepthook__(exc_type, exc_value, exc_traceback)

sys.excepthook = excepthook

def resource_path(relative_path):
    """PyInstaller 번들(_MEIPASS) 및 일반 개발 환경 모두에서 리소스 절대경로 반환"""
    if getattr(sys, 'frozen', False):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QComboBox, QWidget, QHBoxLayout, QLabel,
    QPushButton, QMenuBar, QMenu, QMessageBox
)
from PySide6.QtGui import QPalette, QAction, QIcon
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices

from utils import setup_matplotlib
from simulation_tab import SimulationTab
from fitting_tab import FittingTab
from hypothesis_tab import HypothesisTab
from knowledge_base import KnowledgeHubDialog

LIGHT_QSS = """
    QWidget {
        font-family: 'Malgun Gothic', 'AppleGothic', 'NanumGothic', sans-serif;
        font-size: 10pt;
        color: #212529;
    }
    QGroupBox {
        font-weight: bold;
        border: 1px solid #ced4da;
        border-radius: 6px;
        margin-top: 10px;
        padding-top: 14px;
        background-color: #fcfcfc;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 6px;
        color: #0d6efd;
    }
    QPushButton {
        background-color: #f8f9fa;
        border: 1px solid #ced4da;
        border-bottom: 2px solid #adb5bd;
        border-radius: 4px;
        padding: 5px 12px;
        color: #212529;
        font-weight: 500;
    }
    QPushButton:hover {
        background-color: #e9ecef;
        border-color: #0d6efd;
        color: #0d6efd;
    }
    QPushButton:pressed {
        background-color: #c8cbcf;
        border: 1px solid #6c757d;
        border-top: 2px solid #495057;
        padding-top: 7px;
        padding-bottom: 3px;
        padding-left: 14px;
        padding-right: 10px;
        color: #0a58ca;
    }
    QPushButton:disabled {
        background-color: #e9ecef;
        border: 1px solid #dee2e6;
        color: #6c757d;
    }

    /* Primary Button (Blue) */
    QPushButton[btnClass="primary"] {
        background-color: #0d6efd;
        border: 1px solid #0b5ed7;
        border-bottom: 2px solid #084298;
        border-radius: 4px;
        padding: 6px 14px;
        color: #ffffff;
        font-weight: bold;
    }
    QPushButton[btnClass="primary"]:hover {
        background-color: #0b5ed7;
        border-color: #0a58ca;
        color: #ffffff;
    }
    QPushButton[btnClass="primary"]:pressed {
        background-color: #084298;
        border: 1px solid #052c65;
        border-top: 2px solid #031633;
        padding-top: 8px;
        padding-bottom: 4px;
        padding-left: 16px;
        padding-right: 12px;
        color: #d0e2ff;
    }

    /* Success Button (Green) */
    QPushButton[btnClass="success"] {
        background-color: #198754;
        border: 1px solid #157347;
        border-bottom: 2px solid #0f5132;
        border-radius: 4px;
        padding: 6px 14px;
        color: #ffffff;
        font-weight: bold;
    }
    QPushButton[btnClass="success"]:hover {
        background-color: #157347;
        border-color: #146c43;
        color: #ffffff;
    }
    QPushButton[btnClass="success"]:pressed {
        background-color: #0f5132;
        border: 1px solid #0a3622;
        border-top: 2px solid #051b11;
        padding-top: 8px;
        padding-bottom: 4px;
        padding-left: 16px;
        padding-right: 12px;
        color: #d1e7dd;
    }

    /* Secondary Button (Gray) */
    QPushButton[btnClass="secondary"] {
        background-color: #6c757d;
        border: 1px solid #5c636a;
        border-bottom: 2px solid #495057;
        border-radius: 4px;
        padding: 5px 12px;
        color: #ffffff;
        font-weight: bold;
    }
    QPushButton[btnClass="secondary"]:hover {
        background-color: #5c636a;
        border-color: #495057;
        color: #ffffff;
    }
    QPushButton[btnClass="secondary"]:pressed {
        background-color: #495057;
        border: 1px solid #343a40;
        border-top: 2px solid #212529;
        padding-top: 7px;
        padding-bottom: 3px;
        padding-left: 14px;
        padding-right: 10px;
        color: #e0e0e0;
    }

    QComboBox, QLineEdit, QListWidget, QTableWidget, QTextEdit {
        border: 1px solid #ced4da;
        border-radius: 4px;
        padding: 4px;
        background-color: #ffffff;
        color: #212529;
    }
    QTabWidget::pane {
        border: 1px solid #ced4da;
        background: #ffffff;
    }
    QTabBar::tab {
        background: #f1f3f5;
        border: 1px solid #ced4da;
        padding: 8px 16px;
        margin-right: 2px;
        border-top-left-radius: 5px;
        border-top-right-radius: 5px;
        color: #495057;
        font-weight: 500;
    }
    QTabBar::tab:selected {
        background: #ffffff;
        border-bottom-color: #ffffff;
        font-weight: bold;
        color: #0d6efd;
    }
    QHeaderView::section {
        background-color: #f8f9fa;
        border: 1px solid #ced4da;
        padding: 4px;
        font-weight: bold;
        color: #212529;
    }
    QSlider::groove:horizontal {
        height: 6px;
        background: #e9ecef;
        border-radius: 3px;
    }
    QSlider::sub-page:horizontal {
        background: #0d6efd;
        border-radius: 3px;
    }
    QSlider::handle:horizontal {
        background: #ffffff;
        border: 2px solid #0d6efd;
        width: 16px;
        margin-top: -5px;
        margin-bottom: -5px;
        border-radius: 8px;
    }
    QSplitter::handle:horizontal {
        background-color: #dee2e6;
        width: 7px;
        margin: 4px 1px;
        border-radius: 3px;
    }
    QSplitter::handle:horizontal:hover {
        background-color: #0d6efd;
    }
    QSplitter::handle:horizontal:pressed {
        background-color: #0a58ca;
    }
"""

DARK_QSS = """
    QWidget {
        font-family: 'Malgun Gothic', 'AppleGothic', 'NanumGothic', sans-serif;
        font-size: 10pt;
        color: #E0E0E0;
        background-color: #2b2b2b;
    }
    QGroupBox {
        font-weight: bold;
        border: 1px solid #555555;
        border-radius: 6px;
        margin-top: 10px;
        padding-top: 14px;
        background-color: #313335;
    }
    QGroupBox::title {
        subcontrol-origin: margin;
        subcontrol-position: top left;
        padding: 0 6px;
        color: #82AAFF;
    }
    QPushButton {
        background-color: #3c3f41;
        border: 1px solid #555555;
        border-bottom: 2px solid #333333;
        border-radius: 4px;
        padding: 5px 12px;
        color: #E0E0E0;
        font-weight: 500;
    }
    QPushButton:hover {
        background-color: #4b4e50;
        border-color: #82AAFF;
        color: #ffffff;
    }
    QPushButton:pressed {
        background-color: #26282a;
        border: 1px solid #82AAFF;
        border-top: 2px solid #2F65CA;
        padding-top: 7px;
        padding-bottom: 3px;
        padding-left: 14px;
        padding-right: 10px;
        color: #82AAFF;
    }
    QPushButton:disabled {
        background-color: #2e3032;
        border: 1px solid #444444;
        color: #777777;
    }

    /* Primary Accent Button (Blue in Dark Mode) */
    QPushButton[btnClass="primary"] {
        background-color: #2F65CA;
        border: 1px solid #2451a5;
        border-bottom: 2px solid #1a3c7d;
        border-radius: 4px;
        padding: 6px 14px;
        color: #ffffff;
        font-weight: bold;
    }
    QPushButton[btnClass="primary"]:hover {
        background-color: #3d76e4;
        border-color: #82AAFF;
        color: #ffffff;
    }
    QPushButton[btnClass="primary"]:pressed {
        background-color: #1c3e80;
        border: 1px solid #82AAFF;
        border-top: 2px solid #0f2348;
        padding-top: 8px;
        padding-bottom: 4px;
        padding-left: 16px;
        padding-right: 12px;
        color: #d0e2ff;
    }

    /* Success Button (Green in Dark Mode) */
    QPushButton[btnClass="success"] {
        background-color: #218838;
        border: 1px solid #1e7e34;
        border-bottom: 2px solid #145523;
        border-radius: 4px;
        padding: 6px 14px;
        color: #ffffff;
        font-weight: bold;
    }
    QPushButton[btnClass="success"]:hover {
        background-color: #28a745;
        border-color: #5cd079;
        color: #ffffff;
    }
    QPushButton[btnClass="success"]:pressed {
        background-color: #145523;
        border: 1px solid #5cd079;
        border-top: 2px solid #0b3214;
        padding-top: 8px;
        padding-bottom: 4px;
        padding-left: 16px;
        padding-right: 12px;
        color: #d1e7dd;
    }

    /* Secondary Button (Gray in Dark Mode) */
    QPushButton[btnClass="secondary"] {
        background-color: #5a6268;
        border: 1px solid #545b62;
        border-bottom: 2px solid #3e444a;
        border-radius: 4px;
        padding: 5px 12px;
        color: #ffffff;
        font-weight: bold;
    }
    QPushButton[btnClass="secondary"]:hover {
        background-color: #6c757d;
        border-color: #adb5bd;
        color: #ffffff;
    }
    QPushButton[btnClass="secondary"]:pressed {
        background-color: #3e444a;
        border: 1px solid #adb5bd;
        border-top: 2px solid #23272b;
        padding-top: 7px;
        padding-bottom: 3px;
        padding-left: 14px;
        padding-right: 10px;
        color: #e0e0e0;
    }

    QComboBox, QLineEdit, QListWidget, QTableWidget, QTextEdit {

        border: 1px solid #555555;
        border-radius: 4px;
        padding: 4px;
        background-color: #2b2b2b;
        color: #E0E0E0;
    }
    QComboBox QAbstractItemView {
        background-color: #2b2b2b;
        color: #E0E0E0;
        border: 1px solid #555555;
        selection-background-color: #2F65CA;
    }
    QListWidget::item:selected, QTableWidget::item:selected {
        background-color: #2F65CA;
        color: white;
    }
    QTabWidget::pane {
        border: 1px solid #555555;
        background: #2b2b2b;
    }
    QTabBar::tab {
        background: #3c3f41;
        border: 1px solid #555555;
        padding: 8px 16px;
        margin-right: 2px;
        border-top-left-radius: 5px;
        border-top-right-radius: 5px;
        color: #A0A0A0;
    }
    QTabBar::tab:selected {
        background: #2b2b2b;
        border-bottom-color: #2b2b2b;
        font-weight: bold;
        color: #82AAFF;
    }
    QHeaderView::section {
        background-color: #3c3f41;
        border: 1px solid #555555;
        padding: 4px;
        color: #E0E0E0;
    }
    QSlider::groove:horizontal {
        height: 6px;
        background: #444444;
        border-radius: 3px;
    }
    QSlider::sub-page:horizontal {
        background: #82AAFF;
        border-radius: 3px;
    }
    QSlider::handle:horizontal {
        background: #3c3f41;
        border: 2px solid #82AAFF;
        width: 16px;
        margin-top: -5px;
        margin-bottom: -5px;
        border-radius: 8px;
    }
    QSplitter::handle:horizontal {
        background-color: #444444;
        width: 7px;
        margin: 4px 1px;
        border-radius: 3px;
    }
    QSplitter::handle:horizontal:hover {
        background-color: #82AAFF;
    }
    QSplitter::handle:horizontal:pressed {
        background-color: #2F65CA;
    }
"""

class StatApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("통계 확률 분포 인터랙티브 시뮬레이션 및 데이터 분석 도구 (AlphaSpace)")
        self.resize(1280, 850)
        
        # 애플리케이션 아이콘 설정
        icon_file = resource_path("app_icon.ico")
        if os.path.exists(icon_file):
            self.setWindowIcon(QIcon(icon_file))
        
        # 시스템 기본 테마 최초 파악 및 초기화
        palette = QApplication.instance().palette()
        bg_color = palette.color(QPalette.Window)
        lightness = (bg_color.red() * 299 + bg_color.green() * 587 + bg_color.blue() * 114) / 1000
        is_dark = lightness < 128
        setup_matplotlib(is_dark)

        self.setup_menu_bar()

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)
        
        self.sim_tab = SimulationTab()
        self.fit_tab = FittingTab()
        self.hypo_tab = HypothesisTab()
        
        self.tabs.addTab(self.sim_tab, "📊 확률 분포 인터랙티브 시뮬레이션")
        self.tabs.addTab(self.fit_tab, "🎯 데이터 적합 (Data Fitting & Diagnostics)")
        self.tabs.addTab(self.hypo_tab, "🧪 가설 검정 및 통계 분석 (Hypothesis Testing)")

        # 사용자 화면 해상도에 맞춰 각 탭의 분할창(좌측 컨트롤 패널 / 우측 차트) 크기 최적화
        screen = QApplication.primaryScreen()
        avail_geo = screen.availableGeometry() if screen else None
        screen_w = avail_geo.width() if avail_geo else 1920
        left_w = max(480, min(680, int(screen_w * 0.27)))
        right_w = max(screen_w - left_w, 800)
        
        for tab in [self.sim_tab, self.fit_tab, self.hypo_tab]:
            if hasattr(tab, 'splitter'):
                tab.splitter.setCollapsible(0, False)
                tab.splitter.setCollapsible(1, False)
                tab.splitter.setSizes([left_w, right_w])
                tab.splitter.setStretchFactor(0, 0)
                tab.splitter.setStretchFactor(1, 1)

        # 상단 코너 위젯 (지식 허브 바로가기 + 테마 선택기)
        corner_widget = QWidget()
        corner_layout = QHBoxLayout(corner_widget)
        corner_layout.setContentsMargins(0, 0, 8, 0)
        corner_layout.setSpacing(8)
        
        self.btn_top_kb = QPushButton("📚 통계 지식 & 수식 사전")
        self.btn_top_kb.setProperty("btnClass", "primary")
        self.btn_top_kb.setCursor(Qt.PointingHandCursor)
        self.btn_top_kb.clicked.connect(self.open_global_knowledge_hub)
        corner_layout.addWidget(self.btn_top_kb)
        
        self.theme_lbl = QLabel("테마:")
        self.theme_lbl.setStyleSheet("font-weight: bold;")
        corner_layout.addWidget(self.theme_lbl)
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["시스템 기본", "라이트 모드", "다크 모드"])
        self.theme_combo.currentIndexChanged.connect(self.on_theme_changed)
        corner_layout.addWidget(self.theme_combo)
        
        self.tabs.setCornerWidget(corner_widget, Qt.TopRightCorner)

        # 시스템 기본 테마 최초 적용
        self.apply_theme("system")

    def setup_menu_bar(self):
        menubar = self.menuBar()
        
        # 파일 메뉴
        file_menu = menubar.addMenu("파일(&F)")
        act_exit = QAction("종료(&X)", self)
        act_exit.triggered.connect(self.close)
        file_menu.addAction(act_exit)
        
        # 지식 & 레퍼런스 메뉴
        kb_menu = menubar.addMenu("통계 지식 & 사전(&K)")
        
        act_kb = QAction("📚 통계 지식 & 수식 사전 열기 (Knowledge Hub)", self)
        act_kb.triggered.connect(self.open_global_knowledge_hub)
        kb_menu.addAction(act_kb)
        
        kb_menu.addSeparator()
        
        act_nist = QAction("🌐 NIST 공학 통계 핸드북 (NIST e-Handbook)", self)
        act_nist.triggered.connect(lambda: QDesktopServices.openUrl(QUrl("https://www.itl.nist.gov/div898/handbook/")))
        kb_menu.addAction(act_nist)
        
        act_scipy = QAction("🌐 SciPy 공식 통계 패키지 문서", self)
        act_scipy.triggered.connect(lambda: QDesktopServices.openUrl(QUrl("https://docs.scipy.org/doc/scipy/reference/stats.html")))
        kb_menu.addAction(act_scipy)
        
        # 정보 메뉴
        help_menu = menubar.addMenu("도움말(&H)")
        act_about = QAction("프로그램 정보(&A)", self)
        act_about.triggered.connect(self.show_about)
        help_menu.addAction(act_about)

    def open_global_knowledge_hub(self):
        dlg = KnowledgeHubDialog(self)
        dlg.exec()

    def show_about(self):
        QMessageBox.about(
            self,
            "프로그램 정보",
            "<h3>통계 확률 분포 및 분석 도구 (AlphaSpace)</h3>"
            "<p>21종 이상의 연속형/이산형 확률 분포 시뮬레이션, 실시간 모수 슬라이더, "
            "몬테카를로 표본 추출, 데이터 적합(AIC/BIC 랭킹 & Q-Q 플롯), "
            "유의수준 기각역 시각화 및 가설검정 리포트를 제공합니다.</p>"
            "<p><b>버전:</b> 2.0.0 (Interactive Edition)</p>"
        )

    def on_theme_changed(self, index):
        modes = ["system", "light", "dark"]
        self.apply_theme(modes[index])

    def apply_theme(self, mode):
        if mode == "system":
            palette = QApplication.instance().palette()
            bg_color = palette.color(QPalette.Window)
            lightness = (bg_color.red() * 299 + bg_color.green() * 587 + bg_color.blue() * 114) / 1000
            is_dark = lightness < 128
        elif mode == "dark":
            is_dark = True
        else:
            is_dark = False

        if is_dark:
            self.setStyleSheet(DARK_QSS)
            self.theme_lbl.setStyleSheet("font-weight: bold; color: #E0E0E0;")
        else:
            self.setStyleSheet(LIGHT_QSS)
            self.theme_lbl.setStyleSheet("font-weight: bold; color: #212529;")

        setup_matplotlib(is_dark)

        # 탭 내부 차트들 동적 테마 업데이트
        bg_col = '#2b2b2b' if is_dark else 'white'
        fg_col = '#E0E0E0' if is_dark else '#333333'
        grid_col = '#444444' if is_dark else '#D3D3D3'

        for i in range(self.tabs.count()):
            tab = self.tabs.widget(i)
            for fig_attr, canvas_attr in [('figure', 'canvas'), ('figure2', 'canvas2')]:
                if hasattr(tab, fig_attr) and hasattr(tab, canvas_attr):
                    fig = getattr(tab, fig_attr)
                    canvas = getattr(tab, canvas_attr)
                    fig.set_facecolor(bg_col)
                    for ax in fig.get_axes():
                        ax.set_facecolor(bg_col)
                        ax.tick_params(colors=fg_col, which='both')
                        ax.xaxis.label.set_color(fg_col)
                        ax.yaxis.label.set_color(fg_col)
                        ax.title.set_color(fg_col)
                        for spine in ax.spines.values():
                            spine.set_edgecolor(grid_col)
                        legend = ax.get_legend()
                        if legend:
                            for text in legend.get_texts():
                                text.set_color(fg_col)
                    canvas.draw()

if __name__ == "__main__":
    # Windows 작업 표시줄 전용 아이콘 매핑 ID 등록
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("AlphaSpace.StatisticsApp.2.0")
    except Exception:
        pass

    app = QApplication(sys.argv)
    
    icon_file = resource_path("app_icon.ico")
    if os.path.exists(icon_file):
        app.setWindowIcon(QIcon(icon_file))

    window = StatApp()
    window.showMaximized()
    sys.exit(app.exec())
