import numpy as np
import pandas as pd
import scipy.stats as stats

try:
    import statsmodels.api as sm
    import statsmodels.formula.api as smf
    HAS_STATSMODELS = True
except ImportError:
    HAS_STATSMODELS = False

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox,
    QTextEdit, QGroupBox, QFormLayout, QSplitter, QListWidget, QAbstractItemView,
    QLineEdit, QTabWidget, QSlider, QRadioButton, QButtonGroup, QScrollArea,
    QFrame, QGridLayout
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from knowledge_base import KnowledgeHubDialog

HYPOTHESIS_PRESETS = {
    "신약 임상시험 치료 효과 (A/B 집단, n=60)": lambda: pd.DataFrame({
        "대조군_혈압감소": np.round(np.random.normal(loc=3.5, scale=4.2, size=60), 1),
        "신약군_혈압감소": np.round(np.random.normal(loc=8.2, scale=4.0, size=60), 1),
        "투약전_혈압": np.round(np.random.normal(loc=142.0, scale=8.5, size=60), 1),
        "투약후_혈압": np.round(np.random.normal(loc=134.0, scale=7.8, size=60), 1)
    }),
    "마케팅 광고비 vs 매출액 (회귀/상관, n=50)": lambda: (lambda n=50, tv=np.round(np.random.uniform(10, 100, 50), 1): pd.DataFrame({
        "TV광고비": tv,
        "SNS광고비": np.round(np.random.uniform(5, 50, n), 1),
        "총매출액": np.round(25.0 + 1.8 * tv + 2.5 * np.random.uniform(5, 50, n) + np.random.normal(0, 12, n), 1)
    }))(),
    "학생 학업 성취도 및 수면시간 (ANOVA/상관, n=75)": lambda: (lambda n=75: pd.DataFrame({
        "시험점수": np.round(np.clip(np.random.normal(74, 12, n), 40, 100), 1),
        "일일공부시간": np.round(np.random.uniform(1.5, 8.0, n), 1),
        "수면시간": np.round(np.random.uniform(4.5, 9.0, n), 1),
        "학습방법_그룹": np.random.choice(["온라인강의", "독학", "학원스터디"], size=n)
    }))(),
    "기계 가공 공정 품질 A vs B (이표본/등분산, n=50)": lambda: pd.DataFrame({
        "공정A_치수오차": np.round(np.random.normal(0.02, 0.05, 50), 3),
        "공정B_치수오차": np.round(np.random.normal(0.08, 0.09, 50), 3)
    })
}

