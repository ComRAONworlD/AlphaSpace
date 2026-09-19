import numpy as np
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QLineEdit, QPushButton, 
    QStackedWidget, QFormLayout, QGroupBox, QMessageBox, QRadioButton, QButtonGroup, 
    QFileDialog, QSlider, QCheckBox, QScrollArea, QFrame, QGridLayout, QToolTip,
    QSplitter
)
from PySide6.QtCore import Qt, QUrl
from PySide6.QtGui import QDesktopServices
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

from core_distributions import DISTRIBUTIONS, map_params, calculate_theoretical_stats
from knowledge_base import DISTRIBUTION_KNOWLEDGE, KnowledgeHubDialog

class SimulationTab(QWidget):
    def __init__(self):
        super().__init__()
        self.sample_data = None
        self.updating_params = False
        self.setup_ui()

    def setup_ui(self):
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(6, 6, 6, 6)
        
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setChildrenCollapsible(False)
        
        # 좌측 제어 패널 (스크롤 영역 적용)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setMinimumWidth(320)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setFrameShape(QFrame.NoFrame)
        
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(12)
        left_layout.setContentsMargins(5, 5, 10, 5)
        
        # 1. 타입 및 분포 선택
        type_group = QGroupBox("1. 확률분포 선택")
        type_layout = QFormLayout()
        
        self.type_combo = QComboBox()
        self.type_combo.addItem("연속형 분포 (Continuous)", "continuous")
        self.type_combo.addItem("이산형 분포 (Discrete)", "discrete")
        self.type_combo.currentIndexChanged.connect(self.on_type_changed)
        
        self.dist_combo = QComboBox()
        self.dist_combo.currentIndexChanged.connect(self.on_dist_changed)
        
        type_layout.addRow("분포 유형:", self.type_combo)
        type_layout.addRow("분포 종류:", self.dist_combo)
        
        # 지식 허브 바로가기 버튼
        kb_btn_layout = QHBoxLayout()
        self.btn_open_kb = QPushButton("📚 수식 & 지식 사전")
        self.btn_open_kb.setProperty("btnClass", "primary")
        self.btn_open_kb.setCursor(Qt.PointingHandCursor)
        self.btn_open_kb.clicked.connect(self.open_knowledge_hub)
        kb_btn_layout.addWidget(self.btn_open_kb)
        
        self.btn_web_link = QPushButton("🌐 웹 레퍼런스")
        self.btn_web_link.setProperty("btnClass", "success")
        self.btn_web_link.setCursor(Qt.PointingHandCursor)
        self.btn_web_link.clicked.connect(self.open_web_reference)
        kb_btn_layout.addWidget(self.btn_web_link)
        
        type_layout.addRow(kb_btn_layout)
        type_group.setLayout(type_layout)
        left_layout.addWidget(type_group)
        
        # 2. 동적 모수 슬라이더 및 입력 위젯 스택
        self.param_stack = QStackedWidget()
        self.param_controls = {} # {dist_key: [{'le': QLineEdit, 'slider': QSlider, 'meta': tuple}, ...]}
        
        for d_type, d_dict in DISTRIBUTIONS.items():
            for key, dist_info in d_dict.items():
                page = QWidget()
                page_layout = QVBoxLayout(page)
                page_layout.setContentsMargins(0, 0, 0, 0)
                page_layout.setSpacing(8)
                
                controls = []
                for p_meta in dist_info["params"]:
                    p_name, def_val, p_min, p_max, p_step, is_int = p_meta
                    
                    row_box = QGroupBox(f"{p_name}")
                    row_box.setStyleSheet("QGroupBox { margin-top: 5px; padding-top: 8px; font-size: 9pt; }")
                    row_layout = QVBoxLayout(row_box)
                    row_layout.setContentsMargins(6, 6, 6, 6)
                    row_layout.setSpacing(4)
                    
                    # 수치 입력과 슬라이더
                    input_layout = QHBoxLayout()
                    le = QLineEdit(str(def_val))
                    le.setFixedWidth(75)
                    
                    slider = QSlider(Qt.Horizontal)
                    steps_count = int((p_max - p_min) / p_step) if p_step > 0 else 100
                    slider.setRange(0, max(steps_count, 1))
                    
                    # 기본 슬라이더 위치 계산
                    try:
                        cur_val = float(def_val)
                        init_slider_pos = int((cur_val - p_min) / (p_max - p_min) * steps_count)
                        slider.setValue(max(0, min(steps_count, init_slider_pos)))
                    except:
                        slider.setValue(0)
                        
                    input_layout.addWidget(slider, stretch=1)
                    input_layout.addWidget(le)
                    row_layout.addLayout(input_layout)
                    
                    # 범위 표시 레이블
                    range_lbl = QLabel(f"조정 범위: [{p_min} ~ {p_max}], 간격: {p_step}")
                    range_lbl.setStyleSheet("color: #777; font-size: 8pt;")
                    row_layout.addWidget(range_lbl)
                    
                    page_layout.addWidget(row_box)
                    
                    ctrl_data = {
                        'le': le, 'slider': slider, 
                        'min': p_min, 'max': p_max, 'step': p_step, 
                        'is_int': is_int, 'name': p_name
                    }
                    controls.append(ctrl_data)
                    
                    # 상호 동기화 이벤트 연결
                    self.connect_param_events(ctrl_data)
                    
                self.param_controls[key] = controls
                self.param_stack.addWidget(page)
                dist_info["stack_index"] = self.param_stack.count() - 1
                
        param_group = QGroupBox("2. 인터랙티브 모수 조정 (Sliders)")
        param_layout = QVBoxLayout()
        param_layout.addWidget(self.param_stack)
        
        # 실시간 자동 반영 체크박스
        self.chk_live_update = QCheckBox("⚡ 슬라이더 조작 시 실시간 차트 반영 (Live Preview)")
        self.chk_live_update.setChecked(True)
        self.chk_live_update.setStyleSheet("font-weight: bold; color: #0d6efd; margin-top: 4px;")
        param_layout.addWidget(self.chk_live_update)
        
        param_group.setLayout(param_layout)
        left_layout.addWidget(param_group)
        
        # 3. 실시간 이론적 기초통계량 카드
        stats_group = QGroupBox("3. 실시간 이론적 통계량 (Moments)")
        stats_layout = QGridLayout()
        stats_layout.setSpacing(6)
        
        self.lbl_stat_mean = QLabel("-")
        self.lbl_stat_var = QLabel("-")
        self.lbl_stat_std = QLabel("-")
        self.lbl_stat_median = QLabel("-")
        self.lbl_stat_skew = QLabel("-")
        self.lbl_stat_kurt = QLabel("-")
        
        for lbl in [self.lbl_stat_mean, self.lbl_stat_var, self.lbl_stat_std, 
                    self.lbl_stat_median, self.lbl_stat_skew, self.lbl_stat_kurt]:
            lbl.setStyleSheet("font-weight: bold; color: #198754;")
            
        stats_layout.addWidget(QLabel("기댓값 E[X] (평균):"), 0, 0)
        stats_layout.addWidget(self.lbl_stat_mean, 0, 1)
        stats_layout.addWidget(QLabel("분산 Var(X):"), 0, 2)
        stats_layout.addWidget(self.lbl_stat_var, 0, 3)
        
        stats_layout.addWidget(QLabel("표준편차 (σ):"), 1, 0)
        stats_layout.addWidget(self.lbl_stat_std, 1, 1)
        stats_layout.addWidget(QLabel("중앙값 (Median):"), 1, 2)
        stats_layout.addWidget(self.lbl_stat_median, 1, 3)
        
        stats_layout.addWidget(QLabel("왜도 (Skewness):"), 2, 0)
        stats_layout.addWidget(self.lbl_stat_skew, 2, 1)
        stats_layout.addWidget(QLabel("첨도 (Kurtosis):"), 2, 2)
        stats_layout.addWidget(self.lbl_stat_kurt, 2, 3)
        
        stats_group.setLayout(stats_layout)
        left_layout.addWidget(stats_group)
        
        # 4. 표본 시뮬레이션 (Monte Carlo Sampling)
        sample_group = QGroupBox("4. 표본 추출 시뮬레이션 (Monte Carlo)")
        sample_layout = QVBoxLayout()
        
        self.chk_sample_overlay = QCheckBox("무작위 표본 추출 및 히스토그램 오버레이")
        self.chk_sample_overlay.toggled.connect(self.on_sample_toggle)
        sample_layout.addWidget(self.chk_sample_overlay)
        
        sample_ctrl_layout = QHBoxLayout()
        sample_ctrl_layout.addWidget(QLabel("표본 수 N:"))
        self.sample_size_combo = QComboBox()
        self.sample_size_combo.addItems(["100", "500", "1,000", "5,000", "10,000"])
        self.sample_size_combo.setCurrentIndex(2) # 1000
        self.sample_size_combo.currentIndexChanged.connect(self.generate_new_samples)
        sample_ctrl_layout.addWidget(self.sample_size_combo)
        
        self.btn_resample = QPushButton("🎲 새로 추출")
        self.btn_resample.setCursor(Qt.PointingHandCursor)
        self.btn_resample.clicked.connect(self.generate_new_samples)
        sample_ctrl_layout.addWidget(self.btn_resample)
        sample_layout.addLayout(sample_ctrl_layout)
        
        sample_group.setLayout(sample_layout)
        left_layout.addWidget(sample_group)

        # 5. 값 표기 및 확률 계산
        mark_group = QGroupBox("5. 확률 및 분위수 계산기")
        mark_layout = QFormLayout()
        self.mark_x = QLineEdit()
        self.mark_x.setPlaceholderText("X 값 (예: 1.96)")
        self.mark_prob = QLineEdit()
        self.mark_prob.setPlaceholderText("누적 확률 (0~1, 예: 0.95)")
        mark_layout.addRow("X 값 (x):", self.mark_x)
        mark_layout.addRow("확률 (p):", self.mark_prob)
        
        # 계산 기준
        dir_layout = QHBoxLayout()
        self.radio_less = QRadioButton("이하 (X ≤ x)")
        self.radio_less.setChecked(True)
        self.radio_greater = QRadioButton("이상 (X ≥ x)")
        self.radio_equal = QRadioButton("같다 (X = x)")
        
        self.dir_btn_group = QButtonGroup()
        self.dir_btn_group.addButton(self.radio_less, id=0)
        self.dir_btn_group.addButton(self.radio_greater, id=1)
        self.dir_btn_group.addButton(self.radio_equal, id=2)
        
        dir_layout.addWidget(self.radio_less)
        dir_layout.addWidget(self.radio_greater)
        dir_layout.addWidget(self.radio_equal)
        mark_layout.addRow("계산 기준:", dir_layout)
        
        self.dir_btn_group.buttonToggled.connect(lambda: self.plot_chart() if self.chk_live_update.isChecked() else None)
        
        mark_group.setLayout(mark_layout)
        left_layout.addWidget(mark_group)

        self.mark_x.textChanged.connect(self.on_mark_x_changed)
        self.mark_prob.textChanged.connect(self.on_mark_prob_changed)
        
        # 6. 시각화 모드 선택 & 액션 버튼
        view_group = QGroupBox("6. 시각화 모드 및 내보내기")
        view_layout = QVBoxLayout()
        
        view_mode_layout = QHBoxLayout()
        view_mode_layout.addWidget(QLabel("차트 뷰:"))
        self.view_combo = QComboBox()
        self.view_combo.addItems(["PDF/PMF (확률밀도/질량)", "CDF (누적확률분포)", "듀얼 뷰 (PDF/PMF + CDF)"])
        self.view_combo.currentIndexChanged.connect(lambda: self.plot_chart())
        view_mode_layout.addWidget(self.view_combo)
        view_layout.addLayout(view_mode_layout)
        
        # 그리기 & 저장 버튼
        btn_action_layout = QHBoxLayout()
        self.plot_btn = QPushButton("차트 새로고침")
        self.plot_btn.setProperty("btnClass", "primary")
        self.plot_btn.setCursor(Qt.PointingHandCursor)
        self.plot_btn.setMinimumHeight(38)
        self.plot_btn.clicked.connect(self.plot_chart)
        btn_action_layout.addWidget(self.plot_btn)

        self.export_btn = QPushButton("차트 이미지 저장")
        self.export_btn.setProperty("btnClass", "secondary")
        self.export_btn.setCursor(Qt.PointingHandCursor)
        self.export_btn.setMinimumHeight(38)
        self.export_btn.clicked.connect(self.export_chart)
        btn_action_layout.addWidget(self.export_btn)
        
        view_layout.addLayout(btn_action_layout)
        view_group.setLayout(view_layout)
        left_layout.addWidget(view_group)
        
        left_layout.addStretch()
        scroll_area.setWidget(left_panel)
        
        # 우측 패널 (차트 영역 + 하단 수식/지식 카드)
        right_panel = QWidget()
        right_panel.setMinimumWidth(350)
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        right_layout.addWidget(self.canvas, stretch=1)
        
        # 하단 요약 정보 카드
        self.info_card = QGroupBox("📌 현재 분포 수식 및 모수 특성 요약")
        self.info_card.setMinimumHeight(100)
        info_layout = QVBoxLayout(self.info_card)
        self.lbl_formula = QLabel()
        self.lbl_formula.setWordWrap(True)
        self.lbl_formula.setStyleSheet("font-family: Consolas, monospace; font-size: 9.5pt; color: #0d6efd;")
        self.lbl_desc = QLabel()
        self.lbl_desc.setWordWrap(True)
        self.lbl_desc.setStyleSheet("color: #555; font-size: 9pt;")
        info_layout.addWidget(self.lbl_formula)
        info_layout.addWidget(self.lbl_desc)
        right_layout.addWidget(self.info_card)
        
        self.splitter.addWidget(scroll_area)
        self.splitter.addWidget(right_panel)
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)
        self.splitter.setSizes([480, 800])
        self.splitter.setStretchFactor(0, 0)
        self.splitter.setStretchFactor(1, 1)
        main_layout.addWidget(self.splitter)
        
        # 초기화
        self.on_type_changed()
        self.plot_chart()

    def connect_param_events(self, ctrl):
        slider = ctrl['slider']
        le = ctrl['le']
        p_min = ctrl['min']
        p_max = ctrl['max']
        is_int = ctrl['is_int']
        
        def on_slider_moved(val):
            if self.updating_params: return
            self.updating_params = True
            ratio = val / max(slider.maximum(), 1)
            real_val = p_min + ratio * (p_max - p_min)
            if is_int:
                le.setText(str(int(round(real_val))))
            else:
                le.setText(f"{real_val:.2f}")
            self.updating_params = False
            if self.chk_live_update.isChecked():
                self.plot_chart()
                
        def on_text_edited(text):
            if self.updating_params: return
            try:
                val = float(text.strip())
                val_clipped = max(p_min, min(p_max, val))
                ratio = (val_clipped - p_min) / (p_max - p_min) if p_max > p_min else 0
                self.updating_params = True
                slider.setValue(int(ratio * slider.maximum()))
                self.updating_params = False
                if self.chk_live_update.isChecked():
                    self.plot_chart()
            except ValueError:
                pass

        slider.valueChanged.connect(on_slider_moved)
        le.textChanged.connect(on_text_edited)

    def on_mark_x_changed(self, text):
        if text.strip() and self.mark_prob.text():
            self.mark_prob.blockSignals(True)
            self.mark_prob.clear()
            self.mark_prob.blockSignals(False)
        if self.chk_live_update.isChecked():
            self.plot_chart()

    def on_mark_prob_changed(self, text):
        if text.strip() and self.mark_x.text():
            self.mark_x.blockSignals(True)
            self.mark_x.clear()
            self.mark_x.blockSignals(False)
        if self.chk_live_update.isChecked():
            self.plot_chart()

    def on_sample_toggle(self, checked):
        if checked and self.sample_data is None:
            self.generate_new_samples()
        else:
            self.plot_chart()

    def generate_new_samples(self):
        d_type = self.type_combo.currentData()
        dist_key = self.dist_combo.currentData()
        if not dist_key: return
        
        dist_info = DISTRIBUTIONS[d_type][dist_key]
        try:
            raw_params = []
            for ctrl in self.param_controls[dist_key]:
                val_str = ctrl['le'].text().strip()
                raw_params.append(float(val_str))
            
            args, kwargs = map_params(d_type, dist_key, raw_params)
            dist = dist_info["func"](*args, **kwargs)
            
            n_str = self.sample_size_combo.currentText().replace(',', '')
            n_samples = int(n_str)
            self.sample_data = dist.rvs(size=n_samples)
            self.plot_chart()
        except Exception as e:
            self.sample_data = None

    def open_knowledge_hub(self):
        dist_key = self.dist_combo.currentData()
        dlg = KnowledgeHubDialog(self, initial_dist_key=dist_key)
        dlg.exec()

    def open_web_reference(self):
        dist_key = self.dist_combo.currentData()
        info = DISTRIBUTION_KNOWLEDGE.get(dist_key)
        if info and "links" in info and len(info["links"]) > 0:
            url = info["links"][0]["url"]
            QDesktopServices.openUrl(QUrl(url))
        else:
            QMessageBox.information(self, "안내", "해당 분포의 웹 링크 정보가 없습니다.")

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

    def on_type_changed(self):
        d_type = self.type_combo.currentData()
        
        self.dist_combo.blockSignals(True)
        self.dist_combo.clear()
        for key, dist_info in DISTRIBUTIONS[d_type].items():
            self.dist_combo.addItem(dist_info["name"], key)
        self.dist_combo.blockSignals(False)
        
        if d_type == "discrete":
            self.radio_equal.setVisible(True)
        else:
            self.radio_equal.setVisible(False)
            if self.radio_equal.isChecked():
                self.radio_less.setChecked(True)
                
        self.on_dist_changed()
        
    def on_dist_changed(self):
        d_type = self.type_combo.currentData()
        dist_key = self.dist_combo.currentData()
        if not dist_key: return
        
        dist_info = DISTRIBUTIONS[d_type][dist_key]
        self.param_stack.setCurrentIndex(dist_info["stack_index"])
        
        # 하단 요약 정보 카드 갱신
        k_info = DISTRIBUTION_KNOWLEDGE.get(dist_key, {})
        formula_txt = k_info.get("formula_pdf", "-")
        self.lbl_formula.setText(f"수식: {formula_txt}")
        
        exp_txt = k_info.get("explanation", "").replace("<br>", " ").replace("<b>", "").replace("</b>", "")
        self.lbl_desc.setText(exp_txt[:180] + ("..." if len(exp_txt) > 180 else ""))
        
        self.sample_data = None
        self.plot_chart()
        
    def plot_chart(self):
        d_type = self.type_combo.currentData()
        dist_key = self.dist_combo.currentData()
        if not dist_key: return
        
        dist_info = DISTRIBUTIONS[d_type][dist_key]
        self.figure.clear()
        
        view_mode = self.view_combo.currentIndex() # 0: PDF/PMF, 1: CDF, 2: Dual
        
        if view_mode == 2:
            ax1 = self.figure.add_subplot(211)
            ax2 = self.figure.add_subplot(212, sharex=ax1)
            axes = [ax1, ax2]
        elif view_mode == 1:
            ax1 = self.figure.add_subplot(111)
            axes = [ax1]
        else:
            ax1 = self.figure.add_subplot(111)
            axes = [ax1]
            
        x_mark = None
        prob_mark = None
        
        try:
            if self.mark_x.text().strip():
                x_mark = float(self.mark_x.text())
            if self.mark_prob.text().strip():
                prob_mark = float(self.mark_prob.text())
                if not (0 <= prob_mark <= 1):
                    raise ValueError("확률은 0.0과 1.0 사이여야 합니다.")
        except ValueError:
            return

        calc_dir = "less"
        if self.radio_greater.isChecked():
            calc_dir = "greater"
        elif self.radio_equal.isChecked() and d_type == "discrete":
            calc_dir = "equal"

        try:
            raw_params = []
            for ctrl in self.param_controls[dist_key]:
                val_str = ctrl['le'].text().strip()
                raw_params.append(float(val_str))
            
            args, kwargs = map_params(d_type, dist_key, raw_params)
            dist = dist_info["func"](*args, **kwargs)
            
            # 실시간 이론 통계량 카드 갱신
            stats_vals = calculate_theoretical_stats(dist, dist_key)
            self.lbl_stat_mean.setText(stats_vals["mean"])
            self.lbl_stat_var.setText(stats_vals["var"])
            self.lbl_stat_std.setText(stats_vals["std"])
            self.lbl_stat_median.setText(stats_vals["median"])
            self.lbl_stat_skew.setText(stats_vals["skew"])
            self.lbl_stat_kurt.setText(stats_vals["kurt"])
            
            # 정의역 탐색
            if dist_key == "cauchy":
                loc, scale = raw_params[0], raw_params[1]
                min_x, max_x = loc - 6*scale, loc + 6*scale
            else:
                try:
                    min_x, max_x = dist.ppf(0.001), dist.ppf(0.999)
                    if np.isinf(min_x) or np.isnan(min_x): min_x = dist.ppf(0.01)
                    if np.isinf(max_x) or np.isnan(max_x): max_x = dist.ppf(0.99)
                except:
                    min_x, max_x = -10, 10
            
            support_min, support_max = dist.support()
            min_x = max(min_x, support_min)
            max_x = min(max_x, support_max)
            margin = (max_x - min_x) * 0.05 if max_x > min_x else 1.0
            plot_min = max(support_min, min_x - margin)
            plot_max = min(support_max, max_x + margin)

            if prob_mark is not None and calc_dir != "equal":
                if calc_dir == "less":
                    x_mark = dist.ppf(prob_mark)
                elif calc_dir == "greater":
                    x_mark = dist.isf(prob_mark)

            param_str = ", ".join([f"{p[0].split(' (')[0]}={v:.2g}" for p, v in zip(dist_info["params"], raw_params)])

            # PDF / PMF 플롯
            if view_mode in [0, 2]:
                target_ax = ax1
                if d_type == "continuous":
                    x = np.linspace(plot_min, plot_max, 500)
                    y = dist.pdf(x)
                    
                    target_ax.plot(x, y, color='#0d6efd', linewidth=2.5, label=f'이론 PDF: {dist_key.upper()}({param_str})')
                    target_ax.fill_between(x, y, color='#0d6efd', alpha=0.12)
                    
                    # 몬테카를로 표본 오버레이
                    if self.chk_sample_overlay.isChecked() and self.sample_data is not None:
                        target_ax.hist(self.sample_data, bins='auto', density=True, alpha=0.35, color='#ffc107', edgecolor='black', label=f'표본 히스토그램 (N={len(self.sample_data)})')
                    
                    if x_mark is not None:
                        x_mark_clip = max(support_min, min(support_max, x_mark))
                        y_mark = dist.pdf(x_mark_clip)
                        
                        target_ax.axvline(x_mark_clip, color='#dc3545', linestyle='--', linewidth=2, label=f'x = {x_mark_clip:.2f}')
                        target_ax.plot(x_mark_clip, y_mark, 'ro', markersize=6)
                        
                        if calc_dir == "less":
                            calc_prob = dist.cdf(x_mark)
                            shade_x, shade_y = x[x <= x_mark], y[x <= x_mark]
                            text_str = f' P(X ≤ {x_mark:.2f}) = {calc_prob:.4f}'
                        else:
                            calc_prob = dist.sf(x_mark)
                            shade_x, shade_y = x[x >= x_mark], y[x >= x_mark]
                            text_str = f' P(X ≥ {x_mark:.2f}) = {calc_prob:.4f}'

                        target_ax.fill_between(shade_x, shade_y, color='#dc3545', alpha=0.35)
                        target_ax.text(x_mark_clip, y_mark, text_str, verticalalignment='bottom', fontweight='bold', color='#dc3545', fontsize=10)

                else: # 이산형
                    x_int_min = int(np.floor(plot_min))
                    x_int_max = int(np.ceil(plot_max))
                    x = np.arange(x_int_min, x_int_max + 1)
                    y = dist.pmf(x)
                    
                    target_ax.vlines(x, 0, y, colors='#0d6efd', lw=4, alpha=0.7, label=f'이론 PMF: {dist_key.upper()}({param_str})')
                    target_ax.plot(x, y, 'o', color='#0d6efd', markersize=6)
                    
                    if self.chk_sample_overlay.isChecked() and self.sample_data is not None:
                        unique_s, counts_s = np.unique(self.sample_data, return_counts=True)
                        probs_s = counts_s / np.sum(counts_s)
                        target_ax.bar(unique_s, probs_s, alpha=0.3, color='#ffc107', edgecolor='black', width=0.4, label=f'표본 상대도수 (N={len(self.sample_data)})')
                    
                    if x_mark is not None:
                        x_mark_int = int(round(x_mark))
                        y_mark = dist.pmf(x_mark_int)
                        
                        target_ax.plot(x_mark_int, y_mark, 'ro', markersize=8, zorder=5)
                        target_ax.vlines(x_mark_int, 0, y_mark, colors='#dc3545', lw=5, label=f'x = {x_mark_int}', zorder=4)
                        
                        if calc_dir == "less":
                            calc_prob = dist.cdf(x_mark_int)
                            mask = x <= x_mark_int
                            text_str = f' P(X ≤ {x_mark_int}) = {calc_prob:.4f}'
                            target_ax.vlines(x[mask], 0, y[mask], colors='#dc3545', lw=5, alpha=0.6)
                        elif calc_dir == "greater":
                            calc_prob = dist.sf(x_mark_int - 1)
                            mask = x >= x_mark_int
                            text_str = f' P(X ≥ {x_mark_int}) = {calc_prob:.4f}'
                            target_ax.vlines(x[mask], 0, y[mask], colors='#dc3545', lw=5, alpha=0.6)
                        elif calc_dir == "equal":
                            calc_prob = dist.pmf(x_mark_int)
                            text_str = f' P(X = {x_mark_int}) = {calc_prob:.4f}'

                        target_ax.text(x_mark_int, y_mark, text_str, verticalalignment='bottom', fontweight='bold', color='#dc3545', fontsize=10)

                target_ax.set_title(f"{dist_info['name']} - 확률 밀도/질량 (PDF/PMF)")
                target_ax.set_ylabel("확률밀도 (PDF)" if d_type == "continuous" else "확률질량 (PMF)")
                target_ax.grid(True, alpha=0.3)
                target_ax.legend(loc='upper right', fontsize=9)

            # CDF 플롯
            if view_mode in [1, 2]:
                target_ax = ax2 if view_mode == 2 else ax1
                
                if d_type == "continuous":
                    x = np.linspace(plot_min, plot_max, 500)
                    y_cdf = dist.cdf(x)
                    target_ax.plot(x, y_cdf, color='#198754', linewidth=2.5, label='누적분포함수 (CDF)')
                    
                    if x_mark is not None:
                        calc_p = dist.cdf(x_mark)
                        target_ax.plot([x_mark, x_mark], [0, calc_p], 'r--', lw=1.5)
                        target_ax.plot([plot_min, x_mark], [calc_p, calc_p], 'r--', lw=1.5)
                        target_ax.plot(x_mark, calc_p, 'ro')
                        target_ax.text(x_mark, calc_p, f' F({x_mark:.2f})={calc_p:.4f}', color='red', fontweight='bold', va='bottom')
                else:
                    x_int_min = int(np.floor(plot_min))
                    x_int_max = int(np.ceil(plot_max))
                    x = np.arange(x_int_min, x_int_max + 1)
                    y_cdf = dist.cdf(x)
                    target_ax.step(x, y_cdf, where='post', color='#198754', linewidth=2.5, label='누적분포함수 (CDF)')
                    target_ax.plot(x, y_cdf, 'o', color='#198754', markersize=5)
                    
                    if x_mark is not None:
                        x_int = int(round(x_mark))
                        calc_p = dist.cdf(x_int)
                        target_ax.plot([x_int, x_int], [0, calc_p], 'r--', lw=1.5)
                        target_ax.plot([plot_min, x_int], [calc_p, calc_p], 'r--', lw=1.5)
                        target_ax.plot(x_int, calc_p, 'ro')
                        target_ax.text(x_int, calc_p, f' F({x_int})={calc_p:.4f}', color='red', fontweight='bold', va='bottom')

                target_ax.set_title(f"{dist_info['name']} - 누적분포함수 (CDF)")
                target_ax.set_ylabel("누적 확률 P(X ≤ x)")
                target_ax.set_ylim(-0.05, 1.05)
                target_ax.grid(True, alpha=0.3)
                target_ax.legend(loc='lower right', fontsize=9)

            axes[-1].set_xlabel("X (확률변수)")
            self.canvas.draw()
            self.export_btn.setEnabled(True)

        except Exception as e:
            return

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'figure') and hasattr(self, 'canvas'):
            try:
                self.figure.tight_layout()
                self.canvas.draw_idle()
            except Exception:
                pass
