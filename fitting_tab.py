import io
import warnings
import numpy as np
import scipy.stats as stats
import pandas as pd

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QLineEdit, QPushButton, 
    QFormLayout, QGroupBox, QMessageBox, QRadioButton, QButtonGroup,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QScrollArea,
    QFrame, QGridLayout, QTabWidget, QSplitter, QTextEdit, QCheckBox,
    QDialog, QDialogButtonBox, QSpinBox, QDoubleSpinBox, QApplication
)
from PySide6.QtCore import Qt, QEvent, QUrl, QTimer
from PySide6.QtGui import QKeySequence, QDesktopServices, QColor, QFont
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from core_distributions import DISTRIBUTIONS, calculate_theoretical_stats
from knowledge_base import DISTRIBUTION_KNOWLEDGE, KnowledgeHubDialog
from utils import setup_matplotlib

# 실무 예제 데이터셋 정의
PRESET_DATASETS = {
    "부품 수명 시험 (Weibull, n=80)": lambda: np.round(stats.weibull_min.rvs(1.8, scale=120.0, size=80), 2),
    "표준 시험 성적 (Normal, n=100)": lambda: np.round(stats.norm.rvs(loc=72.5, scale=11.2, size=100), 1),
    "고객 대기시간 (Exponential, n=90)": lambda: np.round(stats.expon.rvs(scale=4.5, size=90), 2),
    "소득 및 매출 분포 (Lognormal, n=100)": lambda: np.round(stats.lognorm.rvs(0.6, scale=np.exp(3.5), size=100), 2),
    "일일 웹 요청수 (Poisson, n=60)": lambda: stats.poisson.rvs(mu=8.0, size=60),
    "주가 일일 수익률 (Student-t, n=120)": lambda: np.round(stats.t.rvs(df=4.0, loc=0.05, scale=1.5, size=120), 3),
    "고객 재구매 실패 전 건수 (Negative Binomial, n=80)": lambda: stats.nbinom.rvs(n=4, p=0.45, size=80),
    "정밀 센서 균일 노이즈 (Uniform, n=100)": lambda: np.round(stats.uniform.rvs(loc=-5.0, scale=10.0, size=100), 2)
}


class RandomSampleDialog(QDialog):
    """표본 시뮬레이션 및 검증용 무작위 데이터 생성 다이얼로그"""
    def __init__(self, parent=None, is_discrete=False):
        super().__init__(parent)
        self.setWindowTitle("🎲 무작위 검증 표본 생성기")
        self.resize(360, 240)
        self.is_discrete = is_discrete
        self.generated_data = None
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.dist_combo = QComboBox()
        if not self.is_discrete:
            self.dist_combo.addItem("정규분포 (Normal: μ, σ)", "norm")
            self.dist_combo.addItem("와이불분포 (Weibull: k, λ)", "weibull")
            self.dist_combo.addItem("지수분포 (Exponential: λ)", "expon")
            self.dist_combo.addItem("로그정규분포 (Lognormal: μ_log, σ_log)", "lognorm")
            self.dist_combo.addItem("균일분포 (Uniform: a, b)", "uniform")
        else:
            self.dist_combo.addItem("포아송분포 (Poisson: λ)", "poisson")
            self.dist_combo.addItem("이항분포 (Binomial: n, p)", "binom")
            self.dist_combo.addItem("음이항분포 (Negative Binomial: r, p)", "nbinom")

        self.param1 = QDoubleSpinBox()
        self.param1.setRange(-1000.0, 1000.0)
        self.param1.setValue(50.0)
        self.param1.setDecimals(2)

        self.param2 = QDoubleSpinBox()
        self.param2.setRange(0.01, 1000.0)
        self.param2.setValue(10.0)
        self.param2.setDecimals(2)

        self.lbl_p1 = QLabel("모수 1 (평균 μ / 형태 k):")
        self.lbl_p2 = QLabel("모수 2 (표준편차 σ / 척도 λ):")

        self.sample_size_spin = QSpinBox()
        self.sample_size_spin.setRange(10, 5000)
        self.sample_size_spin.setValue(100)

        form.addRow("분포 유형:", self.dist_combo)
        form.addRow(self.lbl_p1, self.param1)
        form.addRow(self.lbl_p2, self.param2)
        form.addRow("표본 크기 (N):", self.sample_size_spin)
        layout.addLayout(form)

        self.dist_combo.currentIndexChanged.connect(self.update_param_labels)
        self.update_param_labels()

        btn_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btn_box.accepted.connect(self.generate)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)

    def update_param_labels(self):
        d_type = self.dist_combo.currentData()
        if d_type == "norm":
            self.lbl_p1.setText("평균 (μ):")
            self.lbl_p2.setText("표준편차 (σ):")
            self.param1.setValue(50.0)
            self.param2.setValue(10.0)
            self.param2.setVisible(True)
            self.lbl_p2.setVisible(True)
        elif d_type == "weibull":
            self.lbl_p1.setText("형태모수 (k):")
            self.lbl_p2.setText("척도모수 (λ):")
            self.param1.setValue(1.8)
            self.param2.setValue(100.0)
            self.param2.setVisible(True)
            self.lbl_p2.setVisible(True)
        elif d_type == "expon":
            self.lbl_p1.setText("발생률 (λ = 1/평균):")
            self.param1.setValue(0.2)
            self.lbl_p2.setVisible(False)
            self.param2.setVisible(False)
        elif d_type == "lognorm":
            self.lbl_p1.setText("로그평균 (μ_log):")
            self.lbl_p2.setText("로그표준편차 (σ_log):")
            self.param1.setValue(3.0)
            self.param2.setValue(0.5)
            self.param2.setVisible(True)
            self.lbl_p2.setVisible(True)
        elif d_type == "uniform":
            self.lbl_p1.setText("최소값 (a):")
            self.lbl_p2.setText("최대값 (b):")
            self.param1.setValue(0.0)
            self.param2.setValue(100.0)
            self.param2.setVisible(True)
            self.lbl_p2.setVisible(True)
        elif d_type == "poisson":
            self.lbl_p1.setText("평균 발생률 (λ):")
            self.param1.setValue(6.0)
            self.lbl_p2.setVisible(False)
            self.param2.setVisible(False)
        elif d_type == "binom":
            self.lbl_p1.setText("시행 횟수 (n):")
            self.lbl_p2.setText("성공 확률 (p):")
            self.param1.setValue(20.0)
            self.param2.setValue(0.4)
            self.param2.setVisible(True)
            self.lbl_p2.setVisible(True)
        elif d_type == "nbinom":
            self.lbl_p1.setText("목표 성공수 (r):")
            self.lbl_p2.setText("성공 확률 (p):")
            self.param1.setValue(5.0)
            self.param2.setValue(0.5)
            self.param2.setVisible(True)
            self.lbl_p2.setVisible(True)

    def generate(self):
        d_type = self.dist_combo.currentData()
        n = self.sample_size_spin.value()
        p1 = self.param1.value()
        p2 = self.param2.value()

        if d_type == "norm":
            self.generated_data = np.round(stats.norm.rvs(loc=p1, scale=max(p2, 1e-3), size=n), 2)
        elif d_type == "weibull":
            self.generated_data = np.round(stats.weibull_min.rvs(max(p1, 0.1), scale=max(p2, 1e-3), size=n), 2)
        elif d_type == "expon":
            scale = 1.0 / max(p1, 1e-4)
            self.generated_data = np.round(stats.expon.rvs(scale=scale, size=n), 2)
        elif d_type == "lognorm":
            self.generated_data = np.round(stats.lognorm.rvs(max(p2, 0.01), scale=np.exp(p1), size=n), 2)
        elif d_type == "uniform":
            low, high = min(p1, p2), max(p1, p2)
            self.generated_data = np.round(stats.uniform.rvs(loc=low, scale=max(high - low, 1e-3), size=n), 2)
        elif d_type == "poisson":
            self.generated_data = stats.poisson.rvs(mu=max(p1, 0.1), size=n)
        elif d_type == "binom":
            self.generated_data = stats.binom.rvs(n=int(max(p1, 1)), p=min(max(p2, 0.01), 0.99), size=n)
        elif d_type == "nbinom":
            self.generated_data = stats.nbinom.rvs(n=int(max(p1, 1)), p=min(max(p2, 0.01), 0.99), size=n)

        self.accept()