class HypothesisTab(QWidget):
    def __init__(self):
        super().__init__()
        self.df = None
        self.last_test_result = None # {type, stat, p, df, alpha, dist_func, alt, etc.}
        self.updating_alpha = False
        self.setup_ui()

    def setup_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        
        # 좌측 제어 패널 (스크롤)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumWidth(320)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(12)
        left_layout.setContentsMargins(5, 5, 10, 5)
        
        # 1. 데이터 로드 및 예제 프리셋
        data_group = QGroupBox("1. 데이터 입력 (다변량)")
        data_layout = QVBoxLayout()
        
        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("실무 예제:"))
        self.preset_combo = QComboBox()
        self.preset_combo.addItem("-- 다변량 샘플 데이터셋 선택 --", None)
        for p_name in HYPOTHESIS_PRESETS.keys():
            self.preset_combo.addItem(p_name, p_name)
        self.preset_combo.currentIndexChanged.connect(self.load_preset_data)
        preset_layout.addWidget(self.preset_combo)
        data_layout.addLayout(preset_layout)
        
        btn_layout = QHBoxLayout()
        self.btn_load = QPushButton("📂 파일 열기 (CSV/Excel/TXT)")
        self.btn_load.setCursor(Qt.PointingHandCursor)
        self.btn_clear = QPushButton("🗑️ 초기화")
        self.btn_clear.setCursor(Qt.PointingHandCursor)
        btn_layout.addWidget(self.btn_load)
        btn_layout.addWidget(self.btn_clear)
        data_layout.addLayout(btn_layout)
        
        self.table = QTableWidget()
        self.table.setMinimumHeight(110)
        self.table.setMaximumHeight(220)
        data_layout.addWidget(self.table)
        data_group.setLayout(data_layout)
        left_layout.addWidget(data_group)
        
        # 2. 검정 종류 선택
        type_group = QGroupBox("2. 검정 및 분석 종류")
        type_layout = QFormLayout()
        
        self.cat_combo = QComboBox()
        self.cat_combo.addItems([
            "평균 검정 (T-Test 등)", 
            "분산 검정 (F-Test 등)", 
            "비율 검정 (Proportion Test)",
            "분포/비모수 검정 (Normality 등)", 
            "분산분석 (ANOVA)", 
            "상관분석 (Correlation)", 
            "회귀분석 (Regression)"
        ])
        
        self.test_combo = QComboBox()
        type_layout.addRow("분석 범주:", self.cat_combo)
        type_layout.addRow("상세 분석:", self.test_combo)
        
        kb_layout = QHBoxLayout()
        self.btn_open_kb = QPushButton("📚 통계 가설 검정 지식 사전 열기")
        self.btn_open_kb.setProperty("btnClass", "primary")
        self.btn_open_kb.setCursor(Qt.PointingHandCursor)
        self.btn_open_kb.clicked.connect(self.open_knowledge_hub)
        kb_layout.addWidget(self.btn_open_kb)
        type_layout.addRow(kb_layout)
        
        type_group.setLayout(type_layout)
        left_layout.addWidget(type_group)
        
        # 3. 변수 할당
        var_group = QGroupBox("3. 변수 선택")
        var_layout = QVBoxLayout()
        
        self.lbl_v1 = QLabel("검정 변수 (종속 변수 Y / 그룹 1):")
        self.var1_combo = QComboBox()
        var_layout.addWidget(self.lbl_v1)
        var_layout.addWidget(self.var1_combo)
        
        # 검정 기준 모수 입력란 (동적)
        self.param_widget = QWidget()
        param_layout = QFormLayout(self.param_widget)
        param_layout.setContentsMargins(0, 4, 0, 4)
        self.lbl_param = QLabel("기준 모수 (H₀):")
        self.param_input = QLineEdit("0")
        param_layout.addRow(self.lbl_param, self.param_input)
        var_layout.addWidget(self.param_widget)

        # 변수 2 리스트 영역
        self.var2_widget = QWidget()
        list_layout = QVBoxLayout(self.var2_widget)
        list_layout.setContentsMargins(0, 0, 0, 0)
        self.lbl_v2 = QLabel("비교 변수 (독립 변수 X / 그룹 2 등):")
        self.var2_list = QListWidget()
        self.var2_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.var2_list.setFixedHeight(85)
        list_layout.addWidget(self.lbl_v2)
        list_layout.addWidget(self.var2_list)
        var_layout.addWidget(self.var2_widget)
        
        var_group.setLayout(var_layout)
        left_layout.addWidget(var_group)
        
        # 4. 가설 방향 및 대립가설 (Alternative Hypothesis)
        self.alt_group = QGroupBox("4. 가설 방향 및 대립가설 (Alternative)")
        alt_layout = QVBoxLayout()
        
        radio_layout = QHBoxLayout()
        self.radio_two_sided = QRadioButton("양측 검정 (≠)")
        self.radio_greater = QRadioButton("우측 단측 (>)")
        self.radio_less = QRadioButton("좌측 단측 (<)")
        self.radio_two_sided.setChecked(True)
        
        self.alt_btn_group = QButtonGroup(self)
        self.alt_btn_group.addButton(self.radio_two_sided, 0)
        self.alt_btn_group.addButton(self.radio_greater, 1)
        self.alt_btn_group.addButton(self.radio_less, 2)
        
        radio_layout.addWidget(self.radio_two_sided)
        radio_layout.addWidget(self.radio_greater)
        radio_layout.addWidget(self.radio_less)
        alt_layout.addLayout(radio_layout)
        
        self.lbl_hypo_preview = QLabel("H1: 대립가설 설정")
        self.lbl_hypo_preview.setStyleSheet(
            "font-size: 8.5pt; color: #0d6efd; font-weight: bold; "
            "background: rgba(13, 110, 253, 0.08); padding: 6px; border-radius: 4px;"
        )
        self.lbl_hypo_preview.setWordWrap(True)
        alt_layout.addWidget(self.lbl_hypo_preview)
        
        self.alt_group.setLayout(alt_layout)
        left_layout.addWidget(self.alt_group)
        
        # 5. 인터랙티브 유의수준 (alpha) 슬라이더
        alpha_group = QGroupBox("5. 인터랙티브 유의수준 (Significance Level α)")
        alpha_layout = QVBoxLayout()
        
        alpha_top = QHBoxLayout()
        alpha_top.addWidget(QLabel("유의수준 (α):"))
        self.lbl_alpha_val = QLabel("0.050 (5%)")
        self.lbl_alpha_val.setStyleSheet("font-weight: bold; color: #dc3545; font-size: 10.5pt;")
        alpha_top.addWidget(self.lbl_alpha_val)
        alpha_top.addStretch()
        
        # 프리셋 버튼들
        self.btn_a01 = QPushButton("1% (0.01)")
        self.btn_a05 = QPushButton("5% (0.05)")
        self.btn_a10 = QPushButton("10% (0.10)")
        for b, val in [(self.btn_a01, 0.01), (self.btn_a05, 0.05), (self.btn_a10, 0.10)]:
            b.setFixedWidth(65)
            b.setCursor(Qt.PointingHandCursor)
            b.clicked.connect(lambda _, v=val: self.set_alpha_val(v))
            alpha_top.addWidget(b)
        alpha_layout.addLayout(alpha_top)
        
        self.slider_alpha = QSlider(Qt.Horizontal)
        self.slider_alpha.setRange(1, 200) # 0.001 to 0.200
        self.slider_alpha.setValue(50) # 0.050
        self.slider_alpha.valueChanged.connect(self.on_alpha_slider_changed)
        alpha_layout.addWidget(self.slider_alpha)
        
        alpha_hint = QLabel("💡 α 슬라이더를 움직이면 기각역(붉은색)과 임계값이 실시간 재계산됩니다.")
        alpha_hint.setStyleSheet("color: #666; font-size: 8pt;")
        alpha_layout.addWidget(alpha_hint)
        
        alpha_group.setLayout(alpha_layout)
        left_layout.addWidget(alpha_group)
        
        # 실행 & 내보내기 버튼
        self.btn_run = QPushButton("🚀 분석 실행 및 기각역 검정")
        self.btn_run.setProperty("btnClass", "primary")
        self.btn_run.setCursor(Qt.PointingHandCursor)
        self.btn_run.setMinimumHeight(42)
        left_layout.addWidget(self.btn_run)

        self.btn_export = QPushButton("차트 이미지 저장")
        self.btn_export.setProperty("btnClass", "secondary")
        self.btn_export.setCursor(Qt.PointingHandCursor)
        self.btn_export.setMinimumHeight(36)
        self.btn_export.clicked.connect(self.export_chart)
        self.btn_export.setEnabled(False)
        left_layout.addWidget(self.btn_export)

        left_layout.addStretch(1)
        scroll_area.setWidget(left_panel)
        
        # 우측 패널 (결과 출력 + 결론 카드 + 차트)
        right_panel = QWidget()
        right_panel.setMinimumWidth(350)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        # 상단 자연어 직관 결론 카드
        self.conclusion_card = QGroupBox("📋 가설 검정 결론 및 통계적 의사결정 리포트")
        self.conclusion_card.setFixedHeight(120)
        card_layout = QVBoxLayout(self.conclusion_card)
        self.lbl_hypo = QLabel("가설: -")
        self.lbl_hypo.setStyleSheet("font-weight: bold; color: #333;")
        self.lbl_hypo.setWordWrap(True)
        self.lbl_decision = QLabel("판정: 분석 대기 중")
        self.lbl_decision.setStyleSheet("font-size: 11pt; font-weight: bold; color: #0d6efd;")
        self.lbl_decision.setWordWrap(True)
        self.lbl_effect = QLabel("효과 크기 (Effect Size): -")
        self.lbl_effect.setStyleSheet("color: #198754; font-weight: bold;")
        self.lbl_effect.setWordWrap(True)
        
        card_layout.addWidget(self.lbl_hypo)
        card_layout.addWidget(self.lbl_decision)
        card_layout.addWidget(self.lbl_effect)
        right_layout.addWidget(self.conclusion_card)
        
        # 탭 (결과 텍스트 & 파이썬 코드)
        self.res_tabs = QTabWidget()
        self.res_tabs.setMinimumHeight(140)
        self.res_tabs.setMaximumHeight(260)
        
        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.result_text.setStyleSheet("font-family: Consolas, monospace; font-size: 9.5pt;")
        
        self.code_text = QTextEdit()
        self.code_text.setReadOnly(True)
        self.code_text.setStyleSheet("font-family: Consolas, monospace; font-size: 9.5pt;")
        
        self.res_tabs.addTab(self.result_text, "분석 결과 요약 (Report)")
        self.res_tabs.addTab(self.code_text, "Python 재현 코드 (Code)")
        right_layout.addWidget(self.res_tabs)
        
        # 차트 캔버스
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        right_layout.addWidget(self.canvas, stretch=1)
        
        self.splitter.addWidget(scroll_area)
        self.splitter.addWidget(right_panel)
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)
        self.splitter.setSizes([480, 800])
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        layout.addWidget(self.splitter)
        
        # 이벤트 연결
        self.cat_combo.currentIndexChanged.connect(self.update_tests)
        self.test_combo.currentIndexChanged.connect(self.update_var_ui)
        self.var1_combo.currentIndexChanged.connect(self.update_hypo_preview)
        self.var2_list.itemSelectionChanged.connect(self.update_hypo_preview)
        self.param_input.textChanged.connect(self.update_hypo_preview)
        
        self.radio_two_sided.toggled.connect(self.on_alt_changed)
        self.radio_greater.toggled.connect(self.on_alt_changed)
        self.radio_less.toggled.connect(self.on_alt_changed)

        self.btn_load.clicked.connect(self.load_data)
        self.btn_clear.clicked.connect(self.clear_data)
        self.btn_run.clicked.connect(self.run_analysis)
        
        self.update_tests()
        
        # 초기 예제 1개 로드
        self.preset_combo.setCurrentIndex(1)

    def load_preset_data(self):
        p_name = self.preset_combo.currentData()
        if not p_name or p_name not in HYPOTHESIS_PRESETS: return
        
        self.df = HYPOTHESIS_PRESETS[p_name]()
        self.update_table_and_combos()
        
        if "신약" in p_name:
            self.cat_combo.setCurrentIndex(0) # 평균 검정
            self.test_combo.setCurrentIndex(1) # 독립표본 t-검정
            self.var1_combo.setCurrentIndex(1)
            self.var2_list.setCurrentRow(1)
        elif "마케팅" in p_name:
            self.cat_combo.setCurrentIndex(6) # 회귀분석
            self.test_combo.setCurrentIndex(0)
            self.var1_combo.setCurrentIndex(3) # 총매출액
            self.var2_list.setCurrentRow(0)
        elif "학생" in p_name:
            self.cat_combo.setCurrentIndex(4) # 분산분석 (ANOVA)
            self.test_combo.setCurrentIndex(0)
            self.var1_combo.setCurrentIndex(1)
            self.var2_list.setCurrentRow(3)
        elif "기계" in p_name or "공정" in p_name:
            self.cat_combo.setCurrentIndex(1) # 분산 검정
            self.test_combo.setCurrentIndex(1) # F-검정
            self.var1_combo.setCurrentIndex(1)
            self.var2_list.setCurrentRow(1)
        self.update_hypo_preview()
        self.run_analysis()

    def open_knowledge_hub(self):
        dlg = KnowledgeHubDialog(self)
        dlg.exec()

    def set_alpha_val(self, val):
        self.slider_alpha.setValue(int(val * 1000))

    def on_alpha_slider_changed(self, val):
        alpha = val / 1000.0
        self.lbl_alpha_val.setText(f"{alpha:.3f} ({alpha*100:.1f}%)")
        if self.last_test_result is not None:
            self.redraw_sampling_distribution(alpha)

    def on_alt_changed(self):
        self.update_hypo_preview()
        if self.df is not None and not self.df.empty and self.last_test_result is not None:
            self.run_analysis()

    def get_alternative(self):
        if self.radio_greater.isChecked():
            return "greater", "우측 단측 검정", ">"
        elif self.radio_less.isChecked():
            return "less", "좌측 단측 검정", "<"
        else:
            return "two-sided", "양측 검정", "≠"

    def update_hypo_preview(self):
        cat = self.cat_combo.currentText()
        test = self.test_combo.currentText()
        alt, alt_name, alt_sym = self.get_alternative()
        v1 = self.var1_combo.currentText()
        v1_name = v1 if v1 != "선택안함" else "변수1"
        
        v2_items = [item.text() for item in self.var2_list.selectedItems()]
        v2_name = v2_items[0] if v2_items else "변수2"
        param_val = self.param_input.text().strip() or "0"

        # 방향 선택이 통계학적으로 제한되는 다집단 적합도 및 정규성 검정
        if any(term in test for term in ["ANOVA", "회귀", "Shapiro", "Kolmogorov", "Levene", "Bartlett"]):
            self.alt_group.setEnabled(False)
            if "ANOVA" in test or "회귀" in test:
                self.lbl_hypo_preview.setText("ℹ️ 다집단/회귀 모형 F-검정: 모형 유의성 및 적합도 검정 (상위 기각역 고정)")
            elif "Levene" in test or "Bartlett" in test:
                self.lbl_hypo_preview.setText("ℹ️ 등분산 다집단 검정: H0: 분산 모두 동일 vs H1: 적어도 한 집단 분산 다름")
            else:
                self.lbl_hypo_preview.setText("ℹ️ 정규성 검정: H0: 정규분포를 따름 vs H1: 정규분포를 따르지 않음")
            return

        self.alt_group.setEnabled(True)

        if "평균 검정" in cat:
            if "One-sample" in test:
                h0_sym = "=" if alt == "two-sided" else ("≤" if alt == "greater" else "≥")
                self.lbl_hypo_preview.setText(f"H0: μ({v1_name}) {h0_sym} {param_val}  vs  H1: μ({v1_name}) {alt_sym} {param_val} ({alt_name})")
            elif "Two-sample independent" in test:
                h0_sym = "=" if alt == "two-sided" else ("≤" if alt == "greater" else "≥")
                self.lbl_hypo_preview.setText(f"H0: μ({v1_name}) {h0_sym} μ({v2_name})  vs  H1: μ({v1_name}) {alt_sym} μ({v2_name}) ({alt_name})")
            elif "Two-sample paired" in test:
                h0_sym = "= 0" if alt == "two-sided" else ("≤ 0" if alt == "greater" else "≥ 0")
                h1_sym = "≠ 0" if alt == "two-sided" else ("> 0" if alt == "greater" else "< 0")
                self.lbl_hypo_preview.setText(f"H0: μ_diff({v1_name} - {v2_name}) {h0_sym}  vs  H1: μ_diff {h1_sym} ({alt_name})")
        elif "분산 검정" in cat:
            if "F-" in test:
                h0_sym = "=" if alt == "two-sided" else ("≤" if alt == "greater" else "≥")
                self.lbl_hypo_preview.setText(f"H0: σ²({v1_name}) {h0_sym} σ²({v2_name})  vs  H1: σ²({v1_name}) {alt_sym} σ²({v2_name}) ({alt_name})")
            else:
                h0_sym = "=" if alt == "two-sided" else ("≤" if alt == "greater" else "≥")
                self.lbl_hypo_preview.setText(f"H0: σ²({v1_name}) {h0_sym} {param_val}  vs  H1: σ²({v1_name}) {alt_sym} {param_val} ({alt_name})")
        elif "비율 검정" in cat:
            if "일표본" in test:
                h0_sym = "=" if alt == "two-sided" else ("≤" if alt == "greater" else "≥")
                self.lbl_hypo_preview.setText(f"H0: p({v1_name}) {h0_sym} {param_val}  vs  H1: p({v1_name}) {alt_sym} {param_val} ({alt_name})")
            else:
                h0_sym = "=" if alt == "two-sided" else ("≤" if alt == "greater" else "≥")
                self.lbl_hypo_preview.setText(f"H0: p({v1_name}) {h0_sym} p({v2_name})  vs  H1: p({v1_name}) {alt_sym} p({v2_name}) ({alt_name})")
        elif "상관분석" in cat:
            h0_sym = "= 0" if alt == "two-sided" else ("≤ 0" if alt == "greater" else "≥ 0")
            h1_sym = "≠ 0" if alt == "two-sided" else ("> 0 (양의 상관)" if alt == "greater" else "< 0 (음의 상관)")
            self.lbl_hypo_preview.setText(f"H0: ρ({v1_name}, {v2_name}) {h0_sym}  vs  H1: ρ {h1_sym} ({alt_name})")
        elif "분포/비모수" in cat:
            if "Mann-Whitney" in test:
                h0_sym = "=" if alt == "two-sided" else ("≤" if alt == "greater" else "≥")
                self.lbl_hypo_preview.setText(f"H0: 분포({v1_name}) {h0_sym} 분포({v2_name})  vs  H1: 분포({v1_name}) {alt_sym} 분포({v2_name}) ({alt_name})")
            else:
                self.lbl_hypo_preview.setText("ℹ️ 정규성 검정: H0: 정규분포를 따름 vs H1: 정규분포를 따르지 않음")
        else:
            self.lbl_hypo_preview.setText(f"가설: {alt_name} ({alt_sym})")

    def update_tests(self):
        cat = self.cat_combo.currentText()
        self.test_combo.clear()
        
        if "평균 검정" in cat:
            self.test_combo.addItems([
                "일표본 t-검정 (One-sample)", 
                "독립표본 t-검정 (Two-sample independent)", 
                "대응표본 t-검정 (Two-sample paired)"
            ])
        elif "분산 검정" in cat:
            self.test_combo.addItems([
                "일표본 분산 검정 (Chi-square 모분산)",
                "F-검정 (F-test 두 집단 분산)", 
                "Levene 검정 (다집단 등분산)", 
                "Bartlett 검정 (다집단 등분산, 정규성 가정)"
            ])
        elif "비율 검정" in cat:
            self.test_combo.addItems([
                "일표본 비율 검정 (Z-test 표본비율 vs 모비율)",
                "이표본 비율 검정 (Z-test 두 집단간 검정)"
            ])
        elif "분포/비모수" in cat:
            self.test_combo.addItems([
                "정규성 검정 (Shapiro-Wilk)", 
                "정규성 검정 (Kolmogorov-Smirnov)",
                "Mann-Whitney U 검정 (비모수 2집단)"
            ])
        elif "분산분석" in cat:
            self.test_combo.addItems([
                "일원배치 분산분석 (One-way ANOVA) - 요인별",
                "일원배치 분산분석 (One-way ANOVA) - 전체 다중비교"
            ])
        elif "상관분석" in cat:
            self.test_combo.addItems([
                "Pearson 상관계수", 
                "Spearman 순위 상관계수"
            ])
        elif "회귀분석" in cat:
            self.test_combo.addItems([
                "단순 선형 회귀분석 (Simple OLS)", 
                "다중 선형 회귀분석 (Multiple OLS)", 
                "로지스틱 회귀분석 (Logistic)"
            ])
            
        self.update_var_ui()

    def update_var_ui(self):
        cat = self.cat_combo.currentText()
        test = self.test_combo.currentText()
        
        self.param_widget.setVisible(False)
        self.var2_widget.setVisible(True)
        self.lbl_v1.setText("종속 변수 Y (또는 그룹 1):")
        self.lbl_v2.setText("독립 변수 X (또는 그룹 2):")
        
        if "일표본" in test or "정규성" in test:
            self.var2_widget.setVisible(False)
            self.param_widget.setVisible(True)
            self.lbl_v1.setText("검정 대상 변수 (X):")
            
            if "평균" in cat:
                self.lbl_param.setText("기준 귀무평균 (μ0):")
                self.param_input.setText("0")
            elif "분산" in cat:
                self.lbl_param.setText("기준 귀무모분산 (σ²0):")
                self.param_input.setText("1")
            elif "비율" in cat:
                self.lbl_param.setText("기준 귀무모비율 (P0):")
                self.param_input.setText("0.5")
            else:
                self.param_widget.setVisible(False)
                
        elif "이표본" in test or "독립표본" in test or "대응표본" in test or "F-검정" in test:
            self.lbl_v1.setText("비교 변수 1 (그룹 1 / Y1):")
            self.lbl_v2.setText("비교 변수 2 (목록에서 1개 선택):")
        
        elif "상관분석" in cat:
            self.lbl_v1.setText("변수 1 (X 축):")
            self.lbl_v2.setText("변수 2 (Y 축):")
            
        elif "ANOVA" in test:
            if "다중비교" in test:
                self.lbl_v1.setText("기준 변수 (그룹 1):")
                self.lbl_v2.setText("추가 비교 변수들 (다중 선택):")
            else:
                self.lbl_v1.setText("연속형 종속 변수 (Y):")
                self.lbl_v2.setText("범주형 그룹 요인 (Factor, 1개):")
                
        elif "회귀분석" in cat:
            self.lbl_v1.setText("종속 변수 (Y / 반응 변수):")
            self.lbl_v2.setText("독립 변수 (X / 다중 선택 가능):")

        self.update_hypo_preview()

    def load_data(self):
        fname, _ = QFileDialog.getOpenFileName(self, "데이터 열기", "", "Excel (*.xlsx *.xls);;CSV (*.csv);;Text (*.txt)")
        if not fname: return
        try:
            if fname.endswith('xlsx') or fname.endswith('xls'):
                self.df = pd.read_excel(fname)
            elif fname.endswith('csv'):
                self.df = pd.read_csv(fname)
            else:
                self.df = pd.read_csv(fname, sep=r'\s+')
            self.update_table_and_combos()
        except Exception as e:
            QMessageBox.warning(self, "파일 열기 오류", f"데이터를 로드하는 중 오류가 발생했습니다:\n{e}")

    def clear_data(self):
        self.df = None
        self.table.setRowCount(0)
        self.table.setColumnCount(0)
        self.var1_combo.clear()
        self.var2_list.clear()
        self.figure.clear()
        self.canvas.draw()
        self.btn_export.setEnabled(False)
        self.lbl_hypo.setText("가설: -")
        self.lbl_decision.setText("판정: 초기화됨")
        self.lbl_effect.setText("효과 크기: -")
        self.last_test_result = None

    def export_chart(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "차트 이미지 저장", "", 
            "PNG Files (*.png);;JPEG Files (*.jpg);;PDF Files (*.pdf);;All Files (*)"
        )
        if file_path:
            try:
                self.figure.savefig(file_path, dpi=300, bbox_inches='tight')
                QMessageBox.information(self, "저장 완료", f"차트가 성공적으로 저장되었습니다:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "저장 실패", f"차트를 저장하는 중 오류가 발생했습니다:\n{str(e)}")

    def update_table_and_combos(self):
        if self.df is None or self.df.empty: return
        columns = [str(c) for c in self.df.columns]
        
        self.table.setColumnCount(len(columns))
        self.table.setHorizontalHeaderLabels(columns)
        self.table.setRowCount(min(len(self.df), 50))
        
        for i, row in self.df.head(50).iterrows():
            for j, val in enumerate(row):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))
                
        self.var1_combo.clear()
        self.var2_list.clear()
        self.var1_combo.addItems(["선택안함"] + columns)
        self.var2_list.addItems(columns)

    def out(self, text):
        self.result_text.append(text)
        
    def out_code(self, text):
        self.code_text.append(text)

    def run_analysis(self):
        if self.df is None or self.df.empty:
            QMessageBox.warning(self, "오류", "먼저 데이터를 로드해주세요.")
            return
            
        cat = self.cat_combo.currentText()
        test = self.test_combo.currentText()
        v1 = self.var1_combo.currentText()
        v2_items = [item.text() for item in self.var2_list.selectedItems()]
        
        self.result_text.clear()
        self.code_text.clear()
        alpha = self.slider_alpha.value() / 1000.0
        alt, alt_kr, alt_sym = self.get_alternative()
        
        self.out_code(f"### {cat} > {test} [{alt_kr}] ###")
        self.out_code("import pandas as pd, numpy as np, scipy.stats as stats")
        
        try:
            if "평균 검정" in cat:
                if "One-sample" in test:
                    if v1 == "선택안함": raise ValueError("검정 대상 변수를 선택하세요.")
                    mu0 = float(self.param_input.text() or 0)
                    data = pd.to_numeric(self.df[v1], errors='coerce').dropna()
                    n = len(data)
                    stat, p = stats.ttest_1samp(data, popmean=mu0, alternative=alt)
                    df = n - 1
                    cohen_d = (np.mean(data) - mu0) / (np.std(data, ddof=1) or 1)
                    
                    h0_txt = f"H0: μ = {mu0} vs H1: μ {alt_sym} {mu0} ({alt_kr})"
                    self.last_test_result = {
                        "dist": "t", "df": df, "stat": stat, "p": p, "alpha": alpha, "alt": alt,
                        "title": f"일표본 t-검정 표본분포 (df={df}, {alt_kr})",
                        "h0": h0_txt,
                        "effect": f"Cohen's d = {cohen_d:.3f} ({self.interpret_cohen_d(cohen_d)})",
                        "data": data, "v1": v1
                    }
                    self.out(f"[일표본 t-검정 ({alt_kr})]\n변수: {v1} (기준 귀무평균 μ0 = {mu0})\n"
                             f"표본평균 = {np.mean(data):.4f} (표준편차: {np.std(data, ddof=1):.4f}, N={n})\n"
                             f"t-통계량 = {stat:.4f}, 자유도 = {df}\n"
                             f"p-value = {p:.4e}, 유의수준 α = {alpha:.3f}\n"
                             f"Cohen's d = {cohen_d:.3f}")
                    self.out_code(f"data = df['{v1}'].dropna()\nstat, p = stats.ttest_1samp(data, popmean={mu0}, alternative='{alt}')\nprint(f't={stat:.4f}, p={p:.4e}')")
                    
                elif "Two-sample independent" in test:
                    if v1 == "선택안함" or not v2_items: raise ValueError("두 개의 비교 변수를 선택하세요.")
                    v2 = v2_items[0]
                    d1 = pd.to_numeric(self.df[v1], errors='coerce').dropna()
                    d2 = pd.to_numeric(self.df[v2], errors='coerce').dropna()
                    stat, p = stats.ttest_ind(d1, d2, equal_var=False, alternative=alt)
                    n1, n2 = len(d1), len(d2)
                    s1, s2 = np.std(d1, ddof=1), np.std(d2, ddof=1)
                    v_1, v_2 = (s1**2)/n1, (s2**2)/n2
                    df_welch = ((v_1 + v_2)**2) / ((v_1**2)/(n1-1) + (v_2**2)/(n2-1)) if (v_1 + v_2) > 0 else (n1+n2-2)
                    s_pooled = np.sqrt(((n1-1)*(s1**2) + (n2-1)*(s2**2)) / (n1+n2-2))
                    cohen_d = (np.mean(d1) - np.mean(d2)) / (s_pooled or 1)
                    
                    h0_txt = f"H0: μ({v1}) = μ({v2}) vs H1: μ({v1}) {alt_sym} μ({v2}) ({alt_kr})"
                    self.last_test_result = {
                        "dist": "t", "df": df_welch, "stat": stat, "p": p, "alpha": alpha, "alt": alt,
                        "title": f"독립표본 t-검정 표본분포 (Welch, {alt_kr})",
                        "h0": h0_txt,
                        "effect": f"Cohen's d = {cohen_d:.3f} ({self.interpret_cohen_d(cohen_d)})",
                        "groups": [d1, d2], "labels": [v1, v2]
                    }
                    self.out(f"[독립표본 t-검정 (Welch, {alt_kr})]\n"
                             f"그룹1 ({v1}): mean={np.mean(d1):.4f}, std={s1:.4f}, n={n1}\n"
                             f"그룹2 ({v2}): mean={np.mean(d2):.4f}, std={s2:.4f}, n={n2}\n"
                             f"t-통계량 = {stat:.4f}, Welch 자유도 = {df_welch:.2f}\n"
                             f"p-value = {p:.4e}, 유의수준 α = {alpha:.3f}\n"
                             f"Cohen's d = {cohen_d:.3f}")
                    self.out_code(f"d1 = df['{v1}'].dropna()\nd2 = df['{v2}'].dropna()\nstat, p = stats.ttest_ind(d1, d2, equal_var=False, alternative='{alt}')\nprint(f't={stat:.4f}, p={p:.4e}')")
                    
                elif "Two-sample paired" in test:
                    if v1 == "선택안함" or not v2_items: raise ValueError("두 개의 대응 변수를 선택하세요.")
                    v2 = v2_items[0]
                    valid = self.df[[v1, v2]].apply(pd.to_numeric, errors='coerce').dropna()
                    diff = valid[v1] - valid[v2]
                    stat, p = stats.ttest_rel(valid[v1], valid[v2], alternative=alt)
                    df = len(valid) - 1
                    cohen_d = np.mean(diff) / (np.std(diff, ddof=1) or 1)
                    
                    h0_txt = f"H0: μ_diff = 0 vs H1: μ_diff {alt_sym} 0 ({alt_kr})"
                    self.last_test_result = {
                        "dist": "t", "df": df, "stat": stat, "p": p, "alpha": alpha, "alt": alt,
                        "title": f"대응표본 t-검정 표본분포 (차이값 df={df}, {alt_kr})",
                        "h0": h0_txt,
                        "effect": f"Cohen's d = {cohen_d:.3f} ({self.interpret_cohen_d(cohen_d)})",
                        "diff": diff
                    }
                    self.out(f"[대응표본 t-검정 ({alt_kr})]\n변수쌍: {v1} - {v2} (N={len(valid)})\n"
                             f"평균 차이(Mean Diff) = {np.mean(diff):.4f}, 표준편차 = {np.std(diff, ddof=1):.4f}\n"
                             f"t-통계량 = {stat:.4f}, 자유도 = {df}\n"
                             f"p-value = {p:.4e}, 유의수준 α = {alpha:.3f}\n"
                             f"Cohen's d = {cohen_d:.3f}")
                    self.out_code(f"valid = df[['{v1}', '{v2}']].dropna()\nstat, p = stats.ttest_rel(valid['{v1}'], valid['{v2}'], alternative='{alt}')\nprint(f't={stat:.4f}, p={p:.4e}')")

            elif "분산 검정" in cat:
                if "F-" in test:
                    if v1 == "선택안함" or not v2_items: raise ValueError("두 개의 비교 변수를 선택하세요.")
                    v2 = v2_items[0]
                    d1 = pd.to_numeric(self.df[v1], errors='coerce').dropna()
                    d2 = pd.to_numeric(self.df[v2], errors='coerce').dropna()
                    var1, var2 = np.var(d1, ddof=1), np.var(d2, ddof=1)
                    f_stat = var1 / var2 if var2 > 0 else 1.0
                    df1, df2 = len(d1)-1, len(d2)-1
                    
                    if alt == "two-sided":
                        p = 2 * min(stats.f.cdf(f_stat, df1, df2), stats.f.sf(f_stat, df1, df2))
                        h0_txt = f"H0: σ1² = σ2² vs H1: σ1² ≠ σ2² ({alt_kr})"
                    elif alt == "greater":
                        p = stats.f.sf(f_stat, df1, df2)
                        h0_txt = f"H0: σ1² ≤ σ2² vs H1: σ1² > σ2² ({alt_kr})"
                    else: # less
                        p = stats.f.cdf(f_stat, df1, df2)
                        h0_txt = f"H0: σ1² ≥ σ2² vs H1: σ1² < σ2² ({alt_kr})"
                    p = min(max(p, 0.0), 1.0)
                    
                    self.last_test_result = {
                        "dist": "f", "df1": df1, "df2": df2, "stat": f_stat, "p": p, "alpha": alpha, "alt": alt,
                        "title": f"F-분포 두 집단 분산 검정 ({alt_kr}, df1={df1}, df2={df2})",
                        "h0": h0_txt,
                        "effect": f"분산비율 F = {f_stat:.3f} (s1²={var1:.3f}, s2²={var2:.3f})",
                        "groups": [d1, d2], "labels": [v1, v2]
                    }
                    self.out(f"[두 집단 분산 F-검정 ({alt_kr})]\n"
                             f"그룹1 ({v1}): s1²={var1:.4f} (df1={df1})\n"
                             f"그룹2 ({v2}): s2²={var2:.4f} (df2={df2})\n"
                             f"F-통계량 = {f_stat:.4f}, p-value = {p:.4e}, 유의수준 α = {alpha:.3f}")
                    self.out_code(f"v1 = np.var(df['{v1}'].dropna(), ddof=1)\nv2 = np.var(df['{v2}'].dropna(), ddof=1)\nf_val = v1 / v2\nprint(f'F-statistic = {{f_val:.4f}}, p-value = {p:.4e}')")
                elif "일표본" in test:
                    if v1 == "선택안함": raise ValueError("검정 대상 변수를 선택하세요.")
                    var0 = float(self.param_input.text() or 1)
                    data = pd.to_numeric(self.df[v1], errors='coerce').dropna()
                    n = len(data)
                    s2 = np.var(data, ddof=1)
                    df = n - 1
                    chi2_stat = df * s2 / var0
                    
                    if alt == "two-sided":
                        p = 2 * min(stats.chi2.cdf(chi2_stat, df), stats.chi2.sf(chi2_stat, df))
                        h0_txt = f"H0: σ² = {var0} vs H1: σ² ≠ {var0} ({alt_kr})"
                    elif alt == "greater":
                        p = stats.chi2.sf(chi2_stat, df)
                        h0_txt = f"H0: σ² ≤ {var0} vs H1: σ² > {var0} ({alt_kr})"
                    else: # less
                        p = stats.chi2.cdf(chi2_stat, df)
                        h0_txt = f"H0: σ² ≥ {var0} vs H1: σ² < {var0} ({alt_kr})"
                    p = min(max(p, 0.0), 1.0)
                    
                    self.last_test_result = {
                        "dist": "chi2", "df": df, "stat": chi2_stat, "p": p, "alpha": alpha, "alt": alt,
                        "title": f"카이제곱 모분산 검정 ({alt_kr}, df={df})",
                        "h0": h0_txt,
                        "effect": f"표본분산 s² = {s2:.3f} (기준 모분산 σ0² = {var0})",
                        "data": data, "v1": v1
                    }
                    self.out(f"[모분산 카이제곱 검정 ({alt_kr})]\n변수: {v1} (기준 귀무모분산 σ0² = {var0})\n"
                             f"표본분산 s² = {s2:.4f}, N = {n}, 자유도 = {df}\n"
                             f"Chi2-통계량 = {chi2_stat:.4f}, p-value = {p:.4e}, 유의수준 α = {alpha:.3f}")
                    self.out_code(f"data = df['{v1}'].dropna()\ns2 = np.var(data, ddof=1)\nchi2_val = (len(data)-1)*s2 / {var0}\nprint(f'Chi2 = {{chi2_val:.4f}}, p-value = {p:.4e}')")
                else: # Levene / Bartlett
                    if v1 == "선택안함": raise ValueError("기준 변수를 선택하세요.")
                    cols = [v1] + v2_items
                    groups = [pd.to_numeric(self.df[c], errors='coerce').dropna().values for c in cols]
                    if "Levene" in test:
                        stat, p = stats.levene(*groups)
                        t_name = "Levene 등분산 검정"
                    else:
                        stat, p = stats.bartlett(*groups)
                        t_name = "Bartlett 등분산 검정"
                    self.last_test_result = {
                        "dist": "custom", "stat": stat, "p": p, "alpha": alpha, "alt": "greater",
                        "title": f"{t_name} ({', '.join(cols)})",
                        "h0": "H0: 모든 그룹의 모분산은 동일하다 vs H1: 적어도 한 그룹의 모분산은 다르다",
                        "effect": f"검정통계량 = {stat:.4f}",
                        "groups": groups, "labels": cols
                    }
                    self.out(f"[{t_name}]\n통계량 = {stat:.4f}, p-value = {p:.4e}")

            elif "비율 검정" in cat:
                if "일표본" in test:
                    if v1 == "선택안함": raise ValueError("검정 대상 변수를 선택하세요.")
                    p0 = float(self.param_input.text() or 0.5)
                    data = pd.to_numeric(self.df[v1], errors='coerce').dropna()
                    n = len(data)
                    p_hat = np.mean(data)
                    se = np.sqrt(p0 * (1 - p0) / n) if p0 * (1 - p0) > 0 else 1e-6
                    z_stat = (p_hat - p0) / se
                    if alt == "two-sided":
                        p = 2 * (1 - stats.norm.cdf(abs(z_stat)))
                        h0_txt = f"H0: p = {p0} vs H1: p ≠ {p0} ({alt_kr})"
                    elif alt == "greater":
                        p = stats.norm.sf(z_stat)
                        h0_txt = f"H0: p ≤ {p0} vs H1: p > {p0} ({alt_kr})"
                    else:
                        p = stats.norm.cdf(z_stat)
                        h0_txt = f"H0: p ≥ {p0} vs H1: p < {p0} ({alt_kr})"
                    p = min(max(p, 0.0), 1.0)
                    
                    self.last_test_result = {
                        "dist": "z", "stat": z_stat, "p": p, "alpha": alpha, "alt": alt,
                        "title": f"일표본 비율 Z-검정 ({alt_kr})",
                        "h0": h0_txt,
                        "effect": f"표본비율 p̂ = {p_hat:.4f} (기준 p0 = {p0})",
                        "data": data, "v1": v1
                    }
                    self.out(f"[일표본 비율 Z-검정 ({alt_kr})]\n변수: {v1} (기준 귀무모비율 p0 = {p0})\n"
                             f"표본비율 p̂ = {p_hat:.4f}, 표본크기 N = {n}\n"
                             f"Z-통계량 = {z_stat:.4f}, p-value = {p:.4e}, 유의수준 α = {alpha:.3f}")
                    self.out_code(f"data = df['{v1}'].dropna()\np_hat = np.mean(data)\nse = np.sqrt({p0}*(1-{p0})/len(data))\nz_val = (p_hat - {p0})/se\nprint(f'Z = {{z_val:.4f}}, p-value = {p:.4e}')")
                else: # 이표본 비율 검정
                    if v1 == "선택안함" or not v2_items: raise ValueError("두 개의 비교 변수를 선택하세요.")
                    v2 = v2_items[0]
                    d1 = pd.to_numeric(self.df[v1], errors='coerce').dropna()
                    d2 = pd.to_numeric(self.df[v2], errors='coerce').dropna()
                    n1, n2 = len(d1), len(d2)
                    p1, p2 = np.mean(d1), np.mean(d2)
                    p_c = (np.sum(d1) + np.sum(d2)) / (n1 + n2)
                    se = np.sqrt(p_c * (1 - p_c) * (1/n1 + 1/n2)) if p_c * (1 - p_c) > 0 else 1e-6
                    z_stat = (p1 - p2) / se
                    if alt == "two-sided":
                        p = 2 * (1 - stats.norm.cdf(abs(z_stat)))
                        h0_txt = f"H0: p1 = p2 vs H1: p1 ≠ p2 ({alt_kr})"
                    elif alt == "greater":
                        p = stats.norm.sf(z_stat)
                        h0_txt = f"H0: p1 ≤ p2 vs H1: p1 > p2 ({alt_kr})"
                    else:
                        p = stats.norm.cdf(z_stat)
                        h0_txt = f"H0: p1 ≥ p2 vs H1: p1 < p2 ({alt_kr})"
                    p = min(max(p, 0.0), 1.0)
                    
                    self.last_test_result = {
                        "dist": "z", "stat": z_stat, "p": p, "alpha": alpha, "alt": alt,
                        "title": f"이표본 비율 Z-검정 ({alt_kr}: {v1} vs {v2})",
                        "h0": h0_txt,
                        "effect": f"비율 차이 (p1 - p2) = {p1 - p2:.4f} (p1={p1:.3f}, p2={p2:.3f})",
                        "groups": [d1, d2], "labels": [v1, v2]
                    }
                    self.out(f"[이표본 비율 Z-검정 ({alt_kr})]\n"
                             f"그룹1 ({v1}): p1={p1:.4f}, n1={n1}\n"
                             f"그룹2 ({v2}): p2={p2:.4f}, n2={n2}\n"
                             f"Z-통계량 = {z_stat:.4f}, p-value = {p:.4e}, 유의수준 α = {alpha:.3f}")
                    self.out_code(f"d1, d2 = df['{v1}'].dropna(), df['{v2}'].dropna()\np1, p2 = np.mean(d1), np.mean(d2)\np_c = (np.sum(d1)+np.sum(d2))/(len(d1)+len(d2))\nse = np.sqrt(p_c*(1-p_c)*(1/len(d1)+1/len(d2)))\nz_val = (p1 - p2)/se\nprint(f'Z = {{z_val:.4f}}, p-value = {p:.4e}')")

            elif "상관분석" in cat:
                if v1 == "선택안함" or not v2_items: raise ValueError("두 변수를 선택하세요.")
                v2 = v2_items[0]
                valid = self.df[[v1, v2]].apply(pd.to_numeric, errors='coerce').dropna()
                r, p = stats.pearsonr(valid[v1], valid[v2], alternative=alt) if "Pearson" in test else stats.spearmanr(valid[v1], valid[v2], alternative=alt)
                n = len(valid)
                t_stat = r * np.sqrt((n-2)/(1-r**2)) if abs(r) < 1 else (100.0 if r > 0 else -100.0)
                
                h0_txt = f"H0: ρ = 0 vs H1: ρ {alt_sym} 0 ({alt_kr})"
                self.last_test_result = {
                    "dist": "t", "df": n-2, "stat": t_stat, "p": p, "alpha": alpha, "alt": alt,
                    "title": f"상관계수 유의성 검정 ({alt_kr}, df={n-2})",
                    "h0": h0_txt,
                    "effect": f"상관계수 r = {r:.3f} (결정계수 R² = {r**2:.3f})",
                    "scatter": (valid[v2], valid[v1], v2, v1)
                }
                self.out(f"[상관분석 ({test}, {alt_kr})]\n상관계수 = {r:.4f}, t-통계량 = {t_stat:.4f}, p-value = {p:.4e}")

            elif "분산분석" in cat:
                if v1 == "선택안함": raise ValueError("종속 변수를 선택하세요.")
                if "요인별" in test and v2_items:
                    v2 = v2_items[0]
                    valid = self.df[[v1, v2]].dropna()
                    valid[v1] = pd.to_numeric(valid[v1], errors='coerce')
                    valid = valid.dropna()
                    groups = [g[v1].values for _, g in valid.groupby(v2)]
                    labels = [str(n) for n, _ in valid.groupby(v2)]
                else:
                    cols = [v1] + v2_items
                    groups = [pd.to_numeric(self.df[c], errors='coerce').dropna().values for c in cols]
                    labels = cols
                    
                stat, p = stats.f_oneway(*groups)
                k = len(groups)
                N = sum(len(g) for g in groups)
                df1 = k - 1
                df2 = N - k
                
                grand_mean = np.mean(np.concatenate(groups))
                ss_between = sum(len(g) * (np.mean(g) - grand_mean)**2 for g in groups)
                ss_total = sum(np.sum((g - grand_mean)**2) for g in groups)
                eta_sq = ss_between / (ss_total or 1)
                
                self.last_test_result = {
                    "dist": "f", "df1": df1, "df2": df2, "stat": stat, "p": p, "alpha": alpha, "alt": "greater",
                    "title": f"ANOVA F-검정 표본분포 (df1={df1}, df2={df2})",
                    "h0": "H0: 모든 그룹의 모평균은 동일하다 vs H1: 적어도 한 그룹은 다르다",
                    "effect": f"에타제곱 η² = {eta_sq:.3f} ({self.interpret_eta_sq(eta_sq)})",
                    "groups": groups, "labels": labels
                }
                self.out(f"[One-way ANOVA]\nF-통계량 = {stat:.4f}, p-value = {p:.4e}, η² = {eta_sq:.4f}")

            elif "회귀분석" in cat:
                if not HAS_STATSMODELS: raise ImportError("statsmodels 가 필요합니다.")
                if v1 == "선택안함" or not v2_items: raise ValueError("종속변수와 독립변수를 선택하세요.")
                y = pd.to_numeric(self.df[v1], errors='coerce')
                X = self.df[v2_items].apply(pd.to_numeric, errors='coerce')
                common = pd.concat([y, X], axis=1).dropna()
                Y_data = common[v1]
                X_data = sm.add_constant(common.drop(columns=[v1]))
                
                model = sm.OLS(Y_data, X_data).fit()
                self.out(model.summary().as_text())
                
                f_stat = model.fvalue
                f_p = model.f_pvalue
                df1 = int(model.df_model)
                df2 = int(model.df_resid)
                
                self.last_test_result = {
                    "dist": "f", "df1": df1, "df2": df2, "stat": f_stat, "p": f_p, "alpha": alpha, "alt": "greater",
                    "title": f"회귀모형 전체 유의성 F-검정 (df1={df1}, df2={df2})",
                    "h0": "H0: 모든 회귀계수는 0이다 vs H1: 적어도 하나의 회귀계수는 0이 아니다",
                    "effect": f"결정계수 R² = {model.rsquared:.3f} (수정 R² = {model.rsquared_adj:.3f})",
                    "regression": (common[v2_items[0]], Y_data, model.predict(X_data), v2_items[0], v1)
                }

            elif "분포/비모수" in cat:
                if "Mann-Whitney" in test:
                    if v1 == "선택안함" or not v2_items: raise ValueError("두 개의 비교 변수를 선택하세요.")
                    v2 = v2_items[0]
                    d1 = pd.to_numeric(self.df[v1], errors='coerce').dropna()
                    d2 = pd.to_numeric(self.df[v2], errors='coerce').dropna()
                    stat, p = stats.mannwhitneyu(d1, d2, alternative=alt)
                    h0_txt = f"H0: 분포({v1}) = 분포({v2}) vs H1: 분포({v1}) {alt_sym} 분포({v2}) ({alt_kr})"
                    self.last_test_result = {
                        "dist": "custom", "stat": stat, "p": p, "alpha": alpha, "alt": alt,
                        "title": f"Mann-Whitney U 검정 ({alt_kr}: {v1} vs {v2})",
                        "h0": h0_txt,
                        "effect": f"U-통계량 = {stat:.1f} (n1={len(d1)}, n2={len(d2)})",
                        "groups": [d1, d2], "labels": [v1, v2]
                    }
                    self.out(f"[Mann-Whitney U 검정 ({alt_kr})]\nU-통계량 = {stat:.4f}, p-value = {p:.4e}")
                else:
                    if v1 == "선택안함": raise ValueError("변수 1을 선택하세요.")
                    data = pd.to_numeric(self.df[v1], errors='coerce').dropna()
                    stat, p = stats.shapiro(data) if "Shapiro" in test else stats.kstest((data-np.mean(data))/np.std(data, ddof=1), 'norm')
                    
                    self.last_test_result = {
                        "dist": "custom", "stat": stat, "p": p, "alpha": alpha, "alt": "greater",
                        "title": f"정규성 검정: {v1}",
                        "h0": "H0: 모집단은 정규분포를 따른다 vs H1: 정규분포를 따르지 않는다",
                        "effect": f"검정통계량 = {stat:.4f}",
                        "data": data, "v1": v1
                    }
                    self.out(f"[정규성 검정 ({test})]\n통계량 = {stat:.4f}, p-value = {p:.4e}")

            # 리포트 및 기각역 시각화 갱신
            if self.last_test_result:
                self.redraw_sampling_distribution(alpha)

        except Exception as e:
            self.out(f"\n[오류 발생]: {str(e)}")

    def interpret_cohen_d(self, d):
        ad = abs(d)
        if ad < 0.2: return "효과 없음 (Negligible)"
        elif ad < 0.5: return "작은 효과 (Small)"
        elif ad < 0.8: return "중간 크기 효과 (Medium)"
        else: return "큰 효과 (Large)"

    def interpret_eta_sq(self, eta):
        if eta < 0.01: return "효과 없음"
        elif eta < 0.06: return "작은 효과 (Small)"
        elif eta < 0.14: return "중간 효과 (Medium)"
        else: return "큰 효과 (Large)"

    def redraw_sampling_distribution(self, alpha):
        res = self.last_test_result
        if not res: return
        
        stat = res["stat"]
        p_val = res["p"]
        h0_txt = res["h0"]
        effect_txt = res["effect"]
        alt = res.get("alt", "two-sided")
        
        # 3단계 결론 카드 갱신
        self.lbl_hypo.setText(f"가설 설정: {h0_txt}")
        
        alt_tag = "우측단측" if alt == "greater" else ("좌측단측" if alt == "less" else "양측")
        is_reject = p_val < alpha
        if is_reject:
            if alt == "greater":
                meaning = "모수가 기준값(대조군)보다 통계적으로 유의미하게 큼!"
            elif alt == "less":
                meaning = "모수가 기준값(대조군)보다 통계적으로 유의미하게 작음!"
            else:
                meaning = "통계적으로 유의미한 효과/차이 확인!"
            self.lbl_decision.setText(f"🔴 통계적 판정: H0 기각 (p-value = {p_val:.4e} < α = {alpha:.3f}) → [{alt_tag}] {meaning}")
            self.lbl_decision.setStyleSheet("color: #dc3545; font-weight: bold; font-size: 10.5pt;")
        else:
            if alt == "greater":
                meaning = "더 크다는 통계적으로 유의미한 증거 부족."
            elif alt == "less":
                meaning = "더 작다는 통계적으로 유의미한 증거 부족."
            else:
                meaning = "통계적으로 유의미한 차이 없음."
            self.lbl_decision.setText(f"🔵 통계적 판정: H0 채택 (p-value = {p_val:.4e} ≥ α = {alpha:.3f}) → [{alt_tag}] {meaning}")
            self.lbl_decision.setStyleSheet("color: #0d6efd; font-weight: bold; font-size: 10.5pt;")
            
        self.lbl_effect.setText(f"실무적 효과 크기: {effect_txt}")
        
        # 차트 그리기
        self.figure.clear()
        
        if res.get("dist") in ["t", "f", "chi2", "z"]:
            # 2분할 뷰: 좌측(표본분포 및 기각역), 우측(데이터 Boxplot/Scatter)
            ax1 = self.figure.add_subplot(121)
            ax2 = self.figure.add_subplot(122)
            
            d_kind = res["dist"]
            if d_kind == "t":
                df = res["df"]
                limit = max(4.5, abs(stat) + 1.2)
                x = np.linspace(-limit, limit, 600)
                y = stats.t.pdf(x, df=df)
                df_label = f"{df:.1f}" if isinstance(df, float) else f"{df}"
                ax1.plot(x, y, color='#0d6efd', lw=2, label=f't-분포 (df={df_label})')
                ax1.fill_between(x, y, alpha=0.1, color='#0d6efd')
                
                if alt == "two-sided":
                    crit = stats.t.ppf(1 - alpha/2, df=df)
                    ax1.fill_between(x[x >= crit], y[x >= crit], color='#dc3545', alpha=0.45, label=f'기각역 (양측 α={alpha:.3f})')
                    ax1.fill_between(x[x <= -crit], y[x <= -crit], color='#dc3545', alpha=0.45)
                    ax1.axvline(crit, color='#dc3545', linestyle='--', label=f'임계값: ±{crit:.2f}')
                    ax1.axvline(-crit, color='#dc3545', linestyle='--')
                elif alt == "greater":
                    crit = stats.t.ppf(1 - alpha, df=df)
                    ax1.fill_between(x[x >= crit], y[x >= crit], color='#dc3545', alpha=0.45, label=f'우측 기각역 (α={alpha:.3f})')
                    ax1.axvline(crit, color='#dc3545', linestyle='--', label=f'임계값: +{crit:.2f}')
                else: # less
                    crit = stats.t.ppf(alpha, df=df)
                    ax1.fill_between(x[x <= crit], y[x <= crit], color='#dc3545', alpha=0.45, label=f'좌측 기각역 (α={alpha:.3f})')
                    ax1.axvline(crit, color='#dc3545', linestyle='--', label=f'임계값: {crit:.2f}')
                
                ax1.axvline(stat, color='black', lw=2.5, label=f'관측 t = {stat:.2f}')
                ax1.plot(stat, stats.t.pdf(stat, df=df) if abs(stat) < limit else 0, 'ko', markersize=7)
                
            elif d_kind == "f":
                df1, df2 = res["df1"], res["df2"]
                if alt == "two-sided":
                    crit_l = stats.f.ppf(alpha/2, df1, df2)
                    crit_r = stats.f.ppf(1 - alpha/2, df1, df2)
                    max_x = max(crit_r * 1.5, stat * 1.3, 5.0)
                    x = np.linspace(0.001, max_x, 600)
                    y = stats.f.pdf(x, df1, df2)
                    ax1.plot(x, y, color='#0d6efd', lw=2, label=f'F-분포 (df={df1},{df2})')
                    ax1.fill_between(x, y, alpha=0.1, color='#0d6efd')
                    ax1.fill_between(x[x <= crit_l], y[x <= crit_l], color='#dc3545', alpha=0.45, label=f'기각역 (양측 α={alpha:.3f})')
                    ax1.fill_between(x[x >= crit_r], y[x >= crit_r], color='#dc3545', alpha=0.45)
                    ax1.axvline(crit_l, color='#dc3545', linestyle='--', label=f'임계값: {crit_l:.2f}, {crit_r:.2f}')
                    ax1.axvline(crit_r, color='#dc3545', linestyle='--')
                elif alt == "greater":
                    crit = stats.f.ppf(1 - alpha, df1, df2)
                    max_x = max(crit * 1.8, stat * 1.3, 5.0)
                    x = np.linspace(0.001, max_x, 600)
                    y = stats.f.pdf(x, df1, df2)
                    ax1.plot(x, y, color='#0d6efd', lw=2, label=f'F-분포 (df={df1},{df2})')
                    ax1.fill_between(x, y, alpha=0.1, color='#0d6efd')
                    ax1.fill_between(x[x >= crit], y[x >= crit], color='#dc3545', alpha=0.45, label=f'우측 기각역 (α={alpha:.3f})')
                    ax1.axvline(crit, color='#dc3545', linestyle='--', label=f'임계값: {crit:.2f}')
                else: # less
                    crit = stats.f.ppf(alpha, df1, df2)
                    max_x = max(5.0, stat * 1.5)
                    x = np.linspace(0.001, max_x, 600)
                    y = stats.f.pdf(x, df1, df2)
                    ax1.plot(x, y, color='#0d6efd', lw=2, label=f'F-분포 (df={df1},{df2})')
                    ax1.fill_between(x, y, alpha=0.1, color='#0d6efd')
                    ax1.fill_between(x[x <= crit], y[x <= crit], color='#dc3545', alpha=0.45, label=f'좌측 기각역 (α={alpha:.3f})')
                    ax1.axvline(crit, color='#dc3545', linestyle='--', label=f'임계값: {crit:.2f}')
                
                ax1.axvline(stat, color='black', lw=2.5, label=f'관측 F = {stat:.2f}')
                ax1.plot(stat, stats.f.pdf(stat, df1, df2) if stat < max_x else 0, 'ko', markersize=7)

            elif d_kind == "chi2":
                df = res["df"]
                if alt == "two-sided":
                    crit_l = stats.chi2.ppf(alpha/2, df)
                    crit_r = stats.chi2.ppf(1 - alpha/2, df)
                    max_x = max(crit_r * 1.4, stat * 1.2, df + 4 * np.sqrt(2 * df))
                    x = np.linspace(0.001, max_x, 600)
                    y = stats.chi2.pdf(x, df)
                    ax1.plot(x, y, color='#0d6efd', lw=2, label=f'χ²-분포 (df={df})')
                    ax1.fill_between(x, y, alpha=0.1, color='#0d6efd')
                    ax1.fill_between(x[x <= crit_l], y[x <= crit_l], color='#dc3545', alpha=0.45, label=f'기각역 (양측 α={alpha:.3f})')
                    ax1.fill_between(x[x >= crit_r], y[x >= crit_r], color='#dc3545', alpha=0.45)
                    ax1.axvline(crit_l, color='#dc3545', linestyle='--')
                    ax1.axvline(crit_r, color='#dc3545', linestyle='--', label=f'임계값: {crit_l:.1f}, {crit_r:.1f}')
                elif alt == "greater":
                    crit = stats.chi2.ppf(1 - alpha, df)
                    max_x = max(crit * 1.4, stat * 1.2, df + 4 * np.sqrt(2 * df))
                    x = np.linspace(0.001, max_x, 600)
                    y = stats.chi2.pdf(x, df)
                    ax1.plot(x, y, color='#0d6efd', lw=2, label=f'χ²-분포 (df={df})')
                    ax1.fill_between(x, y, alpha=0.1, color='#0d6efd')
                    ax1.fill_between(x[x >= crit], y[x >= crit], color='#dc3545', alpha=0.45, label=f'우측 기각역 (α={alpha:.3f})')
                    ax1.axvline(crit, color='#dc3545', linestyle='--', label=f'임계값: {crit:.1f}')
                else: # less
                    crit = stats.chi2.ppf(alpha, df)
                    max_x = max(df + 3 * np.sqrt(2 * df), stat * 1.3, 5.0)
                    x = np.linspace(0.001, max_x, 600)
                    y = stats.chi2.pdf(x, df)
                    ax1.plot(x, y, color='#0d6efd', lw=2, label=f'χ²-분포 (df={df})')
                    ax1.fill_between(x, y, alpha=0.1, color='#0d6efd')
                    ax1.fill_between(x[x <= crit], y[x <= crit], color='#dc3545', alpha=0.45, label=f'좌측 기각역 (α={alpha:.3f})')
                    ax1.axvline(crit, color='#dc3545', linestyle='--', label=f'임계값: {crit:.1f}')
                
                ax1.axvline(stat, color='black', lw=2.5, label=f'관측 χ² = {stat:.2f}')
                ax1.plot(stat, stats.chi2.pdf(stat, df) if stat < max_x else 0, 'ko', markersize=7)

            elif d_kind == "z":
                limit = max(4.5, abs(stat) + 1.2)
                x = np.linspace(-limit, limit, 600)
                y = stats.norm.pdf(x)
                ax1.plot(x, y, color='#0d6efd', lw=2, label='표준정규분포 Z')
                ax1.fill_between(x, y, alpha=0.1, color='#0d6efd')
                
                if alt == "two-sided":
                    crit = stats.norm.ppf(1 - alpha/2)
                    ax1.fill_between(x[x >= crit], y[x >= crit], color='#dc3545', alpha=0.45, label=f'기각역 (양측 α={alpha:.3f})')
                    ax1.fill_between(x[x <= -crit], y[x <= -crit], color='#dc3545', alpha=0.45)
                    ax1.axvline(crit, color='#dc3545', linestyle='--', label=f'임계값: ±{crit:.2f}')
                    ax1.axvline(-crit, color='#dc3545', linestyle='--')
                elif alt == "greater":
                    crit = stats.norm.ppf(1 - alpha)
                    ax1.fill_between(x[x >= crit], y[x >= crit], color='#dc3545', alpha=0.45, label=f'우측 기각역 (α={alpha:.3f})')
                    ax1.axvline(crit, color='#dc3545', linestyle='--', label=f'임계값: +{crit:.2f}')
                else: # less
                    crit = stats.norm.ppf(alpha)
                    ax1.fill_between(x[x <= crit], y[x <= crit], color='#dc3545', alpha=0.45, label=f'좌측 기각역 (α={alpha:.3f})')
                    ax1.axvline(crit, color='#dc3545', linestyle='--', label=f'임계값: {crit:.2f}')
                
                ax1.axvline(stat, color='black', lw=2.5, label=f'관측 Z = {stat:.2f}')
                ax1.plot(stat, stats.norm.pdf(stat) if abs(stat) < limit else 0, 'ko', markersize=7)

            ax1.set_title(res["title"], fontsize=10.5, fontweight='bold')
            ax1.set_ylabel("확률밀도 (Sampling Density)")
            ax1.set_xlabel("검정 통계량 스케일")
            ax1.grid(True, alpha=0.3)
            ax1.legend(fontsize=8, loc='upper right')

            # 2) 우측 실제 데이터 시각화
            if "groups" in res:
                ax2.boxplot(res["groups"], labels=res["labels"], patch_artist=True,
                            boxprops=dict(facecolor='#E8F0FE', color='#2C3E50'),
                            medianprops=dict(color='#dc3545', lw=2), showmeans=True)
                ax2.set_title("집단별 데이터 분포 (Boxplot)", fontsize=10.5)
                ax2.set_ylabel("측정값")
            elif "scatter" in res:
                x_v, y_v, xl, yl = res["scatter"]
                ax2.scatter(x_v, y_v, color='#0d6efd', alpha=0.6, edgecolors='k')
                m, b = np.polyfit(x_v, y_v, 1)
                ax2.plot(x_v, m*x_v+b, 'r--', lw=2, label='추세선 (Trend)')
                ax2.set_xlabel(xl)
                ax2.set_ylabel(yl)
                ax2.set_title("산점도 및 선형 회귀 추세", fontsize=10.5)
                ax2.legend(fontsize=8)
            elif "regression" in res:
                xv, yv, pred_v, xl, yl = res["regression"]
                ax2.scatter(xv, yv, color='#0d6efd', alpha=0.5, edgecolors='k')
                sort_i = np.argsort(xv.values)
                ax2.plot(xv.values[sort_i], pred_v.values[sort_i], 'r-', lw=2, label='회귀 적합선')
                ax2.set_xlabel(xl)
                ax2.set_ylabel(yl)
                ax2.set_title("회귀 적합 시각화", fontsize=10.5)
                ax2.legend(fontsize=8)
            elif "diff" in res:
                ax2.hist(res["diff"], bins='auto', color='#8172B3', edgecolor='black', alpha=0.7)
                ax2.axvline(0, color='red', linestyle='--', lw=2, label='차이 = 0 (H0)')
                ax2.axvline(np.mean(res["diff"]), color='green', lw=2, label=f'평균차이 = {np.mean(res["diff"]):.2f}')
                ax2.set_title("대응 차이값 분포", fontsize=10.5)
                ax2.set_xlabel("차이 (Diff)")
                ax2.legend(fontsize=8)
            elif "data" in res:
                ax2.hist(res["data"], bins='auto', color='#0d6efd', edgecolor='black', alpha=0.6)
                ax2.axvline(np.mean(res["data"]), color='red', lw=2, label=f'표본평균 = {np.mean(res["data"]):.2f}')
                ax2.set_title("데이터 히스토그램", fontsize=10.5)
                ax2.legend(fontsize=8)
            ax2.grid(True, alpha=0.3)

        else: # Normal / Custom QQ-plot or Nonparametric
            ax = self.figure.add_subplot(111)
            if "groups" in res and "labels" in res:
                ax.boxplot(res["groups"], labels=res["labels"], patch_artist=True,
                           boxprops=dict(facecolor='#E8F0FE', color='#2C3E50'),
                           medianprops=dict(color='#dc3545', lw=2), showmeans=True)
                ax.set_title(f"{res['title']} - 집단별 분포", fontsize=11)
                ax.set_ylabel("측정값")
                ax.grid(True, alpha=0.3)
            elif "data" in res:
                (osm, osr), (slope, intercept, r) = stats.probplot(res["data"], dist="norm")
                ax.plot(osm, osr, 'o', color='#0d6efd', alpha=0.7)
                ax.plot(osm, slope*osm + intercept, 'r--', lw=2, label=f'Fit Line (R² = {r**2:.3f})')
                ax.set_title(f"{res['title']} - 정규 Q-Q 플롯", fontsize=11)
                ax.set_xlabel("Theoretical Quantiles")
                ax.set_ylabel("Ordered Values")
                ax.grid(True, alpha=0.3)
                ax.legend()

        self.canvas.draw()
        self.btn_export.setEnabled(True)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'figure') and hasattr(self, 'canvas'):
            try:
                self.figure.tight_layout()
                self.canvas.draw_idle()
            except Exception:
                pass