class FittingTab(QWidget):
    def __init__(self):
        super().__init__()
        setup_matplotlib()
        self.fitted_results = []
        self.current_dist_key = None
        self.current_params = None
        self.current_dist_obj = None
        
        self.data_debounce_timer = QTimer(self)
        self.data_debounce_timer.setSingleShot(True)
        self.data_debounce_timer.setInterval(200)
        self.data_debounce_timer.timeout.connect(self.on_data_changed_debounced)
        
        self.is_syncing_data = False
        self.is_selecting_dist = False
        self.is_updating_mode = False

        self.setup_ui()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setFrameShape(QFrame.NoFrame)
        left_scroll.setMinimumWidth(320)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(12)
        left_layout.setContentsMargins(4, 4, 8, 4)
        
        # 1단계: 원본 데이터 입력 및 기술통계 요약
        data_group = QGroupBox("1. 원본 데이터 입력 및 기술통계 요약")
        data_layout = QVBoxLayout()
        data_layout.setSpacing(8)
        
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("샘플 프리셋:"))
        self.preset_combo = QComboBox()
        self.preset_combo.setMinimumWidth(100)
        self.preset_combo.setSizeAdjustPolicy(QComboBox.AdjustToContentsOnFirstShow)
        self.preset_combo.addItem("-- 실무 예제 데이터셋 선택 --", None)
        for p_name in PRESET_DATASETS.keys():
            self.preset_combo.addItem(p_name, p_name)
        self.preset_combo.currentIndexChanged.connect(self.load_preset_data)
        preset_layout.addWidget(self.preset_combo, stretch=1)
        data_layout.addLayout(preset_layout)
        
        action_btn_layout = QGridLayout()
        action_btn_layout.setSpacing(6)
        self.btn_load_file = QPushButton("📂 파일 열기")
        self.btn_load_file.setToolTip("Excel(.xlsx), CSV, TXT 파일을 불러옵니다.")
        self.btn_load_file.setCursor(Qt.PointingHandCursor)
        self.btn_load_file.clicked.connect(self.load_data_file)
        
        self.btn_gen_sample = QPushButton("🎲 표본 생성")
        self.btn_gen_sample.setToolTip("테스트 및 검증을 위해 특정 분포의 난수를 생성합니다.")
        self.btn_gen_sample.setCursor(Qt.PointingHandCursor)
        self.btn_gen_sample.clicked.connect(self.open_sample_generator)
        
        self.btn_filter_outliers = QPushButton("🧹 이상치 제거")
        self.btn_filter_outliers.setToolTip("IQR 1.5 기준의 이상치를 탐지하여 제거합니다.")
        self.btn_filter_outliers.setCursor(Qt.PointingHandCursor)
        self.btn_filter_outliers.clicked.connect(self.remove_outliers)
        
        self.btn_clear_data = QPushButton("🗑️ 비우기")
        self.btn_clear_data.setCursor(Qt.PointingHandCursor)
        self.btn_clear_data.clicked.connect(self.clear_data)
        
        action_btn_layout.addWidget(self.btn_load_file, 0, 0)
        action_btn_layout.addWidget(self.btn_gen_sample, 0, 1)
        action_btn_layout.addWidget(self.btn_filter_outliers, 1, 0)
        action_btn_layout.addWidget(self.btn_clear_data, 1, 1)
        data_layout.addLayout(action_btn_layout)
        
        self.data_input_tabs = QTabWidget()
        tab_table = QWidget()
        tab_table_layout = QVBoxLayout(tab_table)
        tab_table_layout.setContentsMargins(0, 4, 0, 0)
        
        self.data_table = QTableWidget(0, 1)
        self.data_table.setHorizontalHeaderLabels(["표본 데이터 (X)"])
        self.data_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.data_table.setMinimumHeight(110)
        self.data_table.setMaximumHeight(240)
        self.data_table.installEventFilter(self)
        self.data_table.itemChanged.connect(self.on_table_item_changed)
        tab_table_layout.addWidget(self.data_table)
        
        table_row_btns = QHBoxLayout()
        self.btn_add_row = QPushButton("➕ 행 추가")
        self.btn_add_row.setCursor(Qt.PointingHandCursor)
        self.btn_add_row.clicked.connect(self.add_table_row)
        self.btn_del_row = QPushButton("➖ 선택 삭제")
        self.btn_del_row.setCursor(Qt.PointingHandCursor)
        self.btn_del_row.clicked.connect(self.delete_selected_data)
        self.btn_paste_table = QPushButton("📋 붙여넣기")
        self.btn_paste_table.setCursor(Qt.PointingHandCursor)
        self.btn_paste_table.clicked.connect(self.paste_data)
        table_row_btns.addWidget(self.btn_add_row)
        table_row_btns.addWidget(self.btn_del_row)
        table_row_btns.addWidget(self.btn_paste_table)
        tab_table_layout.addLayout(table_row_btns)
        
        tab_text = QWidget()
        tab_text_layout = QVBoxLayout(tab_text)
        tab_text_layout.setContentsMargins(0, 4, 0, 0)
        
        self.data_text_edit = QTextEdit()
        self.data_text_edit.setPlaceholderText("숫자 데이터를 쉼표(,), 줄바꿈, 탭, 공백 등으로 자유롭게 붙여넣으세요.\n예: 12.5, 14.2, 11.8, 15.6 ...")
        self.data_text_edit.setMinimumHeight(110)
        self.data_text_edit.setMaximumHeight(240)
        self.data_text_edit.textChanged.connect(self.on_text_edit_changed)
        tab_text_layout.addWidget(self.data_text_edit)
        
        self.data_input_tabs.addTab(tab_table, "📋 스프레드시트 표")
        self.data_input_tabs.addTab(tab_text, "✍️ 텍스트 직접 입력")
        self.data_input_tabs.currentChanged.connect(self.on_input_tab_switched)
        data_layout.addWidget(self.data_input_tabs)
        
        stats_frame = QFrame()
        stats_frame.setStyleSheet("QFrame { background-color: rgba(13, 110, 253, 0.05); border: 1px dashed #b6d4fe; border-radius: 4px; padding: 4px; }")
        stats_layout = QGridLayout(stats_frame)
        stats_layout.setSpacing(4)
        
        self.lbl_n = QLabel("0")
        self.lbl_mean = QLabel("-")
        self.lbl_std = QLabel("-")
        self.lbl_median = QLabel("-")
        self.lbl_iqr = QLabel("-")
        self.lbl_minmax = QLabel("-")
        self.lbl_skew = QLabel("-")
        self.lbl_kurt = QLabel("-")
        
        for lbl in [self.lbl_n, self.lbl_mean, self.lbl_std, self.lbl_median, 
                    self.lbl_iqr, self.lbl_minmax, self.lbl_skew, self.lbl_kurt]:
            lbl.setStyleSheet("font-weight: bold; color: #0d6efd;")
            
        stats_layout.addWidget(QLabel("표본수 (N):"), 0, 0)
        stats_layout.addWidget(self.lbl_n, 0, 1)
        stats_layout.addWidget(QLabel("표본평균 (X̄):"), 0, 2)
        stats_layout.addWidget(self.lbl_mean, 0, 3)
        
        stats_layout.addWidget(QLabel("표준편차 (s):"), 1, 0)
        stats_layout.addWidget(self.lbl_std, 1, 1)
        stats_layout.addWidget(QLabel("중앙값 (Med):"), 1, 2)
        stats_layout.addWidget(self.lbl_median, 1, 3)
        
        stats_layout.addWidget(QLabel("사분위 (IQR):"), 2, 0)
        stats_layout.addWidget(self.lbl_iqr, 2, 1)
        stats_layout.addWidget(QLabel("표본왜도:"), 2, 2)
        stats_layout.addWidget(self.lbl_skew, 2, 3)
        
        stats_layout.addWidget(QLabel("표본첨도:"), 3, 0)
        stats_layout.addWidget(self.lbl_kurt, 3, 1)
        stats_layout.addWidget(QLabel("범위:"), 3, 2)
        stats_layout.addWidget(self.lbl_minmax, 3, 3)
        
        data_layout.addWidget(stats_frame)
        data_group.setLayout(data_layout)
        left_layout.addWidget(data_group)

        # 2단계: 적합 모드 및 대상 분포 모형 선택
        model_group = QGroupBox("2. 적합 모드 및 대상 분포 모형 선택")
        model_layout = QVBoxLayout()
        model_layout.setSpacing(8)
        
        type_form = QFormLayout()
        type_form.setSpacing(6)
        self.fit_type_combo = QComboBox()
        self.fit_type_combo.setMinimumWidth(100)
        self.fit_type_combo.setSizeAdjustPolicy(QComboBox.AdjustToContentsOnFirstShow)
        self.fit_type_combo.addItem("연속형 데이터 (Continuous)", "continuous")
        self.fit_type_combo.addItem("이산형 데이터 (Discrete)", "discrete")
        self.fit_type_combo.currentIndexChanged.connect(self.on_fit_type_changed)
        type_form.addRow("데이터 유형:", self.fit_type_combo)
        model_layout.addLayout(type_form)
        
        mode_box = QGroupBox("적합 방식 선택:")
        mode_box.setStyleSheet("QGroupBox { font-size: 9.5pt; margin-top: 4px; padding-top: 6px; }")
        mode_box_layout = QVBoxLayout(mode_box)
        mode_box_layout.setSpacing(4)
        
        self.radio_mode_auto = QRadioButton("🏆 전체 후보 자동 비교 (Auto Best Fit)")
        self.radio_mode_target = QRadioButton("🎯 특정 분포 맞춤 적합 (Target Fit)")
        self.radio_mode_auto.setChecked(True)
        
        self.mode_btn_group = QButtonGroup()
        self.mode_btn_group.addButton(self.radio_mode_auto, 0)
        self.mode_btn_group.addButton(self.radio_mode_target, 1)
        self.mode_btn_group.buttonToggled.connect(self.on_fit_mode_changed)
        
        mode_box_layout.addWidget(self.radio_mode_auto)
        mode_box_layout.addWidget(self.radio_mode_target)
        model_layout.addWidget(mode_box)
        
        dist_form = QFormLayout()
        dist_form.setSpacing(6)
        self.fit_dist_combo = QComboBox()
        self.fit_dist_combo.setMinimumWidth(100)
        self.fit_dist_combo.setSizeAdjustPolicy(QComboBox.AdjustToContentsOnFirstShow)
        self.fit_dist_combo.currentIndexChanged.connect(self.on_dist_combo_selected)
        dist_form.addRow("대상 모형:", self.fit_dist_combo)
        model_layout.addLayout(dist_form)
        
        kb_btn_layout = QHBoxLayout()
        self.btn_kb = QPushButton("📚 지식 & 수식 사전")
        self.btn_kb.setProperty("btnClass", "primary")
        self.btn_kb.setCursor(Qt.PointingHandCursor)
        self.btn_kb.clicked.connect(self.open_knowledge_hub)
        kb_btn_layout.addWidget(self.btn_kb)
        
        self.btn_web = QPushButton("🌐 웹 레퍼런스")
        self.btn_web.setProperty("btnClass", "success")
        self.btn_web.setCursor(Qt.PointingHandCursor)
        self.btn_web.clicked.connect(self.open_web_reference)
        kb_btn_layout.addWidget(self.btn_web)
        model_layout.addLayout(kb_btn_layout)
        
        model_group.setLayout(model_layout)
        left_layout.addWidget(model_group)

        # 3단계: 적합 실행 및 모드별 동적 피팅 제어
        fit_ctrl_group = QGroupBox("3. 분포 적합 실행 및 실시간 연동")
        fit_ctrl_layout = QVBoxLayout()
        fit_ctrl_layout.setSpacing(8)
        
        self.fit_guide_card = QFrame()
        self.fit_guide_card.setStyleSheet("QFrame { background-color: #f8f9fa; border: 1px solid #ced4da; border-radius: 5px; padding: 6px; }")
        guide_layout = QVBoxLayout(self.fit_guide_card)
        guide_layout.setContentsMargins(4, 4, 4, 4)
        guide_layout.setSpacing(2)
        
        self.lbl_fit_guide_title = QLabel("💡 <b>실행 방식 안내:</b>")
        self.lbl_fit_guide_title.setStyleSheet("color: #0d6efd; font-size: 9.5pt;")
        self.lbl_fit_guide_desc = QLabel("모든 후보 분포를 적합하여 AIC/BIC 기준 1위 최적 분포를 자동으로 찾아냅니다.")
        self.lbl_fit_guide_desc.setStyleSheet("color: #495057; font-size: 9pt;")
        self.lbl_fit_guide_desc.setWordWrap(True)
        guide_layout.addWidget(self.lbl_fit_guide_title)
        guide_layout.addWidget(self.lbl_fit_guide_desc)
        fit_ctrl_layout.addWidget(self.fit_guide_card)
        
        self.btn_fit = QPushButton("🚀 최적 분포 탐색 및 적합 실행")
        self.btn_fit.setProperty("btnClass", "success")
        self.btn_fit.setCursor(Qt.PointingHandCursor)
        self.btn_fit.setMinimumHeight(38)
        self.btn_fit.clicked.connect(self.fit_data)
        fit_ctrl_layout.addWidget(self.btn_fit)
        
        auto_fit_layout = QVBoxLayout()
        auto_fit_layout.setSpacing(3)
        self.chk_auto_fit = QCheckBox("⚡ 데이터/모형 변경 시 실시간 자동 반영")
        self.chk_auto_fit.setChecked(True)
        self.chk_auto_fit.setStyleSheet("font-weight: bold; color: #198754;")
        auto_fit_layout.addWidget(self.chk_auto_fit)
        
        self.lbl_fit_status = QLabel("대기 중")
        self.lbl_fit_status.setStyleSheet("font-size: 8.5pt; color: #6c757d; font-weight: bold;")
        self.lbl_fit_status.setWordWrap(True)
        auto_fit_layout.addWidget(self.lbl_fit_status)
        fit_ctrl_layout.addLayout(auto_fit_layout)
        
        fit_ctrl_group.setLayout(fit_ctrl_layout)
        left_layout.addWidget(fit_ctrl_group)

        # 4단계: 분포 적합도 비교 순위 (Goodness-of-Fit Ranking)
        rank_group = QGroupBox("4. 후보 분포 적합도 비교 순위 (Goodness-of-Fit Ranking)")
        rank_layout = QVBoxLayout()
        rank_layout.setSpacing(4)
        
        self.rank_table = QTableWidget(0, 6)
        self.rank_table.setHorizontalHeaderLabels(["순위", "분포명", "AIC", "BIC", "검정 p값", "적합 판정"])
        self.rank_table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        self.rank_table.horizontalHeader().setStretchLastSection(False)
        self.rank_table.setColumnWidth(0, 42)
        self.rank_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.rank_table.setColumnWidth(2, 60)
        self.rank_table.setColumnWidth(3, 60)
        self.rank_table.setColumnWidth(4, 72)
        self.rank_table.setColumnWidth(5, 75)
        self.rank_table.setMinimumHeight(120)
        self.rank_table.setMaximumHeight(260)
        self.rank_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.rank_table.setSelectionMode(QTableWidget.SingleSelection)
        self.rank_table.itemSelectionChanged.connect(self.on_rank_row_selected)
        rank_layout.addWidget(self.rank_table)
        
        rank_hint = QLabel("💡 순위표 행을 클릭하면 해당 분포로 즉시 차트가 전환됩니다.")
        rank_hint.setStyleSheet("color: #6c757d; font-size: 8pt;")
        rank_hint.setWordWrap(True)
        rank_layout.addWidget(rank_hint)
        
        rank_group.setLayout(rank_layout)
        left_layout.addWidget(rank_group)

        # 5단계: 적합 모델 기반 확률/분위수 계산기
        calc_outer_group = QGroupBox("5. 적합 모델 기반 확률 및 분위수 계산기")
        calc_outer_layout = QVBoxLayout()
        calc_outer_layout.setSpacing(6)
        
        dir_layout = QHBoxLayout()
        self.radio_less = QRadioButton("이하 (X ≤ x)")
        self.radio_less.setChecked(True)
        self.radio_greater = QRadioButton("이상 (X ≥ x)")
        self.radio_equal = QRadioButton("같다 (X = x)")
        
        self.dir_group = QButtonGroup()
        self.dir_group.addButton(self.radio_less, id=0)
        self.dir_group.addButton(self.radio_greater, id=1)
        self.dir_group.addButton(self.radio_equal, id=2)
        self.dir_group.buttonClicked.connect(lambda: self.plot_fitted_chart())
        
        dir_layout.addWidget(self.radio_less)
        dir_layout.addWidget(self.radio_greater)
        dir_layout.addWidget(self.radio_equal)
        calc_outer_layout.addLayout(dir_layout)
        
        calc_form = QFormLayout()
        calc_form.setSpacing(6)
        
        calc_x_layout = QHBoxLayout()
        self.calc_val_x = QLineEdit()
        self.calc_val_x.setPlaceholderText("X 값 (예: 50.0)")
        self.calc_val_x.textChanged.connect(self.on_calc_x_changed)
        calc_x_layout.addWidget(self.calc_val_x)
        
        self.btn_reset_x = QPushButton("초기화")
        self.btn_reset_x.setCursor(Qt.PointingHandCursor)
        self.btn_reset_x.clicked.connect(lambda: self.calc_val_x.clear())
        calc_x_layout.addWidget(self.btn_reset_x)
        calc_form.addRow("X 값 (x):", calc_x_layout)
        
        calc_p_layout = QHBoxLayout()
        self.calc_val_p = QLineEdit()
        self.calc_val_p.setPlaceholderText("누적확률 (0~1, 예: 0.95)")
        self.calc_val_p.textChanged.connect(self.on_calc_p_changed)
        calc_p_layout.addWidget(self.calc_val_p)
        
        self.btn_reset_p = QPushButton("초기화")
        self.btn_reset_p.setCursor(Qt.PointingHandCursor)
        self.btn_reset_p.clicked.connect(lambda: self.calc_val_p.clear())
        calc_p_layout.addWidget(self.btn_reset_p)
        calc_form.addRow("누적 확률 (p):", calc_p_layout)
        
        calc_outer_layout.addLayout(calc_form)
        
        res_box = QHBoxLayout()
        res_box.addWidget(QLabel("계산 결과:"))
        self.lbl_calc_result = QLabel("-")
        self.lbl_calc_result.setStyleSheet("font-weight: bold; color: #198754; font-size: 10pt;")
        res_box.addWidget(self.lbl_calc_result, stretch=1)
        calc_outer_layout.addLayout(res_box)
        
        calc_outer_group.setLayout(calc_outer_layout)
        left_layout.addWidget(calc_outer_group)
        
        left_layout.addStretch()
        left_scroll.setWidget(left_panel)
        self.splitter.addWidget(left_scroll)
        
        # 우측 패널
        right_panel = QWidget()
        right_panel.setMinimumWidth(350)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(6, 4, 6, 4)
        right_layout.setSpacing(6)
        
        self.active_model_card = QFrame()
        self.active_model_card.setStyleSheet(
            "QFrame { background-color: rgba(13, 110, 253, 0.08); border: 1px solid #9ec5fe; border-radius: 5px; padding: 6px; }"
        )
        badge_layout = QHBoxLayout(self.active_model_card)
        badge_layout.setContentsMargins(8, 4, 8, 4)
        self.lbl_active_model_badge = QLabel("🎯 <b>현재 차트 모델:</b> 분석 대기 중")
        self.lbl_active_model_badge.setStyleSheet("font-size: 10.5pt; color: #084298;")
        self.lbl_active_model_badge.setWordWrap(True)
        badge_layout.addWidget(self.lbl_active_model_badge)
        right_layout.addWidget(self.active_model_card)
        
        diag_toolbar = QVBoxLayout()
        diag_toolbar.setSpacing(4)
        
        diag_row1 = QHBoxLayout()
        diag_row1.addWidget(QLabel("<b>진단 시각화:</b>"))
        
        self.diag_combo = QComboBox()
        self.diag_combo.setMinimumWidth(150)
        self.diag_combo.setSizeAdjustPolicy(QComboBox.AdjustToContentsOnFirstShow)
        self.diag_combo.addItems([
            "1. 📊 히스토그램 vs 적합 확률분포 (PDF/PMF)",
            "2. 📈 누적분포함수 비교 (ECDF vs 이론 CDF)",
            "3. 🎯 Q-Q 플롯 (Quantile-Quantile Plot)",
            "4. 🔍 P-P 플롯 (Probability-Probability Plot)",
            "5. 📉 적합 잔차 분석 (Residuals Plot)"
        ])
        self.diag_combo.currentIndexChanged.connect(lambda: self.plot_fitted_chart())
        diag_row1.addWidget(self.diag_combo, stretch=1)
        
        self.btn_copy_chart = QPushButton("📋 복사")
        self.btn_copy_chart.setProperty("btnClass", "secondary")
        self.btn_copy_chart.setCursor(Qt.PointingHandCursor)
        self.btn_copy_chart.setToolTip("차트 이미지를 클립보드에 복사합니다.")
        self.btn_copy_chart.clicked.connect(self.copy_chart_to_clipboard)
        diag_row1.addWidget(self.btn_copy_chart)
        
        self.btn_export_fit = QPushButton("💾 저장")
        self.btn_export_fit.setProperty("btnClass", "secondary")
        self.btn_export_fit.setCursor(Qt.PointingHandCursor)
        self.btn_export_fit.setToolTip("고해상도 이미지(PNG, JPG, PDF)로 차트를 저장합니다.")
        self.btn_export_fit.clicked.connect(self.export_chart)
        self.btn_export_fit.setEnabled(False)
        diag_row1.addWidget(self.btn_export_fit)
        diag_toolbar.addLayout(diag_row1)
        
        diag_row2 = QHBoxLayout()
        self.chk_overlay_top3 = QCheckBox("🎨 상위 3개 분포 오버레이 비교")
        self.chk_overlay_top3.setToolTip("히스토그램 위에 1위~3위 최적 분포 곡선을 함께 표시하여 비교합니다.")
        self.chk_overlay_top3.stateChanged.connect(lambda: self.plot_fitted_chart())
        diag_row2.addWidget(self.chk_overlay_top3)
        
        self.chk_show_kde = QCheckBox("경험적 KDE 표시")
        self.chk_show_kde.setToolTip("표본 데이터의 비모수적 커널 밀도 추정(KDE) 선을 함께 표시합니다.")
        self.chk_show_kde.stateChanged.connect(lambda: self.plot_fitted_chart())
        diag_row2.addWidget(self.chk_show_kde)
        diag_row2.addStretch()
        diag_toolbar.addLayout(diag_row2)
        
        right_layout.addLayout(diag_toolbar)
        
        self.figure2 = Figure(tight_layout=True)
        self.figure = self.figure2
        self.canvas2 = FigureCanvas(self.figure2)
        self.canvas = self.canvas2
        right_layout.addWidget(self.canvas2, stretch=1)
        
        self.fit_result_card = QGroupBox("📌 선택 적합 모델 상세 추정 결과 및 통계적 검정")
        self.fit_result_card.setMinimumHeight(115)
        fit_card_layout = QGridLayout(self.fit_result_card)
        fit_card_layout.setSpacing(6)
        
        self.lbl_best_dist = QLabel("분석 대기 중")
        self.lbl_best_dist.setStyleSheet("font-weight: bold; color: #0d6efd; font-size: 11pt;")
        self.lbl_best_dist.setWordWrap(True)
        
        self.lbl_best_params = QLabel("-")
        self.lbl_best_params.setStyleSheet("font-family: Consolas, monospace; font-weight: bold; color: #198754;")
        self.lbl_best_params.setWordWrap(True)
        
        self.lbl_best_stats = QLabel("-")
        self.lbl_best_stats.setStyleSheet("font-family: Consolas, monospace; font-size: 9.5pt;")
        self.lbl_best_stats.setWordWrap(True)
        
        self.lbl_best_gof = QLabel("-")
        self.lbl_best_gof.setStyleSheet("font-weight: bold;")
        self.lbl_best_gof.setWordWrap(True)
        
        fit_card_layout.addWidget(QLabel("선택 적합 모형:"), 0, 0)
        fit_card_layout.addWidget(self.lbl_best_dist, 0, 1)
        fit_card_layout.addWidget(QLabel("추정 모수 (MLE):"), 0, 2)
        fit_card_layout.addWidget(self.lbl_best_params, 0, 3)
        
        fit_card_layout.addWidget(QLabel("적합도 지수 (AIC/BIC):"), 1, 0)
        fit_card_layout.addWidget(self.lbl_best_gof, 1, 1)
        fit_card_layout.addWidget(QLabel("이론 통계량 (평균/분산):"), 1, 2)
        fit_card_layout.addWidget(self.lbl_best_stats, 1, 3)
        
        right_layout.addWidget(self.fit_result_card)
        
        self.splitter.addWidget(right_panel)
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)
        self.splitter.setSizes([480, 800])
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        main_layout.addWidget(self.splitter)
        
        self.on_fit_type_changed()
        self.preset_combo.setCurrentIndex(1)

    def on_input_tab_switched(self, index):
        """표 편집기와 텍스트 입력창 간 데이터 상호 동기화"""
        if self.is_syncing_data: return
        self.is_syncing_data = True
        try:
            if index == 1:  # 텍스트 탭으로 전환: 표의 데이터를 텍스트로 반영
                raw = self.get_raw_data()
                text = ", ".join(f"{x:g}" for x in raw)
                self.data_text_edit.setPlainText(text)
            else:  # 표 탭으로 전환: 텍스트의 데이터를 표로 반영
                raw = self.parse_text_data(self.data_text_edit.toPlainText())
                self.set_table_data(raw, trigger_fit=False)
        finally:
            self.is_syncing_data = False

    def parse_text_data(self, text):
        """쉼표, 공백, 줄바꿈으로 구분된 텍스트를 float 리스트로 파싱"""
        if not text: return []
        cleaned = text.replace(',', ' ').replace('\t', ' ').replace('\n', ' ')
        tokens = cleaned.split()
        data = []
        for t in tokens:
            try:
                data.append(float(t))
            except ValueError:
                pass
        return data

    def on_table_item_changed(self, item):
        """스프레드시트 표의 셀이 수정되었을 때 반응"""
        if self.is_syncing_data: return
        self.trigger_data_change()

    def on_text_edit_changed(self):
        """텍스트 입력창이 수정되었을 때 반응"""
        if self.is_syncing_data: return
        self.trigger_data_change()

    def trigger_data_change(self):
        """데이터 변경 이벤트 수신 -> 기술통계 즉각 갱신 & 피팅 디바운스 시작"""
        self.update_sample_summary()
        if self.chk_auto_fit.isChecked():
            self.lbl_fit_status.setText("⏳ 변경 감지 (적합 준비 중...)")
            self.data_debounce_timer.start()
        else:
            self.lbl_fit_status.setText("⚠️ 데이터 변경됨 (적합 실행 필요)")

    def on_data_changed_debounced(self):
        """디바운스 타이머 종료 후 실제 적합 및 차트 갱신 수행"""
        data = self.get_raw_data()
        if len(data) >= 3:
            self.fit_data()
        else:
            self.ax2_clear()
            self.lbl_fit_status.setText("데이터 부족 (최소 3개 필요)")

    def get_raw_data(self):
        """현재 활성화된 입력 탭에 따라 순수 숫자 데이터를 추출"""
        curr_tab = self.data_input_tabs.currentIndex()
        if curr_tab == 1 and not self.is_syncing_data:
            return np.array(self.parse_text_data(self.data_text_edit.toPlainText()), dtype=float)
        
        data = []
        for row in range(self.data_table.rowCount()):
            item = self.data_table.item(row, 0)
            if item and item.text().strip():
                try:
                    data.append(float(item.text().strip()))
                except ValueError:
                    pass
        return np.array(data, dtype=float)

    def set_table_data(self, data_list, trigger_fit=True):
        """표 데이터를 설정하고 필요한 경우 자동 적합 트리거"""
        self.is_syncing_data = True
        self.data_table.blockSignals(True)
        self.data_table.setUpdatesEnabled(False)
        self.data_table.setRowCount(len(data_list))
        for i, val in enumerate(data_list):
            item = QTableWidgetItem(f"{val:g}" if isinstance(val, (int, float, np.number)) else str(val))
            item.setTextAlignment(Qt.AlignCenter)
            self.data_table.setItem(i, 0, item)
        self.data_table.setUpdatesEnabled(True)
        self.data_table.blockSignals(False)
        
        # 텍스트 창도 동기화
        text = ", ".join(f"{x:g}" for x in data_list)
        self.data_text_edit.blockSignals(True)
        self.data_text_edit.setPlainText(text)
        self.data_text_edit.blockSignals(False)
        
        self.is_syncing_data = False
        self.update_sample_summary()
        
        if trigger_fit:
            if self.chk_auto_fit.isChecked():
                self.fit_data()
            else:
                self.lbl_fit_status.setText("⚠️ 데이터 변경됨 (적합 실행 필요)")

    def add_table_row(self):
        row = self.data_table.rowCount()
        self.data_table.insertRow(row)
        item = QTableWidgetItem("")
        item.setTextAlignment(Qt.AlignCenter)
        self.data_table.setItem(row, 0, item)
        self.data_table.editItem(item)

    def delete_selected_data(self):
        selected_rows = sorted(set(idx.row() for idx in self.data_table.selectedIndexes()), reverse=True)
        if not selected_rows: return
        self.is_syncing_data = True
        for row in selected_rows:
            self.data_table.removeRow(row)
        self.is_syncing_data = False
        self.trigger_data_change()

    def paste_data(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if not text: return
        parsed = self.parse_text_data(text)
        if not parsed: return
        
        current_data = list(self.get_raw_data())
        current_data.extend(parsed)
        self.set_table_data(current_data, trigger_fit=self.chk_auto_fit.isChecked())

    def clear_data(self):
        self.is_syncing_data = True
        self.data_table.blockSignals(True)
        self.data_table.setRowCount(0)
        self.data_table.blockSignals(False)
        
        self.data_text_edit.blockSignals(True)
        self.data_text_edit.clear()
        self.data_text_edit.blockSignals(False)
        self.is_syncing_data = False
        
        self.fitted_results = []
        self.current_dist_key = None
        self.current_params = None
        self.current_dist_obj = None
        
        self.ax2_clear()
        self.lbl_n.setText("0")
        self.lbl_mean.setText("-")
        self.lbl_std.setText("-")
        self.lbl_median.setText("-")
        self.lbl_iqr.setText("-")
        self.lbl_minmax.setText("-")
        self.lbl_skew.setText("-")
        self.lbl_kurt.setText("-")
        
        self.lbl_best_dist.setText("분석 대기 중")
        self.lbl_best_params.setText("-")
        self.lbl_best_gof.setText("-")
        self.lbl_best_stats.setText("-")
        self.lbl_calc_result.setText("-")
        
        self.rank_table.setRowCount(0)
        self.btn_export_fit.setEnabled(False)
        self.lbl_fit_status.setText("데이터가 비워졌습니다")
        if hasattr(self, 'lbl_active_model_badge'):
            self.lbl_active_model_badge.setText("🎯 <b>현재 차트 모델:</b> 분석 대기 중")

    def update_sample_summary(self):
        data = self.get_raw_data()
        n = len(data)
        self.lbl_n.setText(str(n))
        if n >= 2:
            mean_val = float(np.mean(data))
            std_val = float(np.std(data, ddof=1))
            med_val = float(np.median(data))
            q25, q75 = np.percentile(data, [25, 75])
            iqr_val = float(q75 - q25)
            min_val, max_val = float(np.min(data)), float(np.max(data))
            skew_val = float(stats.skew(data))
            kurt_val = float(stats.kurtosis(data))
            
            self.lbl_mean.setText(f"{mean_val:.3f}")
            self.lbl_std.setText(f"{std_val:.3f}")
            self.lbl_median.setText(f"{med_val:.3f}")
            self.lbl_iqr.setText(f"{iqr_val:.3f}")
            self.lbl_minmax.setText(f"{min_val:.2f} ~ {max_val:.2f}")
            self.lbl_skew.setText(f"{skew_val:.3f}")
            self.lbl_kurt.setText(f"{kurt_val:.3f}")
        else:
            self.lbl_mean.setText("-")
            self.lbl_std.setText("-")
            self.lbl_median.setText("-")
            self.lbl_iqr.setText("-")
            self.lbl_minmax.setText("-")
            self.lbl_skew.setText("-")
            self.lbl_kurt.setText("-")

    def remove_outliers(self):
        """IQR 1.5 기준 이상치 필터링"""
        data = self.get_raw_data()
        if len(data) < 4:
            QMessageBox.information(self, "안내", "이상치 필터링을 위해 최소 4개 이상의 데이터가 필요합니다.")
            return
        
        q25, q75 = np.percentile(data, [25, 75])
        iqr = q75 - q25
        lower = q25 - 1.5 * iqr
        upper = q75 + 1.5 * iqr
        
        cleaned = data[(data >= lower) & (data <= upper)]
        removed_count = len(data) - len(cleaned)
        
        if removed_count == 0:
            QMessageBox.information(self, "탐지 결과", "탐지된 이상치가 없습니다 (모든 데이터가 IQR 1.5 범위 내 정상).")
        else:
            reply = QMessageBox.question(
                self, "이상치 제거 확인",
                f"총 {removed_count}개의 이상치가 발견되었습니다.\n"
                f"정상 범위: [{lower:.2f} ~ {upper:.2f}]\n\n"
                f"이상치를 제거하고 {len(cleaned)}개의 데이터로 다시 적합하시겠습니까?",
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                self.set_table_data(cleaned, trigger_fit=True)

    def open_sample_generator(self):
        d_type = self.fit_type_combo.currentData()
        dlg = RandomSampleDialog(self, is_discrete=(d_type == "discrete"))
        if dlg.exec() == QDialog.Accepted and dlg.generated_data is not None:
            self.set_table_data(dlg.generated_data, trigger_fit=True)

    def load_preset_data(self):
        p_name = self.preset_combo.currentData()
        if not p_name or p_name not in PRESET_DATASETS: return
        
        data = PRESET_DATASETS[p_name]()
        if "Poisson" in p_name or "Negative Binomial" in p_name:
            self.fit_type_combo.setCurrentIndex(1)  # Discrete
        else:
            self.fit_type_combo.setCurrentIndex(0)  # Continuous
            
        self.set_table_data(data, trigger_fit=True)

    def load_data_file(self):
        fname, _ = QFileDialog.getOpenFileName(
            self, "데이터 파일 열기", "", 
            "Data Files (*.xlsx *.xls *.csv *.txt);;Excel Files (*.xlsx *.xls);;CSV Files (*.csv);;Text Files (*.txt);;All Files (*)"
        )
        if not fname: return
        
        try:
            if fname.endswith('.xlsx') or fname.endswith('.xls'):
                df = pd.read_excel(fname, header=None)
            elif fname.endswith('.csv'):
                df = pd.read_csv(fname, header=None)
            else:
                df = pd.read_csv(fname, sep=r'\s+', header=None)
                
            data = pd.to_numeric(df.iloc[:, 0], errors='coerce').dropna().tolist()
            if not data:
                QMessageBox.warning(self, "데이터 없음", "파일에서 유효한 숫자 데이터를 찾지 못했습니다.")
                return
            self.set_table_data(data, trigger_fit=True)
        except Exception as e:
            QMessageBox.warning(self, "파일 열기 오류", f"파일을 읽는 중 오류가 발생했습니다:\n{e}")

    # ================= [분포 선택 및 적합 코어 알고리즘] =================

    def on_fit_type_changed(self):
        """연속형 vs 이산형 데이터 유형 변경 이벤트"""
        d_type = self.fit_type_combo.currentData()
        
        self.fit_dist_combo.blockSignals(True)
        self.fit_dist_combo.clear()
        self.fit_dist_combo.addItem("✨ 모든 후보 분포 자동 비교 (1위 추천)", "auto")
        for key, dist_info in DISTRIBUTIONS[d_type].items():
            self.fit_dist_combo.addItem(dist_info["name"], key)
        self.fit_dist_combo.blockSignals(False)

        if d_type == "discrete":
            self.radio_equal.setVisible(True)
            self.chk_overlay_top3.setVisible(False)
            self.chk_show_kde.setVisible(False)
        else:
            self.radio_equal.setVisible(False)
            if self.radio_equal.isChecked():
                self.radio_less.setChecked(True)
            self.chk_overlay_top3.setVisible(True)
            self.chk_show_kde.setVisible(True)

        self.on_fit_mode_changed()
        if len(self.get_raw_data()) >= 3 and self.chk_auto_fit.isChecked():
            self.fit_data()

    def on_fit_mode_changed(self):
        """적합 모드(🏆 모든 분포 자동 비교 vs 🎯 특정 분포 맞춤 적합) 전환 핸들러"""
        if getattr(self, 'is_updating_mode', False): return
        self.is_updating_mode = True
        try:
            is_target = self.radio_mode_target.isChecked()
            
            if is_target:
                # 🎯 특정 분포 직접 지정 모드
                if self.fit_dist_combo.currentData() == "auto" and self.fit_dist_combo.count() > 1:
                    self.fit_dist_combo.setCurrentIndex(1)
                    
                selected_name = self.fit_dist_combo.currentText()
                dist_key = self.fit_dist_combo.currentData()
                
                self.btn_fit.setText(f"🎯 선택한 [{selected_name}] 모수 추정 및 맞춤 적합 실행")
                self.btn_fit.setProperty("btnClass", "primary")
                self.btn_fit.style().unpolish(self.btn_fit)
                self.btn_fit.style().polish(self.btn_fit)
                
                self.lbl_fit_guide_title.setText("🎯 <b>[특정 모형 맞춤 적합 모드]</b>")
                self.lbl_fit_guide_desc.setText(
                    f"사용자가 지정한 <b>[{selected_name}]</b>의 모수(MLE)를 직접 추정하고, "
                    f"해당 모형의 확률 곡선(PDF/PMF)과 적합도(검정 p-값)를 차트에 집중 반영합니다."
                )
                
                if dist_key and dist_key != "auto" and self.fitted_results:
                    self.select_distribution(dist_key, update_combo=False, update_table=True)
                elif self.chk_auto_fit.isChecked() and len(self.get_raw_data()) >= 3:
                    self.fit_data()
            else:
                # 🏆 모든 후보 분포 자동 비교 모드
                self.fit_dist_combo.blockSignals(True)
                auto_idx = self.fit_dist_combo.findData("auto")
                if auto_idx >= 0:
                    self.fit_dist_combo.setCurrentIndex(auto_idx)
                self.fit_dist_combo.blockSignals(False)
                
                self.btn_fit.setText("🚀 모든 후보 분포 비교 및 최적 1위 탐색 실행")
                self.btn_fit.setProperty("btnClass", "success")
                self.btn_fit.style().unpolish(self.btn_fit)
                self.btn_fit.style().polish(self.btn_fit)
                
                self.lbl_fit_guide_title.setText("🏆 <b>[전체 후보 자동 비교 모드]</b>")
                self.lbl_fit_guide_desc.setText(
                    "모든 후보 분포 모델을 동시 적합하여 AIC/BIC 기준 <b>최적 1위 분포</b>를 자동으로 찾아 추천하고 전체 순위표를 산출합니다."
                )
                
                if self.fitted_results:
                    best_key = self.fitted_results[0]["key"]
                    self.select_distribution(best_key, update_combo=False, update_table=True)
                elif self.chk_auto_fit.isChecked() and len(self.get_raw_data()) >= 3:
                    self.fit_data()
        finally:
            self.is_updating_mode = False

    def on_dist_combo_selected(self):
        """적합 모형 콤보박스 선택 이벤트"""
        if self.is_selecting_dist: return
        selected_key = self.fit_dist_combo.currentData()
        
        if selected_key == "auto":
            if not self.radio_mode_auto.isChecked():
                self.radio_mode_auto.setChecked(True)
            return
        else:
            # 특정 모형을 고르면 자동으로 '특정 분포 맞춤 적합' 라디오 버튼으로 전환
            if not self.radio_mode_target.isChecked():
                self.is_updating_mode = True
                self.radio_mode_target.setChecked(True)
                self.is_updating_mode = False
            
            selected_name = self.fit_dist_combo.currentText()
            self.btn_fit.setText(f"🎯 선택한 [{selected_name}] 모수 추정 및 맞춤 적합 실행")
            self.btn_fit.setProperty("btnClass", "primary")
            self.btn_fit.style().unpolish(self.btn_fit)
            self.btn_fit.style().polish(self.btn_fit)
            
            self.lbl_fit_guide_title.setText("🎯 <b>[특정 모형 맞춤 적합 모드]</b>")
            self.lbl_fit_guide_desc.setText(
                f"사용자가 지정한 <b>[{selected_name}]</b>의 모수(MLE)를 직접 추정하고, "
                f"해당 모형의 확률 곡선(PDF/PMF)과 적합도(검정 p-값)를 차트에 집중 반영합니다."
            )
            
            if not self.fitted_results:
                if len(self.get_raw_data()) >= 3:
                    self.fit_data()
                return
                
            self.select_distribution(selected_key, update_combo=False, update_table=True)

    def select_distribution(self, dist_key, update_combo=True, update_table=True):
        """특정 분포를 활성화하고 파라미터 요약 카드, 랭킹 테이블, 차트, 상단 배지를 일괄 동기화"""
        target_res = None
        target_row = -1
        for i, res in enumerate(self.fitted_results):
            if res["key"] == dist_key:
                target_res = res
                target_row = i
                break
                
        if not target_res:
            # 랭킹에 없으면 단독 적합 시도
            target_res = self.fit_single_distribution(dist_key)
            if not target_res: return

        self.is_selecting_dist = True
        try:
            self.current_dist_key = target_res["key"]
            self.current_params = target_res["params"]
            self.current_dist_obj = target_res["dist_obj"]
            
            # 콤보박스 동기화
            if update_combo:
                self.fit_dist_combo.blockSignals(True)
                idx = self.fit_dist_combo.findData(dist_key)
                if idx >= 0:
                    self.fit_dist_combo.setCurrentIndex(idx)
                self.fit_dist_combo.blockSignals(False)
                
            # 랭킹 테이블 행 동기화
            if update_table and target_row >= 0:
                self.rank_table.blockSignals(True)
                self.rank_table.selectRow(target_row)
                self.rank_table.blockSignals(False)

            # 요약 카드 업데이트
            is_best = (target_row == 0)
            prefix = "⭐ [최적 1위] " if is_best else "🎯 [맞춤 지정] "
            self.lbl_best_dist.setText(f"{prefix}{target_res['name']}")
            self.lbl_best_params.setText(target_res["param_str"])
            
            p_val_str = f"p={target_res['ks_p']:.4f}" if target_res['ks_p'] is not None else "-"
            self.lbl_best_gof.setText(f"AIC: {target_res['aic']:.1f} | BIC: {target_res['bic']:.1f} | {p_val_str}")
            
            # 이론 통계량 계산
            th_stats = calculate_theoretical_stats(target_res["dist_obj"], target_res["key"])
            m_val = th_stats.get("mean", "-")
            std_val = th_stats.get("std", "-")
            skew_val = th_stats.get("skew", "-")
            self.lbl_best_stats.setText(f"E(X)={m_val}, σ={std_val}, 왜도={skew_val}")
            
            # 상단 활성 모델 안내 배지 업데이트
            if hasattr(self, 'lbl_active_model_badge'):
                p_disp = f"검정 p={target_res['ks_p']:.4f}" if target_res['ks_p'] is not None else ""
                badge_tag = "⭐ [1위 최적 모형]" if is_best else "🎯 [사용자 맞춤 모형]"
                self.lbl_active_model_badge.setText(
                    f"{badge_tag} <b>{target_res['name']}</b> &nbsp;|&nbsp; "
                    f"추정 모수 (MLE): <span style='color:#198754; font-family:Consolas; font-weight:bold;'>{target_res['param_str']}</span> &nbsp;|&nbsp; "
                    f"AIC: {target_res['aic']:.1f} ({p_disp})"
                )
            
            # 계산기 값 재산출 및 차트 다시 그리기
            self.recalc_mark()
            self.plot_fitted_chart()
        finally:
            self.is_selecting_dist = False

    def on_rank_row_selected(self):
        """랭킹 테이블 행 클릭 시 해당 분포로 즉시 전환"""
        if self.is_selecting_dist: return
        row = self.rank_table.currentRow()
        if 0 <= row < len(self.fitted_results):
            selected = self.fitted_results[row]
            
            # 행을 직접 클릭하면 '특정 모형 지정' 상태로 전환하여 버튼 텍스트와 가이드 반영
            self.is_updating_mode = True
            self.radio_mode_target.setChecked(True)
            self.is_updating_mode = False
            
            self.btn_fit.setText(f"🎯 선택한 [{selected['name']}] 모수 추정 및 맞춤 적합 실행")
            self.btn_fit.setProperty("btnClass", "primary")
            self.btn_fit.style().unpolish(self.btn_fit)
            self.btn_fit.style().polish(self.btn_fit)
            
            self.lbl_fit_guide_title.setText("🎯 <b>[특정 모형 맞춤 적합 모드]</b>")
            self.lbl_fit_guide_desc.setText(
                f"순위표에서 선택한 <b>[{selected['name']}]</b>의 모수를 차트에 표시하고 있습니다."
            )
            
            self.select_distribution(selected["key"], update_combo=True, update_table=False)

    def fit_single_distribution(self, dist_key):
        """특정 단일 분포에 대해 적합 수행"""
        data = self.get_raw_data()
        d_type = self.fit_type_combo.currentData()
        if dist_key not in DISTRIBUTIONS[d_type]: return None
        
        dist_info = DISTRIBUTIONS[d_type][dist_key]
        res = self._fit_one(data, d_type, dist_key, dist_info)
        return res

    def fit_data(self):
        """모든 후보 분포에 대해 적합을 수행하고 현재 모드에 따라 최적 1위 또는 사용자 지정 모형 선택"""
        data = self.get_raw_data()
        if len(data) < 3:
            self.lbl_fit_status.setText("데이터 부족 (최소 3개 필요)")
            return

        if np.std(data) < 1e-12:
            self.lbl_fit_status.setText("⚠️ 데이터 분산이 0입니다 (모든 관측치 값이 동일하여 적합 불가)")
            self.ax2_clear()
            return

        d_type = self.fit_type_combo.currentData()
        self.fitted_results = []
        
        # 1. 모든 후보 모형 적합 수행
        for dist_key, dist_info in DISTRIBUTIONS[d_type].items():
            res = self._fit_one(data, d_type, dist_key, dist_info)
            if res is not None:
                self.fitted_results.append(res)

        if not self.fitted_results:
            self.lbl_fit_status.setText("적합 가능한 분포를 찾지 못했습니다")
            self.lbl_best_dist.setText("적합 불가")
            self.lbl_best_params.setText("-")
            self.lbl_best_gof.setText("-")
            self.lbl_best_stats.setText("-")
            if hasattr(self, 'lbl_active_model_badge'):
                self.lbl_active_model_badge.setText("⚠️ 적합 가능한 분포를 찾지 못했습니다 (데이터 값/부호 확인 필요)")
            self.ax2_clear()
            return

        # 2. AIC 기준 오름차순 랭킹 정렬
        self.fitted_results.sort(key=lambda x: x["aic"])
        
        # 3. 랭킹 테이블 갱신
        self.rank_table.blockSignals(True)
        self.rank_table.setRowCount(len(self.fitted_results))
        for i, res in enumerate(self.fitted_results):
            rank_str = f"🥇 1위" if i == 0 else f"🥈 2위" if i == 1 else f"🥉 3위" if i == 2 else f"{i+1}위"
            item_rank = QTableWidgetItem(rank_str)
            item_rank.setTextAlignment(Qt.AlignCenter)
            if i == 0:
                item_rank.setFont(QFont("", -1, QFont.Bold))
                item_rank.setForeground(QColor("#0d6efd"))
                
            item_name = QTableWidgetItem(res["name"])
            item_aic = QTableWidgetItem(f"{res['aic']:.1f}")
            item_bic = QTableWidgetItem(f"{res['bic']:.1f}")
            
            p_val = res['ks_p']
            item_p = QTableWidgetItem(f"{p_val:.4f}" if p_val is not None else "-")
            
            # 적합 판정 배지 (유의수준 0.05 기준)
            if i == 0:
                status_text = "⭐ 최적(Best)"
                badge_color = QColor("#198754")
            elif p_val is not None and p_val >= 0.05:
                status_text = "✅ 양호"
                badge_color = QColor("#0d6efd")
            else:
                status_text = "⚠️ 부적합"
                badge_color = QColor("#dc3545")
            item_status = QTableWidgetItem(status_text)
            item_status.setForeground(badge_color)
            item_status.setTextAlignment(Qt.AlignCenter)
            
            for col, item in enumerate([item_rank, item_name, item_aic, item_bic, item_p, item_status]):
                self.rank_table.setItem(i, col, item)
        self.rank_table.blockSignals(False)

        # 4. 모드에 따라 목표 모형 결정
        is_target = self.radio_mode_target.isChecked()
        current_spec = self.fit_dist_combo.currentData()
        
        if is_target and current_spec and current_spec != "auto":
            # 사용자가 선택한 특정 모형에 맞춤 반영
            target_key = current_spec
            target_res = next((r for r in self.fitted_results if r["key"] == target_key), None)
            target_name = target_res["name"] if target_res else target_key
            self.lbl_fit_status.setText(f"✅ [{target_name}] 맞춤 적합 완료")
            self.select_distribution(target_key, update_combo=False, update_table=True)
        else:
            # 자동 비교 모드: 최적 1위 선택
            best_res = self.fitted_results[0]
            self.lbl_fit_status.setText(f"✅ 최적 1위 [{best_res['name']}] 자동 선정 완료")
            self.select_distribution(best_res["key"], update_combo=False, update_table=True)


    def _fit_one(self, data, d_type, dist_key, dist_info):
        """개별 분포에 대한 안정적 과학적 피팅 및 모수 추출"""
        n_samples = len(data)
        func = dist_info["func"]
        
        has_negative = np.any(data < 0)
        has_non_positive = np.any(data <= 0)
        
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                if d_type == "continuous":
                    # 양수 정의역 전용 분포 검증
                    positive_only = ["lognorm", "weibull_min", "gamma", "expon", "pareto", "rayleigh", "chi2", "f"]
                    if dist_key in positive_only and has_non_positive:
                        return None
                    
                    if dist_key == "beta" and (np.any(data <= 0) or np.any(data >= 1)):
                        # Beta는 [0, 1] 범위 외의 데이터는 기본적으로 배제
                        return None

                    # 과학적 모수 추정 (양수 분포의 경우 floc=0 고정으로 안정성 확보)
                    if dist_key in ["weibull_min", "lognorm", "gamma", "expon", "pareto", "rayleigh", "chi2", "f"]:
                        params = func.fit(data, floc=0)
                    else:
                        params = func.fit(data)

                    # 불량 모수 필터링
                    if any(np.isnan(p) or np.isinf(p) for p in params):
                        return None
                    
                    dist_obj = func(*params)
                    
                    # Log-Likelihood, AIC, BIC
                    ll = float(np.sum(func.logpdf(data, *params)))
                    if np.isnan(ll) or np.isinf(ll): return None
                    
                    k_params = len(params)
                    aic = 2 * k_params - 2 * ll
                    bic = k_params * np.log(n_samples) - 2 * ll
                    
                    # SSE (히스토그램 관측 밀도 대비)
                    y_obs, x_bins = np.histogram(data, bins='auto', density=True)
                    x_mids = (x_bins[:-1] + x_bins[1:]) / 2
                    y_theo = dist_obj.pdf(x_mids)
                    sse = float(np.sum((y_obs - y_theo)**2))
                    
                    # Kolmogorov-Smirnov Goodness-of-fit 검정
                    ks_res = stats.kstest(data, lambda x: dist_obj.cdf(x))
                    ks_stat = float(ks_res.statistic)
                    ks_p = float(ks_res.pvalue)
                    
                    param_str = self._format_continuous_params(dist_key, params)
                    
                    return {
                        "key": dist_key,
                        "name": dist_info["name"],
                        "sse": sse,
                        "aic": aic,
                        "bic": bic,
                        "ks_stat": ks_stat,
                        "ks_p": ks_p,
                        "params": params,
                        "param_str": param_str,
                        "dist_obj": dist_obj
                    }
                else:
                    # 이산형 분포
                    data_int = np.round(data).astype(int)
                    if np.any(data_int < 0): return None
                    
                    mean_val = float(np.mean(data_int))
                    var_val = float(np.var(data_int))
                    unique_vals, counts = np.unique(data_int, return_counts=True)
                    probs = counts / np.sum(counts)

                    if dist_key == "poisson":
                        args = (max(mean_val, 1e-3),)
                    elif dist_key == "geom":
                        p = min(max(1.0 / mean_val if mean_val > 0 else 0.5, 1e-4), 0.999)
                        args = (p,)
                    elif dist_key == "binom":
                        n_est = max(int(np.max(data_int)), 1)
                        p_est = min(max(mean_val / n_est, 1e-4), 0.999)
                        args = (n_est, p_est)
                    elif dist_key == "randint":
                        a_est = int(np.min(data_int))
                        b_est = int(np.max(data_int)) + 1
                        args = (a_est, b_est)
                    elif dist_key == "nbinom":
                        p_est = mean_val / var_val if var_val > mean_val else 0.5
                        p_est = min(max(p_est, 1e-4), 0.999)
                        r_est = max(1, int((mean_val * p_est) / (1 - p_est)))
                        args = (r_est, p_est)
                    else:
                        return None

                    dist_obj = func(*args)
                    y_theo = dist_obj.pmf(unique_vals)
                    sse = float(np.sum((probs - y_theo)**2))
                    
                    ll = float(np.sum(func.logpmf(data_int, *args)))
                    if np.isnan(ll) or np.isinf(ll): return None
                    
                    k_params = len(args)
                    aic = 2 * k_params - 2 * ll
                    bic = k_params * np.log(n_samples) - 2 * ll
                    
                    # 카이제곱 적합도 검정 (정규화된 f_exp 적용)
                    ks_p = None
                    ks_stat = None
                    try:
                        expected = y_theo * n_samples
                        valid_mask = expected > 1e-6
                        if np.sum(valid_mask) > k_params:
                            f_obs = counts[valid_mask]
                            f_exp = expected[valid_mask] * (np.sum(f_obs) / np.sum(expected[valid_mask]))
                            chi2_res = stats.chisquare(f_obs=f_obs, f_exp=f_exp, ddof=k_params)
                            ks_p = float(chi2_res.pvalue)
                            ks_stat = float(chi2_res.statistic)
                    except Exception:
                        pass

                    param_str = self._format_discrete_params(dist_key, args)
                    
                    return {
                        "key": dist_key,
                        "name": dist_info["name"],
                        "sse": sse,
                        "aic": aic,
                        "bic": bic,
                        "ks_stat": ks_stat,
                        "ks_p": ks_p,
                        "params": args,
                        "param_str": param_str,
                        "dist_obj": dist_obj
                    }
            except Exception:
                return None

    def _format_continuous_params(self, dist_key, params):
        """수학적/통계적으로 정확한 모수 기호 및 값 서식화"""
        try:
            if dist_key == "norm":
                return f"μ = {params[0]:.3f}, σ = {params[1]:.3f}"
            elif dist_key == "lognorm":
                s, loc, scale = params
                mu_log = np.log(scale)
                return f"μ_log = {mu_log:.3f}, σ_log = {s:.3f}"
            elif dist_key == "weibull_min":
                c, loc, scale = params
                return f"형태(k) = {c:.3f}, 척도(λ) = {scale:.3f}"
            elif dist_key == "expon":
                loc, scale = params
                rate = 1.0 / scale if scale > 0 else 0
                return f"발생률(λ) = {rate:.3f}, 평균 = {scale:.3f}"
            elif dist_key == "gamma":
                a, loc, scale = params
                return f"형태(α) = {a:.3f}, 척도(θ) = {scale:.3f}"
            elif dist_key == "t":
                df, loc, scale = params
                return f"자유도(ν) = {df:.2f}, 위치(μ) = {loc:.3f}, 척도(σ) = {scale:.3f}"
            elif dist_key == "uniform":
                loc, scale = params
                return f"최소(a) = {loc:.3f}, 최대(b) = {loc + scale:.3f}"
            elif dist_key == "beta":
                a, b, loc, scale = params
                return f"형태1(α) = {a:.3f}, 형태2(β) = {b:.3f}"
            elif dist_key == "cauchy":
                return f"위치(x₀) = {params[0]:.3f}, 척도(γ) = {params[1]:.3f}"
            elif dist_key == "laplace":
                return f"위치(μ) = {params[0]:.3f}, 척도(b) = {params[1]:.3f}"
            elif dist_key == "logistic":
                return f"위치(μ) = {params[0]:.3f}, 척도(s) = {params[1]:.3f}"
            elif dist_key == "pareto":
                return f"형태(α) = {params[0]:.3f}, 척도(x_m) = {params[2]:.3f}"
            elif dist_key == "rayleigh":
                return f"척도(σ) = {params[1]:.3f}"
            elif dist_key == "chi2":
                return f"자유도(k) = {params[0]:.2f}"
            elif dist_key == "f":
                return f"자유도1(d₁) = {params[0]:.2f}, 자유도2(d₂) = {params[1]:.2f}"
            else:
                return ", ".join(f"{p:.3f}" for p in params)
        except Exception:
            return str(params)

    def _format_discrete_params(self, dist_key, args):
        try:
            if dist_key == "poisson":
                return f"발생률(λ) = {args[0]:.3f}"
            elif dist_key == "binom":
                return f"시행횟수(n) = {args[0]}, 성공확률(p) = {args[1]:.3f}"
            elif dist_key == "geom":
                return f"성공확률(p) = {args[0]:.3f}"
            elif dist_key == "nbinom":
                return f"목표성공(r) = {args[0]}, 성공확률(p) = {args[1]:.3f}"
            elif dist_key == "randint":
                return f"최소(a) = {args[0]}, 최대(b) = {args[1]-1}"
            else:
                return str(args)
        except Exception:
            return str(args)

    # ================= [시각화 및 5종 진단 플롯] =================

    def plot_fitted_chart(self):
        """선택된 진단 모드 및 분포에 맞춰 고화질 차트 렌더링"""
        if not self.current_dist_obj or not self.current_dist_key:
            return

        data = self.get_raw_data()
        if len(data) < 3: return
        
        d_type = self.fit_type_combo.currentData()
        dist_key = self.current_dist_key
        dist = self.current_dist_obj
        diag_mode = self.diag_combo.currentIndex()
        
        self.figure2.clear()
        ax = self.figure2.add_subplot(111)
        
        # 계산기 음영 값 확인
        x_mark = None
        if self.calc_val_x.text().strip():
            try: x_mark = float(self.calc_val_x.text())
            except ValueError: pass
            
        calc_dir = "less"
        if self.radio_greater.isChecked(): calc_dir = "greater"
        elif self.radio_equal.isChecked() and d_type == "discrete": calc_dir = "equal"

        if d_type == "continuous":
            self._plot_continuous_diagnostics(ax, data, dist, dist_key, diag_mode, x_mark, calc_dir)
        else:
            self._plot_discrete_diagnostics(ax, data, dist, dist_key, diag_mode, x_mark, calc_dir)

        ax.grid(True, linestyle='--', alpha=0.5)
        ax.legend(fontsize=9, loc='best')
        self.figure2.tight_layout()
        self.canvas2.draw_idle()
        self.btn_export_fit.setEnabled(True)

    def _plot_continuous_diagnostics(self, ax, data, dist, dist_key, diag_mode, x_mark, calc_dir):
        """연속형 분포의 5가지 진단 차트"""
        dist_info = DISTRIBUTIONS["continuous"].get(dist_key, {"name": dist_key})
        
        if diag_mode == 0:  # 1. 히스토그램 vs 적합 PDF
            counts, bins, _ = ax.hist(data, bins='auto', density=True, alpha=0.42, 
                                      color='#0d6efd', edgecolor='black', label='표본 히스토그램 (Empirical)')
            
            x_min = min(bins[0], dist.ppf(0.002))
            x_max = max(bins[-1], dist.ppf(0.998))
            x = np.linspace(x_min, x_max, 500)
            y = dist.pdf(x)
            
            # 주 적합선
            ax.plot(x, y, color='#dc3545', lw=2.5, label=f'적합 {dist_info["name"]} PDF')
            
            # 상위 3개 최적분포 오버레이 비교 옵션
            if self.chk_overlay_top3.isChecked() and len(self.fitted_results) >= 2:
                overlay_colors = ['#198754', '#fd7e14', '#6f42c1']
                for idx, top_res in enumerate(self.fitted_results[:3]):
                    if top_res["key"] == dist_key: continue
                    y_top = top_res["dist_obj"].pdf(x)
                    ax.plot(x, y_top, lw=1.8, linestyle='--', color=overlay_colors[idx % len(overlay_colors)],
                            label=f'{idx+1}위: {top_res["name"]} (AIC {top_res["aic"]:.0f})')
                    
            # 경험적 KDE 옵션
            if self.chk_show_kde.isChecked() and len(data) >= 5:
                try:
                    kde = stats.gaussian_kde(data)
                    ax.plot(x, kde(x), color='#20c997', lw=1.8, linestyle=':', label='KDE (경험적 평활 밀도)')
                except Exception:
                    pass

            # 계산기 음영 영역
            if x_mark is not None:
                sym = "≤" if calc_dir == "less" else "≥"
                prob_val = float(dist.cdf(x_mark) if calc_dir == "less" else dist.sf(x_mark))
                ax.axvline(x_mark, color='#198754', linestyle='--', lw=2, label=f'x = {x_mark:g}')
                mask = (x <= x_mark) if calc_dir == "less" else (x >= x_mark)
                ax.fill_between(x[mask], y[mask], color='#198754', alpha=0.3)
                max_y = max(y) if len(y) > 0 and max(y) > 0 else 1.0
                ax.text(x_mark, max_y * 0.75, f' P(X {sym} {x_mark:g}) = {prob_val:.4f}', 
                        color='#198754', fontweight='bold', fontsize=10)

            ax.set_title(f"{dist_info['name']} - 데이터 히스토그램 vs 적합 확률밀도함수(PDF)", fontsize=11, fontweight='bold')
            ax.set_xlabel("X (확률변수)")
            ax.set_ylabel("확률밀도 (Density)")

        elif diag_mode == 1:  # 2. ECDF vs 이론 CDF
            sorted_data = np.sort(data)
            n = len(data)
            y_ecdf = np.arange(1, n + 1) / n
            ax.step(sorted_data, y_ecdf, where='post', color='#0d6efd', lw=2, label='경험적 누적확률 (ECDF)')
            
            x = np.linspace(sorted_data[0], sorted_data[-1], 500)
            ax.plot(x, dist.cdf(x), color='#dc3545', lw=2.5, linestyle='--', label=f'이론 {dist_info["name"]} CDF')
            
            # K-S 최대 차이 D 시각화
            theo_at_data = dist.cdf(sorted_data)
            diffs = np.abs(y_ecdf - theo_at_data)
            max_idx = np.argmax(diffs)
            max_x = sorted_data[max_idx]
            max_diff = diffs[max_idx]
            ax.vlines(max_x, theo_at_data[max_idx], y_ecdf[max_idx], color='#d63384', lw=2.5, 
                      label=f'최대 수직 격차 D = {max_diff:.4f}')
            
            ax.set_title(f"{dist_info['name']} - 경험적 누적분포(ECDF) vs 이론 누적분포(CDF)", fontsize=11, fontweight='bold')
            ax.set_xlabel("X")
            ax.set_ylabel("누적확률 P(X ≤ x)")

        elif diag_mode == 2:  # 3. Q-Q Plot
            sorted_data = np.sort(data)
            n = len(data)
            probs = (np.arange(1, n + 1) - 0.5) / n
            theo_q = dist.ppf(probs)
            
            ax.scatter(theo_q, sorted_data, color='#0d6efd', alpha=0.75, edgecolors='k', s=35, label='표본 분위수 점')
            min_val = min(theo_q[0], sorted_data[0])
            max_val = max(theo_q[-1], sorted_data[-1])
            ax.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='기준선 (y = x)')
            
            ax.set_title(f"{dist_info['name']} - 분위수-분위수 플롯 (Q-Q Plot)", fontsize=11, fontweight='bold')
            ax.set_xlabel("이론적 분위수 (Theoretical Quantiles)")
            ax.set_ylabel("표본 분위수 (Sample Quantiles)")

        elif diag_mode == 3:  # 4. P-P Plot
            sorted_data = np.sort(data)
            n = len(data)
            emp_p = (np.arange(1, n + 1) - 0.5) / n
            theo_p = dist.cdf(sorted_data)
            
            ax.scatter(theo_p, emp_p, color='#198754', alpha=0.75, edgecolors='k', s=35, label='확률 대응점')
            ax.plot([0, 1], [0, 1], 'r--', lw=2, label='완전 일치 기준선 (y = x)')
            
            ax.set_title(f"{dist_info['name']} - 확률-확률 플롯 (P-P Plot)", fontsize=11, fontweight='bold')
            ax.set_xlabel("이론적 누적확률 (Theoretical Probability)")
            ax.set_ylabel("경험적 누적확률 (Empirical Probability)")

        elif diag_mode == 4:  # 5. 잔차 분석 플롯 (Residuals)
            y_obs, x_bins = np.histogram(data, bins='auto', density=True)
            x_mids = (x_bins[:-1] + x_bins[1:]) / 2
            y_theo = dist.pdf(x_mids)
            residuals = y_obs - y_theo
            
            ax.bar(x_mids, residuals, width=(x_bins[1]-x_bins[0])*0.8, color='#6f42c1', alpha=0.6, 
                   edgecolor='black', label='밀도 잔차 (Observed - Expected)')
            ax.axhline(0, color='red', linestyle='--', lw=1.5)
            
            ax.set_title(f"{dist_info['name']} - 구간별 적합 잔차 편차 분석 (Residual Plot)", fontsize=11, fontweight='bold')
            ax.set_xlabel("X 구간 중심점")
            ax.set_ylabel("밀도 오차 (Obs - Exp)")

    def _plot_discrete_diagnostics(self, ax, data, dist, dist_key, diag_mode, x_mark, calc_dir):
        """이산형 분포의 진단 차트 (5가지 모드 완벽 지원)"""
        dist_info = DISTRIBUTIONS["discrete"].get(dist_key, {"name": dist_key})
        data_int = np.round(data).astype(int)
        unique_vals, counts = np.unique(data_int, return_counts=True)
        probs = counts / np.sum(counts)
        min_v, max_v = int(np.min(data_int)), int(np.max(data_int))
        all_x = np.arange(min_v, max_v + 1)
        
        if diag_mode == 0:  # 1. 막대도수 vs PMF
            ax.bar(unique_vals, probs, alpha=0.45, color='#0d6efd', edgecolor='black', width=0.55, label='표본 상대도수')
            y_pmf = dist.pmf(all_x)
            ax.plot(all_x, y_pmf, 'ro-', lw=2, markersize=6, label=f'적합 {dist_info["name"]} PMF')
            
            if x_mark is not None:
                x_int = int(round(x_mark))
                max_y = max(y_pmf) if len(y_pmf) > 0 and max(y_pmf) > 0 else 1.0
                if calc_dir == "equal":
                    p_res = dist.pmf(x_int)
                    ax.axvline(x_int, color='#198754', linestyle='--', lw=2)
                    ax.text(x_int, max_y * 0.7, f' P(X = {x_int}) = {p_res:.4f}', color='#198754', fontweight='bold')
                elif calc_dir == "less":
                    p_res = dist.cdf(x_int)
                    ax.axvline(x_int, color='#198754', linestyle='--', lw=2)
                    ax.text(x_int, max_y * 0.7, f' P(X ≤ {x_int}) = {p_res:.4f}', color='#198754', fontweight='bold')
                else:
                    p_res = dist.sf(x_int - 1)
                    ax.axvline(x_int, color='#198754', linestyle='--', lw=2)
                    ax.text(x_int, max_y * 0.7, f' P(X ≥ {x_int}) = {p_res:.4f}', color='#198754', fontweight='bold')

            ax.set_title(f"{dist_info['name']} - 표본 도수 vs 적합 확률질량함수(PMF)", fontsize=11, fontweight='bold')
            ax.set_xlabel("X (정수값)")
            ax.set_ylabel("확률 (PMF)")

        elif diag_mode == 1:  # 2. ECDF vs 이론 CDF
            sorted_data = np.sort(data_int)
            y_ecdf = np.arange(1, len(data_int) + 1) / len(data_int)
            ax.step(sorted_data, y_ecdf, where='post', color='#0d6efd', lw=2, label='경험적 누적확률 (ECDF)')
            ax.step(all_x, dist.cdf(all_x), where='post', color='#dc3545', lw=2.5, linestyle='--', label='이론 CDF')
            
            ax.set_title(f"{dist_info['name']} - 이산형 누적확률(CDF) 비교", fontsize=11, fontweight='bold')
            ax.set_xlabel("X")
            ax.set_ylabel("누적확률 P(X ≤ x)")

        elif diag_mode == 2:  # 3. Q-Q Plot
            sorted_data = np.sort(data_int)
            n = len(data_int)
            probs_q = (np.arange(1, n + 1) - 0.5) / n
            theo_q = dist.ppf(probs_q)
            ax.scatter(theo_q, sorted_data, color='#0d6efd', alpha=0.75, edgecolors='k', s=35, label='표본 분위수 점')
            min_val = min(theo_q[0], sorted_data[0])
            max_val = max(theo_q[-1], sorted_data[-1])
            ax.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='기준선 (y = x)')
            ax.set_title(f"{dist_info['name']} - 이산형 분위수-분위수 플롯 (Q-Q Plot)", fontsize=11, fontweight='bold')
            ax.set_xlabel("이론적 분위수")
            ax.set_ylabel("표본 분위수")

        elif diag_mode == 3:  # 4. P-P Plot
            sorted_data = np.sort(data_int)
            n = len(data_int)
            emp_p = (np.arange(1, n + 1) - 0.5) / n
            theo_p = dist.cdf(sorted_data)
            ax.scatter(theo_p, emp_p, color='#198754', alpha=0.75, edgecolors='k', s=35, label='확률 대응점')
            ax.plot([0, 1], [0, 1], 'r--', lw=2, label='기준선 (y = x)')
            ax.set_title(f"{dist_info['name']} - 이산형 확률-확률 플롯 (P-P Plot)", fontsize=11, fontweight='bold')
            ax.set_xlabel("이론적 누적확률")
            ax.set_ylabel("경험적 누적확률")

        elif diag_mode == 4:  # 5. 잔차 분석
            y_theo = dist.pmf(unique_vals)
            residuals = probs - y_theo
            ax.bar(unique_vals, residuals, width=0.55, color='#6f42c1', alpha=0.6, edgecolor='black', label='도수 잔차 (Obs - Exp)')
            ax.axhline(0, color='red', linestyle='--', lw=1.5)
            ax.set_title(f"{dist_info['name']} - 관측 도수 vs 이론 PMF 잔차 분석", fontsize=11, fontweight='bold')
            ax.set_xlabel("X (값)")
            ax.set_ylabel("확률 오차 (Obs - Exp)")

    def ax2_clear(self):
        self.figure2.clear()
        self.canvas2.draw_idle()

    # ================= [확률 및 분위수 계산기 로직] =================

    def on_calc_x_changed(self, text):
        if not text.strip() or not self.current_dist_obj: return
        try:
            val_x = float(text)
            self.calc_val_p.blockSignals(True)
            self.calc_val_p.clear()
            self.calc_val_p.blockSignals(False)
            
            d_type = self.fit_type_combo.currentData()
            dist = self.current_dist_obj
            
            if self.radio_less.isChecked():
                p = dist.cdf(val_x)
                self.lbl_calc_result.setText(f"P(X ≤ {val_x:g}) = {p:.5f} ({p*100:.2f}%)")
            elif self.radio_greater.isChecked():
                p = dist.sf(val_x)
                self.lbl_calc_result.setText(f"P(X ≥ {val_x:g}) = {p:.5f} ({p*100:.2f}%)")
            elif self.radio_equal.isChecked() and d_type == "discrete":
                p = dist.pmf(int(round(val_x)))
                self.lbl_calc_result.setText(f"P(X = {int(round(val_x))}) = {p:.5f} ({p*100:.2f}%)")
            else:
                self.lbl_calc_result.setText("-")
                
            self.plot_fitted_chart()
        except Exception:
            self.lbl_calc_result.setText("계산 불가")

    def on_calc_p_changed(self, text):
        if not text.strip() or not self.current_dist_obj: return
        try:
            val_p = float(text)
            if not (0.0 < val_p < 1.0):
                self.lbl_calc_result.setText("확률은 0과 1 사이여야 합니다")
                return
                
            self.calc_val_x.blockSignals(True)
            self.calc_val_x.clear()
            self.calc_val_x.blockSignals(False)
            
            dist = self.current_dist_obj
            if self.radio_less.isChecked():
                x = dist.ppf(val_p)
                self.lbl_calc_result.setText(f"P(X ≤ {x:.3f}) = {val_p:.4f} → x = {x:.3f}")
            elif self.radio_greater.isChecked():
                x = dist.isf(val_p)
                self.lbl_calc_result.setText(f"P(X ≥ {x:.3f}) = {val_p:.4f} → x = {x:.3f}")
            else:
                self.lbl_calc_result.setText("분위수 역산은 이하/이상 모드에서 지원됩니다")
                return
                
            self.calc_val_x.blockSignals(True)
            self.calc_val_x.setText(f"{x:.3f}")
            self.calc_val_x.blockSignals(False)
            self.plot_fitted_chart()
        except Exception:
            self.lbl_calc_result.setText("계산 불가")

    def recalc_mark(self):
        if self.calc_val_x.text().strip():
            self.on_calc_x_changed(self.calc_val_x.text().strip())
        elif self.calc_val_p.text().strip():
            self.on_calc_p_changed(self.calc_val_p.text().strip())

    def reset_calc_inputs(self):
        self.calc_val_x.blockSignals(True)
        self.calc_val_p.blockSignals(True)
        self.calc_val_x.clear()
        self.calc_val_p.clear()
        self.calc_val_x.blockSignals(False)
        self.calc_val_p.blockSignals(False)
        self.lbl_calc_result.setText("-")
        self.plot_fitted_chart()

    # ================= [차트 및 지식 허브 외부 연동] =================

    def copy_chart_to_clipboard(self):
        """차트를 이미지 픽스맵 형태로 클립보드에 복사"""
        pixmap = self.canvas2.grab()
        QApplication.clipboard().setPixmap(pixmap)
        QMessageBox.information(self, "복사 완료", "차트 이미지가 클립보드에 복사되었습니다.\n문서(Word, PPT 등)에 바로 붙여넣기(Ctrl+V)할 수 있습니다.")

    def export_chart(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "차트 이미지 저장", "", 
            "PNG Files (*.png);;JPEG Files (*.jpg);;PDF Files (*.pdf);;All Files (*)"
        )
        if file_path:
            try:
                self.figure2.savefig(file_path, dpi=300, bbox_inches='tight')
                QMessageBox.information(self, "저장 완료", f"차트가 성공적으로 저장되었습니다:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "저장 실패", f"차트를 저장하는 중 오류가 발생했습니다:\n{str(e)}")

    def open_knowledge_hub(self):
        dist_key = self.current_dist_key or self.fit_dist_combo.currentData()
        if dist_key == "auto": dist_key = "norm"
        dlg = KnowledgeHubDialog(self, initial_dist_key=dist_key)
        dlg.exec()

    def open_web_reference(self):
        dist_key = self.current_dist_key or self.fit_dist_combo.currentData()
        if dist_key == "auto": dist_key = "norm"
        info = DISTRIBUTION_KNOWLEDGE.get(dist_key)
        if info and "links" in info and len(info["links"]) > 0:
            url = info["links"][0]["url"]
            QDesktopServices.openUrl(QUrl(url))
        else:
            QMessageBox.information(self, "안내", "해당 분포의 웹 링크 정보가 없습니다.")

    def eventFilter(self, source, event):
        if source is self.data_table and event.type() == QEvent.KeyPress:
            if event.matches(QKeySequence.Paste):
                self.paste_data()
                return True
            elif event.key() == Qt.Key_Delete:
                self.delete_selected_data()
                return True
        return super().eventFilter(source, event)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'figure2') and hasattr(self, 'canvas2'):
            try:
                self.figure2.tight_layout()
                self.canvas2.draw_idle()
            except Exception:
                pass
