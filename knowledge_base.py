"""
knowledge_base.py
통계 확률 분포 및 가설 검정에 대한 상세 수학 공식, 모수 설명, 물리적/통계적 의미,
실생활 활용 사례, 신뢰할 수 있는 외부 웹 레퍼런스(NIST, Wikipedia, SciPy) 링크 및
통계 지식 허브 다이얼로그(KnowledgeHubDialog)를 제공합니다.
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QSplitter, QListWidget, QListWidgetItem,
    QTextBrowser, QLineEdit, QLabel, QPushButton, QComboBox
)
from PySide6.QtCore import Qt

DISTRIBUTION_KNOWLEDGE = {
    # 연속형 분포
    "norm": {
        "name": "정규분포 (Normal / Gaussian)",
        "type": "continuous",
        "formula_pdf": "f(x) = (1 / (σ√(2π))) * exp(-(x - μ)² / (2σ²))",
        "formula_cdf": "F(x) = (1/2) * [1 + erf((x - μ) / (σ√2))]",
        "mean_expr": "E[X] = μ",
        "var_expr": "Var(X) = σ²",
        "skewness": "0 (완전 좌우 대칭)",
        "kurtosis": "0 (정규 첨도 기준 / Excess Kurtosis = 0)",
        "params": [
            {
                "symbol": "μ (평균, 위치 모수)",
                "range": "-∞ < μ < ∞",
                "default": 0.0, "min": -20.0, "max": 20.0, "step": 0.5,
                "desc": "분포의 중심 위치(대칭축)를 결정합니다. μ가 커지면 곡선 전체가 오른쪽으로 평행 이동합니다."
            },
            {
                "symbol": "σ (표준편차, 척도 모수)",
                "range": "σ > 0",
                "default": 1.0, "min": 0.1, "max": 10.0, "step": 0.1,
                "desc": "분포의 퍼짐 정도(산포도)를 결정합니다. σ가 커지면 곡선이 완만하고 넓어지며, 작아지면 평균 근처로 뾰족하게 집중됩니다."
            }
        ],
        "explanation": """
<b>정규분포</b>는 자연계 및 사회과학에서 가장 널리 관측되는 대칭 종 모양(Bell curve)의 확률분포입니다.<br>
<b>중심극한정리(Central Limit Theorem)</b>에 의해 독립적인 확률변수들의 합이나 평균은 표본 수가 커질수록 원래 분포와 무관하게 정규분포에 수렴합니다.
""",
        "applications": [
            "성인 신장, 체중, 혈압 등 인체 측정학적 지표",
            "정밀 가공 부품의 공정 치수 오차 및 측정 오차",
            "대규모 표준화 시험(수능, 토익 등)의 점수 표준화",
            "금융 자산 수익률의 기초 모델링(Black-Scholes 모형의 기반)"
        ],
        "links": [
            {"title": "NIST e-Handbook: Normal Distribution", "url": "https://www.itl.nist.gov/div898/handbook/eda/section3/eda3661.htm"},
            {"title": "Wikipedia: Normal Distribution", "url": "https://en.wikipedia.org/wiki/Normal_distribution"},
            {"title": "SciPy Docs: stats.norm", "url": "https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.norm.html"}
        ]
    },
    "lognorm": {
        "name": "로그정규분포 (Lognormal)",
        "type": "continuous",
        "formula_pdf": "f(x) = (1 / (x σ √(2π))) * exp(-(ln(x) - μ)² / (2σ²)), x > 0",
        "formula_cdf": "F(x) = (1/2) * erfc(-(ln(x) - μ) / (σ√2))",
        "mean_expr": "E[X] = exp(μ + σ²/2)",
        "var_expr": "Var(X) = (exp(σ²) - 1) * exp(2μ + σ²)",
        "skewness": "(exp(σ²) + 2) * √(exp(σ²) - 1) > 0 (우측 긴 꼬리)",
        "kurtosis": "exp(4σ²) + 2*exp(3σ²) + 3*exp(2σ²) - 6",
        "params": [
            {
                "symbol": "μ (로그평균 / scale의 로그)",
                "range": "-∞ < μ < ∞",
                "default": 0.0, "min": -5.0, "max": 5.0, "step": 0.2,
                "desc": "변수에 자연로그를 취했을 때의 평균값입니다. 중앙값(Median) = exp(μ)을 결정합니다."
            },
            {
                "symbol": "σ (로그표준편차, 형태 모수)",
                "range": "σ > 0",
                "default": 0.8, "min": 0.05, "max": 3.0, "step": 0.05,
                "desc": "로그를 취했을 때의 표준편차이며, 클수록 우측 꼬리가 매우 길어지고 심하게 치우쳐집니다."
            }
        ],
        "explanation": """
<b>로그정규분포</b>는 확률변수 X에 자연로그를 취한 ln(X)가 정규분포를 따를 때 X가 따르는 분포입니다.<br>
많은 소규모 독립 효과들이 <b>곱셈적(Multiplicative)</b>으로 누적될 때 자연스럽게 형성되며, 항상 양수(X > 0) 값을 가집니다.
""",
        "applications": [
            "국민 소득, 자산 분배, 부동산 가격 분포 (부의 불평등 모델링)",
            "주식 가격 및 금융 파생상품의 주가 시계열",
            "생물의 잠복기, 전염병 회복 기간, 미네랄 농도 분포",
            "재료의 피로 파괴 수명 및 부품 고장 시간"
        ],
        "links": [
            {"title": "NIST e-Handbook: Lognormal Distribution", "url": "https://www.itl.nist.gov/div898/handbook/eda/section3/eda3669.htm"},
            {"title": "Wikipedia: Log-normal Distribution", "url": "https://en.wikipedia.org/wiki/Log-normal_distribution"},
            {"title": "SciPy Docs: stats.lognorm", "url": "https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.lognorm.html"}
        ]
    },
    "t": {
        "name": "t-분포 (Student's t)",
        "type": "continuous",
        "formula_pdf": "f(t) = Γ((v+1)/2) / (√(vπ) Γ(v/2)) * (1 + t²/v)^(-(v+1)/2)",
        "formula_cdf": "F(t) = 1/2 + t*Γ((v+1)/2) * 2F1(1/2, (v+1)/2; 3/2; -t²/v) / (√(π v) Γ(v/2))",
        "mean_expr": "E[X] = μ (자유도 v > 1)",
        "var_expr": "Var(X) = σ² * v / (v - 2) (자유도 v > 2)",
        "skewness": "0 (대칭, v > 3)",
        "kurtosis": "6 / (v - 4) (v > 4, 정규분포보다 두꺼운 꼬리)",
        "params": [
            {
                "symbol": "v (자유도, df)",
                "range": "v > 0",
                "default": 10.0, "min": 1.0, "max": 100.0, "step": 1.0,
                "desc": "자유도가 작을수록 양끝 꼬리(Heavy-tail)가 두꺼워져 극단값 발생 확률이 높아지며, v가 커질수록(v ≥ 30) 정규분포에 수렴합니다."
            },
            {
                "symbol": "μ (위치 모수, loc)",
                "range": "-∞ < μ < ∞",
                "default": 0.0, "min": -10.0, "max": 10.0, "step": 0.5,
                "desc": "분포의 중심 위치(평균)를 설정합니다."
            },
            {
                "symbol": "σ (척도 모수, scale)",
                "range": "σ > 0",
                "default": 1.0, "min": 0.1, "max": 5.0, "step": 0.1,
                "desc": "분포의 스케일(너비)을 결정합니다."
            }
        ],
        "explanation": """
<b>Student의 t-분포</b>는 모집단의 표준편차를 알 수 없을 때, 소표본(n < 30)의 표본평균 검정(t-test) 및 신뢰구간 추정에 필수적인 분포입니다.<br>
정규분포보다 양끝 꼬리가 두꺼워 표본추출의 불확실성을 보정해줍니다.
""",
        "applications": [
            "단일 표본, 독립 2표본, 대응 표본 모평균 가설 검정 (t-Test)",
            "소표본 기반 모평균 신뢰구간(Confidence Interval) 계산",
            "선형 회귀분석 회귀계수의 유의성 검정",
            "극단적 금융 충격(Black Swan) 모델링"
        ],
        "links": [
            {"title": "NIST e-Handbook: t-Distribution", "url": "https://www.itl.nist.gov/div898/handbook/eda/section3/eda3664.htm"},
            {"title": "Wikipedia: Student's t-distribution", "url": "https://en.wikipedia.org/wiki/Student%27s_t-distribution"},
            {"title": "SciPy Docs: stats.t", "url": "https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.t.html"}
        ]
    },
    "chi2": {
        "name": "카이제곱분포 (Chi-squared)",
        "type": "continuous",
        "formula_pdf": "f(x) = 1 / (2^(k/2) Γ(k/2)) * x^(k/2 - 1) * exp(-x/2), x > 0",
        "formula_cdf": "F(x) = γ(k/2, x/2) / Γ(k/2)",
        "mean_expr": "E[X] = k",
        "var_expr": "Var(X) = 2k",
        "skewness": "√(8 / k) > 0 (양의 왜도)",
        "kurtosis": "12 / k",
        "params": [
            {
                "symbol": "k (자유도, df)",
                "range": "k > 0 (일반적으로 자연수)",
                "default": 5.0, "min": 1.0, "max": 50.0, "step": 1.0,
                "desc": "표준정규분포를 따르는 독립 확률변수의 제곱의 개수입니다. k가 증가할수록 평균(=k)이 우측으로 가며 종 모양으로 변합니다."
            }
        ],
        "explanation": """
<b>카이제곱분포</b>는 서로 독립인 k개의 표준정규분포 Z_1, ..., Z_k의 제곱합 Σ(Z_i)²이 따르는 확률분포입니다.<br>
표본분산의 표집분포이자 범주형 자료의 적합도 검정, 독립성/동질성 검정에 사용됩니다.
""",
        "applications": [
            "분할표(Contingency Table) 기반 카이제곱 독립성 및 동질성 검정",
            "이론적 분포와 실제 관측치 간의 적합도 검정 (Goodness-of-Fit)",
            "정규모집단에서 표본분산을 이용한 모분산 가설 검정 및 신뢰구간",
            "F-검정 및 분산분석(ANOVA) 통계량의 유도 기반"
        ],
        "links": [
            {"title": "NIST e-Handbook: Chi-Square Distribution", "url": "https://www.itl.nist.gov/div898/handbook/eda/section3/eda3666.htm"},
            {"title": "Wikipedia: Chi-squared distribution", "url": "https://en.wikipedia.org/wiki/Chi-squared_distribution"},
            {"title": "SciPy Docs: stats.chi2", "url": "https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.chi2.html"}
        ]
    },
    "f": {
        "name": "F-분포 (Snedecor's F)",
        "type": "continuous",
        "formula_pdf": "f(x) = (1 / B(d1/2, d2/2)) * (d1/d2)^(d1/2) * x^(d1/2 - 1) * (1 + (d1/d2)x)^(-(d1+d2)/2), x > 0",
        "formula_cdf": "F(x) = I_{(d1 x)/(d1 x + d2)}(d1/2, d2/2)",
        "mean_expr": "E[X] = d2 / (d2 - 2) (d2 > 2)",
        "var_expr": "Var(X) = 2 d2² (d1 + d2 - 2) / [d1 (d2 - 2)² (d2 - 4)] (d2 > 4)",
        "skewness": "(2d1 + d2 - 2)√(8(d2 - 4)) / [(d2 - 6)√(d1(d1 + d2 - 2))] (d2 > 6)",
        "kurtosis": "자유도 함수 (d2 > 8)",
        "params": [
            {
                "symbol": "d1 (분자 자유도, dfn)",
                "range": "d1 > 0",
                "default": 5.0, "min": 1.0, "max": 50.0, "step": 1.0,
                "desc": "분자에 위치한 카이제곱 변수의 자유도(예: 집단 간 분산의 자유도 k-1)."
            },
            {
                "symbol": "d2 (분모 자유도, dfd)",
                "range": "d2 > 0",
                "default": 10.0, "min": 1.0, "max": 100.0, "step": 1.0,
                "desc": "분모에 위치한 카이제곱 변수의 자유도(예: 집단 내 오차 분산의 자유도 N-k)."
            }
        ],
        "explanation": """
<b>F-분포</b>는 두 독립적인 카이제곱 변수를 각각의 자유도로 나눈 비율이 따르는 분포입니다.<br>
두 모집단의 분산 비교(등분산 검정) 및 분산분석(ANOVA), 회귀분석 모형의 전체 유의성 검정에 핵심적으로 사용됩니다.
""",
        "applications": [
            "두 집단의 모분산 동일성 검정 (F-test for equality of variances)",
            "일원/이원배치 분산분석(ANOVA)에서 집단 간 평균 차이 유의성 검정",
            "선형회귀분석 전체 결정계수(R²) 유의성 검정",
            "계량경제학 시계열 모형의 Granger 인과성 검정"
        ],
        "links": [
            {"title": "NIST e-Handbook: F-Distribution", "url": "https://www.itl.nist.gov/div898/handbook/eda/section3/eda3665.htm"},
            {"title": "Wikipedia: F-distribution", "url": "https://en.wikipedia.org/wiki/F-distribution"},
            {"title": "SciPy Docs: stats.f", "url": "https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.f.html"}
        ]
    },
    "expon": {
        "name": "지수분포 (Exponential)",
        "type": "continuous",
        "formula_pdf": "f(x) = λ exp(-λx), x ≥ 0",
        "formula_cdf": "F(x) = 1 - exp(-λx)",
        "mean_expr": "E[X] = 1 / λ",
        "var_expr": "Var(X) = 1 / λ²",
        "skewness": "2 (항상 강한 양의 왜도)",
        "kurtosis": "6 (뾰족한 첨도)",
        "params": [
            {
                "symbol": "λ (발생률, rate / 1/scale)",
                "range": "λ > 0",
                "default": 1.0, "min": 0.1, "max": 10.0, "step": 0.1,
                "desc": "단위 시간당 사건 발생 건수입니다. λ가 클수록 사건이 자주 발생하여 대기시간(X)이 짧아지고 급격히 감소합니다."
            }
        ],
        "explanation": """
<b>지수분포</b>는 포아송 과정을 따르는 사건들 사이의 <b>발생 간격(대기 시간)</b>을 모델링하는 연속형 확률분포입니다.<br>
유일하게 <b>무기억성(Memoryless Property: P(X > s+t | X > s) = P(X > t))</b>을 가집니다.
""",
        "applications": [
            "콜센터 상담원 대기 시간, 은행 고객 도착 간격",
            "전자 부품의 우발 고장 기간(신뢰성 공학)",
            "방사성 동위원소의 붕괴 간격",
            "웹 서버 요청 도달 간격 및 네트워크 패킷 딜레이"
        ],
        "links": [
            {"title": "NIST e-Handbook: Exponential Distribution", "url": "https://www.itl.nist.gov/div898/handbook/eda/section3/eda3667.htm"},
            {"title": "Wikipedia: Exponential distribution", "url": "https://en.wikipedia.org/wiki/Exponential_distribution"},
            {"title": "SciPy Docs: stats.expon", "url": "https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.expon.html"}
        ]
    },
    "gamma": {
        "name": "감마분포 (Gamma)",
        "type": "continuous",
        "formula_pdf": "f(x) = (1 / (Γ(α) θ^α)) * x^(α - 1) * exp(-x/θ), x > 0",
        "formula_cdf": "F(x) = γ(α, x/θ) / Γ(α)",
        "mean_expr": "E[X] = αθ",
        "var_expr": "Var(X) = αθ²",
        "skewness": "2 / √α",
        "kurtosis": "6 / α",
        "params": [
            {
                "symbol": "α (형태 모수, shape / k)",
                "range": "α > 0",
                "default": 2.0, "min": 0.2, "max": 15.0, "step": 0.2,
                "desc": "사건의 발생 횟수(지수분포 α개의 합). α=1이면 지수분포가 되며, α가 커질수록 정규분포 형태에 가까워집니다."
            },
            {
                "symbol": "θ (척도 모수, scale = 1/β)",
                "range": "θ > 0",
                "default": 1.0, "min": 0.1, "max": 10.0, "step": 0.1,
                "desc": "시간/크기 척도를 결정하며 클수록 분포가 가로로 넓게 팽창합니다."
            }
        ],
        "explanation": """
<b>감마분포</b>는 포아송 과정에서 α번째 사건이 발생할 때까지 걸리는 총 대기 시간을 모델링하는 일반화된 분포입니다.<br>
지수분포(α=1)와 카이제곱분포(α=k/2, θ=2)를 특수한 경우로 포함합니다.
""",
        "applications": [
            "일일/월별 강우량 및 기상 데이터 분석",
            "보험금 청구 총액 및 클레임 손실 규모 모델링",
            "암 치료 후 재발까지의 시간 또는 임상 시험 생존 분석",
            "베이지안 통계학에서 포아송/정규 정밀도의 켤레 사전분포(Conjugate Prior)"
        ],
        "links": [
            {"title": "NIST e-Handbook: Gamma Distribution", "url": "https://www.itl.nist.gov/div898/handbook/eda/section3/eda366b.htm"},
            {"title": "Wikipedia: Gamma distribution", "url": "https://en.wikipedia.org/wiki/Gamma_distribution"},
            {"title": "SciPy Docs: stats.gamma", "url": "https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.gamma.html"}
        ]
    },
    "weibull_min": {
        "name": "와이불분포 (Weibull)",
        "type": "continuous",
        "formula_pdf": "f(x) = (k/λ) * (x/λ)^(k-1) * exp(-(x/λ)^k), x ≥ 0",
        "formula_cdf": "F(x) = 1 - exp(-(x/λ)^k)",
        "mean_expr": "E[X] = λ Γ(1 + 1/k)",
        "var_expr": "Var(X) = λ² [Γ(1 + 2/k) - (Γ(1 + 1/k))²]",
        "skewness": "k에 따라 변화 (k ≈ 3.6일 때 왜도 ≈ 0)",
        "kurtosis": "k에 따라 변화",
        "params": [
            {
                "symbol": "k (형태 모수, shape)",
                "range": "k > 0",
                "default": 1.5, "min": 0.2, "max": 10.0, "step": 0.1,
                "desc": "고장률 특성을 결정: k < 1(초기 불량/감소형), k = 1(우발 고장/일정형=지수분포), k > 1(마모 고장/증가형), k ≈ 3.6(정규분포 유사)."
            },
            {
                "symbol": "λ (척도 모수, scale / 특성 수명)",
                "range": "λ > 0",
                "default": 1.0, "min": 0.1, "max": 10.0, "step": 0.2,
                "desc": "전체 시험체의 약 63.2%가 고장 나는 시점(특성 수명)을 나타냅니다."
            }
        ],
        "explanation": """
<b>와이불분포</b>는 신뢰성 공학 및 수명 데이터 분석(Survival Analysis)에서 가장 강력하고 표준적으로 사용되는 분포입니다.<br>
형태 모수 k에 따라 초기 고장, 우발 고장, 노화/마모 고장의 욕조 곡선(Bathtub Curve) 전 구간을 유연하게 표현할 수 있습니다.
""",
        "applications": [
            "반도체 칩, 전구, 베어링, 항공기 부품 등의 수명 시험 및 신뢰성 평가",
            "풍력 에너지 발전량 예측(풍속 분포 모델링)",
            "재료의 파괴 강도 및 인장 강도 통계",
            "기상 극값(최대 풍속, 극한 기후) 예측"
        ],
        "links": [
            {"title": "NIST e-Handbook: Weibull Distribution", "url": "https://www.itl.nist.gov/div898/handbook/eda/section3/eda3668.htm"},
            {"title": "Wikipedia: Weibull distribution", "url": "https://en.wikipedia.org/wiki/Weibull_distribution"},
            {"title": "SciPy Docs: stats.weibull_min", "url": "https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.weibull_min.html"}
        ]
    },
    "uniform": {
        "name": "연속균일분포 (Uniform)",
        "type": "continuous",
        "formula_pdf": "f(x) = 1 / (b - a), a ≤ x ≤ b",
        "formula_cdf": "F(x) = (x - a) / (b - a)",
        "mean_expr": "E[X] = (a + b) / 2",
        "var_expr": "Var(X) = (b - a)² / 12",
        "skewness": "0 (완전 대칭)",
        "kurtosis": "-1.2 (평평한 형태)",
        "params": [
            {
                "symbol": "a (구간 최소값, loc)",
                "range": "-∞ < a < b",
                "default": 0.0, "min": -20.0, "max": 20.0, "step": 1.0,
                "desc": "정의역의 시작 지점입니다."
            },
            {
                "symbol": "b (구간 최대값, loc + scale)",
                "range": "b > a",
                "default": 1.0, "min": -10.0, "max": 30.0, "step": 1.0,
                "desc": "정의역의 끝 지점입니다."
            }
        ],
        "explanation": """
<b>연속균일분포</b>는 정해진 유한 구간 [a, b] 내에서 모든 값이 발생할 확률밀도가 동일한 가장 단순한 직사각형 분포입니다.<br>
사전 정보가 전혀 없는 무정보 상태를 나타냅니다.
""",
        "applications": [
            "컴퓨터 의사 난수 생성기(PRNG)의 기본 U(0, 1) 난수 생성",
            "양자화 오차 및 수치 반올림 오차 모델링",
            "몬테카를로 시뮬레이션의 표본 역변환 생성(Inverse Transform Sampling)",
            "베이지안 모수 추정의 무정보 사전분포(Uniform Prior)"
        ],
        "links": [
            {"title": "NIST e-Handbook: Uniform Distribution", "url": "https://www.itl.nist.gov/div898/handbook/eda/section3/eda3662.htm"},
            {"title": "Wikipedia: Continuous uniform distribution", "url": "https://en.wikipedia.org/wiki/Continuous_uniform_distribution"},
            {"title": "SciPy Docs: stats.uniform", "url": "https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.uniform.html"}
        ]
    },
    "beta": {
        "name": "베타분포 (Beta)",
        "type": "continuous",
        "formula_pdf": "f(x) = (1 / B(α, β)) * x^(α - 1) * (1 - x)^(β - 1), 0 ≤ x ≤ 1",
        "formula_cdf": "F(x) = I_x(α, β)",
        "mean_expr": "E[X] = α / (α + β)",
        "var_expr": "Var(X) = (αβ) / [ (α + β)² (α + β + 1) ]",
        "skewness": "2(β - α)√(α + β + 1) / [ (α + β + 2)√(αβ) ]",
        "kurtosis": "형태 모수 의존",
        "params": [
            {
                "symbol": "α (형태 모수 1)",
                "range": "α > 0",
                "default": 2.0, "min": 0.2, "max": 15.0, "step": 0.2,
                "desc": "성공 횟수와 관련된 모수입니다. α가 β보다 크면 분포가 1(우측) 쪽으로 쏠립니다."
            },
            {
                "symbol": "β (형태 모수 2)",
                "range": "β > 0",
                "default": 5.0, "min": 0.2, "max": 15.0, "step": 0.2,
                "desc": "실패 횟수와 관련된 모수입니다. β가 α보다 크면 분포가 0(좌측) 쪽으로 쏠립니다."
            }
        ],
        "explanation": """
<b>베타분포</b>는 [0, 1] 구간에서 정의되는 연속확률분포로, <b>비율, 확률, 성공률</b> 등의 불확실성을 모델링하는 데 가장 널리 사용됩니다.<br>
이항분포(Binomial) 성공확률 p에 대한 베이지안 켤레 사전분포로 핵심적인 역할을 합니다.
""",
        "applications": [
            "A/B 테스트 전환율(Conversion Rate) 및 클릭률(CTR) 모델링",
            "프로젝트 관리(PERT/CPM) 작업 소요 시간 추정",
            "야구 선수의 타율, 배터리 잔량 비율 등 0~1 구간 비율 통계",
            "베이지안 신뢰도 갱신 및 밴딧(Multi-Armed Bandit) 알고리즘"
        ],
        "links": [
            {"title": "NIST e-Handbook: Beta Distribution", "url": "https://www.itl.nist.gov/div898/handbook/eda/section3/eda366h.htm"},
            {"title": "Wikipedia: Beta distribution", "url": "https://en.wikipedia.org/wiki/Beta_distribution"},
            {"title": "SciPy Docs: stats.beta", "url": "https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.beta.html"}
        ]
    },
    "cauchy": {
        "name": "코시분포 (Cauchy / Lorentz)",
        "type": "continuous",
        "formula_pdf": "f(x) = 1 / [ π γ (1 + ((x - x0)/γ)²) ]",
        "formula_cdf": "F(x) = (1/π) * arctan((x - x0)/γ) + 1/2",
        "mean_expr": "E[X] = 정의되지 않음 (Undefined)",
        "var_expr": "Var(X) = 정의되지 않음 (∞)",
        "skewness": "정의되지 않음",
        "kurtosis": "정의되지 않음",
        "params": [
            {
                "symbol": "x0 (위치 모수 / 중앙값, loc)",
                "range": "-∞ < x0 < ∞",
                "default": 0.0, "min": -10.0, "max": 10.0, "step": 0.5,
                "desc": "분포의 대칭 중심(중앙값 및 최빈값)입니다."
            },
            {
                "symbol": "γ (척도 모수, scale)",
                "range": "γ > 0",
                "default": 1.0, "min": 0.1, "max": 10.0, "step": 0.2,
                "desc": "곡선의 너비를 결정하며, 정규분포보다 꼬리가 극단적으로 무겁습니다."
            }
        ],
        "explanation": """
<b>코시분포(로렌츠 분포)</b>는 물리학의 공명 현상 및 회절 현상에서 유도되는 분포입니다.<br>
꼬리가 너무 두꺼워 적분이 수렴하지 않기 때문에 <b>수학적 평균과 분산이 존재하지 않는</b> 대표적인 병리적 통계 분포입니다.
""",
        "applications": [
            "물리학의 원자 분광학 스펙트럼 선폭(Lorentzian Line Shape)",
            "강한 이상치(Outlier)가 빈번한 금융 충격 모의실험",
            "두 독립 표준정규분포 확률변수의 비율 Z1 / Z2",
            "이상치에 강건한 로버스트(Robust) 베이지안 회귀"
        ],
        "links": [
            {"title": "NIST e-Handbook: Cauchy Distribution", "url": "https://www.itl.nist.gov/div898/handbook/eda/section3/eda3663.htm"},
            {"title": "Wikipedia: Cauchy distribution", "url": "https://en.wikipedia.org/wiki/Cauchy_distribution"},
            {"title": "SciPy Docs: stats.cauchy", "url": "https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.cauchy.html"}
        ]
    },
    "laplace": {
        "name": "라플라스분포 (Laplace / Double Exponential)",
        "type": "continuous",
        "formula_pdf": "f(x) = (1 / 2b) * exp(-|x - μ| / b)",
        "formula_cdf": "F(x) = (1/2)exp((x-μ)/b) (x < μ) / 1 - (1/2)exp(-(x-μ)/b) (x ≥ μ)",
        "mean_expr": "E[X] = μ",
        "var_expr": "Var(X) = 2b²",
        "skewness": "0 (대칭)",
        "kurtosis": "3 (정규분포보다 중심이 뾰족함)",
        "params": [
            {
                "symbol": "μ (위치 모수, loc)",
                "range": "-∞ < μ < ∞",
                "default": 0.0, "min": -10.0, "max": 10.0, "step": 0.5,
                "desc": "분포의 중심(첨점, 중앙값, 평균)입니다."
            },
            {
                "symbol": "b (척도 모수, scale)",
                "range": "b > 0",
                "default": 1.0, "min": 0.1, "max": 5.0, "step": 0.1,
                "desc": "분포의 퍼짐 정도입니다."
            }
        ],
        "explanation": """
<b>라플라스분포(이중 지수분포)</b>는 두 개의 지수분포를 중심 μ를 기준으로 등을 맞대어 붙인 형태의 대칭 분포입니다.<br>
머신러닝의 L1 정규화(Lasso Regression)와 차분 프라이버시(Differential Privacy)의 핵심 기반입니다.
""",
        "applications": [
            "머신러닝 Lasso(L1 정규화) 회귀의 사전분포 (희소성 유도)",
            "차분 프라이버시(Differential Privacy) 노이즈 추가 메커니즘",
            "금융 자산 고빈도 매매 수익률의 뾰족한 첨두 모델링",
            "오디오/음성 신호 처리 및 영상 압축(JPEG-DCT 계수)"
        ],
        "links": [
            {"title": "Wikipedia: Laplace distribution", "url": "https://en.wikipedia.org/wiki/Laplace_distribution"},
            {"title": "SciPy Docs: stats.laplace", "url": "https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.laplace.html"}
        ]
    },
    "logistic": {
        "name": "로지스틱분포 (Logistic)",
        "type": "continuous",
        "formula_pdf": "f(x) = exp(-(x-μ)/s) / [ s (1 + exp(-(x-μ)/s))² ]",
        "formula_cdf": "F(x) = 1 / [ 1 + exp(-(x-μ)/s) ] (Sigmoid 함수)",
        "mean_expr": "E[X] = μ",
        "var_expr": "Var(X) = s² π² / 3",
        "skewness": "0",
        "kurtosis": "1.2",
        "params": [
            {
                "symbol": "μ (위치 모수, loc)",
                "range": "-∞ < μ < ∞",
                "default": 0.0, "min": -10.0, "max": 10.0, "step": 0.5,
                "desc": "분포의 중심입니다."
            },
            {
                "symbol": "s (척도 모수, scale)",
                "range": "s > 0",
                "default": 1.0, "min": 0.1, "max": 5.0, "step": 0.1,
                "desc": "스케일 모수입니다."
            }
        ],
        "explanation": """
<b>로지스틱분포</b>는 정규분포와 매우 흡사한 종 모양이지만 꼬리가 좀 더 길고 완만합니다.<br>
누적분포함수가 널리 알려진 <b>시그모이드(Sigmoid / Logit) 함수</b> 형태를 띠어 로지스틱 회귀분석 및 신경망 활성화 함수에 사용됩니다.
""",
        "applications": [
            "로지스틱 회귀분석(Logistic Regression) 및 분류 알고리즘",
            "체스/E-스포츠의 Elo 레이팅 시스템",
            "생물 개체수 증식 및 신기술 수용 확산 모델(S-곡선)",
            "항암제 투약 반응 곡선(Dose-Response Curve)"
        ],
        "links": [
            {"title": "Wikipedia: Logistic distribution", "url": "https://en.wikipedia.org/wiki/Logistic_distribution"},
            {"title": "SciPy Docs: stats.logistic", "url": "https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.logistic.html"}
        ]
    },
    "pareto": {
        "name": "파레토분포 (Pareto / 80-20)",
        "type": "continuous",
        "formula_pdf": "f(x) = (α xm^α) / x^(α + 1), x ≥ xm",
        "formula_cdf": "F(x) = 1 - (xm / x)^α",
        "mean_expr": "E[X] = (α xm) / (α - 1) (α > 1)",
        "var_expr": "Var(X) = (α xm²) / [ (α-1)² (α-2) ] (α > 2)",
        "skewness": "[2(1+α) / (α-3)] * √((α-2)/α) (α > 3)",
        "kurtosis": "Power-law heavy tail",
        "params": [
            {
                "symbol": "α (형태 모수, shape / Pareto index)",
                "range": "α > 0",
                "default": 3.0, "min": 0.5, "max": 10.0, "step": 0.2,
                "desc": "지수 지수(파레토 계수)입니다. 작을수록 극소수가 전체 자원의 대부분을 차지하는 극단적 불평등(롱테일)이 심해집니다."
            },
            {
                "symbol": "xm (최소값 척도 모수, scale)",
                "range": "xm > 0",
                "default": 1.0, "min": 0.1, "max": 10.0, "step": 0.2,
                "desc": "분포의 최소 시작점입니다."
            }
        ],
        "explanation": """
<b>파레토분포</b>는 거듭제곱 법칙(Power Law)을 따르는 두터운 꼬리(Fat Tail) 분포의 대표격입니다.<br>
'상위 20%의 사람이 전체 부의 80%를 소유한다'는 <b>파레토 법칙(80-20 Rule)</b>을 수학적으로 정립한 분포입니다.
""",
        "applications": [
            "사회적 부 및 소득 분배의 불평등 분석",
            "도시별 인구 수(지프의 법칙), 웹사이트 트래픽 및 소셜 네트워크 팔로워 수",
            "지진의 규모(구텐베르크-릭터 법칙), 운석 크기 분포",
            "초대형 손해보험의 위험 청구액(Catastrophe Risk)"
        ],
        "links": [
            {"title": "Wikipedia: Pareto distribution", "url": "https://en.wikipedia.org/wiki/Pareto_distribution"},
            {"title": "SciPy Docs: stats.pareto", "url": "https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.pareto.html"}
        ]
    },
    "rayleigh": {
        "name": "레일리분포 (Rayleigh)",
        "type": "continuous",
        "formula_pdf": "f(x) = (x / σ²) * exp(-x² / (2σ²)), x ≥ 0",
        "formula_cdf": "F(x) = 1 - exp(-x² / (2σ²))",
        "mean_expr": "E[X] = σ √(π/2) ≈ 1.2533 σ",
        "var_expr": "Var(X) = ((4 - π)/2) σ² ≈ 0.4292 σ²",
        "skewness": "2√π (π - 3) / (4 - π)^(3/2) ≈ 0.6311",
        "kurtosis": "0.2451",
        "params": [
            {
                "symbol": "σ (척도 모수, scale)",
                "range": "σ > 0",
                "default": 1.0, "min": 0.1, "max": 10.0, "step": 0.2,
                "desc": "성분 정규분포의 표준편차입니다. σ가 커질수록 최빈값(=σ)이 오른쪽으로 이동하며 넓어집니다."
            }
        ],
        "explanation": """
<b>레일리분포</b>는 서로 독립인 두 정규분포 X, Y ~ N(0, σ²)로 이루어진 2차원 직교 벡터의 크기(길이) R = √(X² + Y²)가 따르는 분포입니다.<br>
무선 통신의 페이딩(Fading) 채널 모델링에 필수적입니다.
""",
        "applications": [
            "무선 통신 다중경로 신호 감쇄(Rayleigh Fading Channel)",
            "해양학 파도의 파고(Wave Height) 통계",
            "MRI 영상의 노이즈 분석",
            "2차원 풍속 벡터의 크기 모델링"
        ],
        "links": [
            {"title": "Wikipedia: Rayleigh distribution", "url": "https://en.wikipedia.org/wiki/Rayleigh_distribution"},
            {"title": "SciPy Docs: stats.rayleigh", "url": "https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.rayleigh.html"}
        ]
    },

    # 이산형 분포
    "binom": {
        "name": "이항분포 (Binomial)",
        "type": "discrete",
        "formula_pdf": "P(X = k) = C(n, k) * p^k * (1-p)^(n-k), k ∈ {0, 1, ..., n}",
        "formula_cdf": "F(k) = I_{1-p}(n-k, k+1)",
        "mean_expr": "E[X] = np",
        "var_expr": "Var(X) = np(1-p)",
        "skewness": "(1 - 2p) / √(np(1-p))",
        "kurtosis": "(1 - 6p(1-p)) / (np(1-p))",
        "params": [
            {
                "symbol": "n (독립 시행 횟수)",
                "range": "n ∈ ℕ",
                "default": 10.0, "min": 1.0, "max": 100.0, "step": 1.0,
                "desc": "동일한 베르누이 시행을 반복하는 총 횟수입니다."
            },
            {
                "symbol": "p (단일 시행 성공 확률)",
                "range": "0 ≤ p ≤ 1",
                "default": 0.5, "min": 0.01, "max": 0.99, "step": 0.05,
                "desc": "각 시행에서 성공할 확률입니다. p=0.5일 때 완전 대칭 종 모양을 형성합니다."
            }
        ],
        "explanation": """
<b>이항분포</b>는 매 시행마다 성공 확률이 p로 일정한 독립적인 베르누이 시행을 n번 반복했을 때의 <b>총 성공 횟수 k</b>의 확률분포입니다.<br>
n이 충분히 크면 드무아브르-라플라스 정리에 의해 정규분포로 근사됩니다.
""",
        "applications": [
            "제조업 품질 관리의 불량품 개수 검사 및 샘플링 검사",
            "의약품 임상 시험 환자 치료 반응 성공률",
            "동전 던지기, 복권 및 도박 승패 확률 계산",
            "선거 출구조사 및 여론조사 오차범위 산정"
        ],
        "links": [
            {"title": "NIST e-Handbook: Binomial Distribution", "url": "https://www.itl.nist.gov/div898/handbook/eda/section3/eda366i.htm"},
            {"title": "Wikipedia: Binomial distribution", "url": "https://en.wikipedia.org/wiki/Binomial_distribution"},
            {"title": "SciPy Docs: stats.binom", "url": "https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.binom.html"}
        ]
    },
    "poisson": {
        "name": "포아송분포 (Poisson)",
        "type": "discrete",
        "formula_pdf": "P(X = k) = (λ^k * exp(-λ)) / k!, k ∈ {0, 1, 2, ...}",
        "formula_cdf": "F(k) = Γ(⌊k+1⌋, λ) / ⌊k⌋!",
        "mean_expr": "E[X] = λ",
        "var_expr": "Var(X) = λ (평균과 분산이 동일)",
        "skewness": "1 / √λ",
        "kurtosis": "1 / λ",
        "params": [
            {
                "symbol": "λ (단위 시간/공간당 평균 발생률)",
                "range": "λ > 0",
                "default": 3.0, "min": 0.1, "max": 30.0, "step": 0.5,
                "desc": "주어진 단위 구간 내에서 발생하는 평균 사건 건수입니다. λ가 커질수록 정규분포에 근사합니다."
            }
        ],
        "explanation": """
<b>포아송분포</b>는 정해진 단위 시간이나 공간 내에서 드물게 발생하는 사건의 <b>총 발생 건수</b>를 나타내는 이산확률분포입니다.<br>
<b>평균과 분산이 모두 λ로 완벽하게 동일</b>하다는 독특한 성질을 가지고 있습니다.
""",
        "applications": [
            "콜센터에 1시간 동안 걸려오는 문의 전화 수",
            "1년 동안 특정 교차로에서 발생하는 교통사고 건수",
            "웹사이트 서버에 1초 동안 인입되는 HTTP 요청 수",
            "생물학에서 배양 접시 단위 면적당 박테리아 군집 수"
        ],
        "links": [
            {"title": "NIST e-Handbook: Poisson Distribution", "url": "https://www.itl.nist.gov/div898/handbook/eda/section3/eda366j.htm"},
            {"title": "Wikipedia: Poisson distribution", "url": "https://en.wikipedia.org/wiki/Poisson_distribution"},
            {"title": "SciPy Docs: stats.poisson", "url": "https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.poisson.html"}
        ]
    },
    "geom": {
        "name": "기하분포 (Geometric)",
        "type": "discrete",
        "formula_pdf": "P(X = k) = (1-p)^(k-1) * p, k ∈ {1, 2, 3, ...}",
        "formula_cdf": "F(k) = 1 - (1-p)^k",
        "mean_expr": "E[X] = 1 / p",
        "var_expr": "Var(X) = (1 - p) / p²",
        "skewness": "(2 - p) / √(1 - p)",
        "kurtosis": "6 + p² / (1 - p)",
        "params": [
            {
                "symbol": "p (성공 확률)",
                "range": "0 < p ≤ 1",
                "default": 0.5, "min": 0.05, "max": 0.95, "step": 0.05,
                "desc": "각 시도에서의 성공 확률입니다. p가 작을수록 첫 성공까지 필요한 시도 횟수(E[X]=1/p)가 늘어납니다."
            }
        ],
        "explanation": """
<b>기하분포</b>는 베르누이 시행에서 <b>첫 번째 성공이 나올 때까지 필요한 총 시행 횟수 k</b>의 분포입니다.<br>
이산확률분포 중 유일하게 <b>무기억성(Memoryless Property)</b>을 가집니다.
""",
        "applications": [
            "면접 합격이나 자격증 시험에 처음 합격할 때까지의 응시 횟수",
            "네트워크 패킷이 오류 없이 목적지에 도달할 때까지의 재전송 횟수",
            "온라인 게임에서 아이템 강화에 첫 성공할 때까지의 시도 횟수",
            "영업 사원이 첫 계약을 성사시킬 때까지의 고객 방문 횟수"
        ],
        "links": [
            {"title": "Wikipedia: Geometric distribution", "url": "https://en.wikipedia.org/wiki/Geometric_distribution"},
            {"title": "SciPy Docs: stats.geom", "url": "https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.geom.html"}
        ]
    },
    "hypergeom": {
        "name": "초기하분포 (Hypergeometric)",
        "type": "discrete",
        "formula_pdf": "P(X = k) = [ C(K, k) * C(N-K, n-k) ] / C(N, n)",
        "formula_cdf": "F(k) = Σ P(X = i)",
        "mean_expr": "E[X] = n * (K / N)",
        "var_expr": "Var(X) = n * (K/N) * ((N-K)/N) * ((N-n)/(N-1))",
        "skewness": "(N-2K)√(N-1)(N-2n) / [ √(nK(N-K)(N-n)) * (N-2) ]",
        "kurtosis": "Finite population kurtosis",
        "params": [
            {
                "symbol": "N (전체 모집단 크기)",
                "range": "N ≥ 1",
                "default": 20.0, "min": 5.0, "max": 100.0, "step": 1.0,
                "desc": "비복원 추출 대상이 되는 전체 유한 모집단의 크기입니다."
            },
            {
                "symbol": "K (모집단 내 성공 아이템 총수)",
                "range": "0 ≤ K ≤ N",
                "default": 7.0, "min": 1.0, "max": 50.0, "step": 1.0,
                "desc": "모집단 전체에 들어있는 당첨/성공 아이템의 총 개수입니다."
            },
            {
                "symbol": "n (표본 추출 횟수)",
                "range": "1 ≤ n ≤ N",
                "default": 12.0, "min": 1.0, "max": 50.0, "step": 1.0,
                "desc": "모집단에서 비복원으로 무작위 추출하는 표본의 크기입니다."
            }
        ],
        "explanation": """
<b>초기하분포</b>는 유한한 모집단에서 <b>비복원 추출(Without Replacement)</b>을 할 때 표본에 포함되는 성공 개수 k의 확률분포입니다.<br>
이항분포(복원추출)와 달리 표본을 뽑을 때마다 성공 확률이 동적으로 변화합니다.
""",
        "applications": [
            "로또 복권 6개 번호 중 당첨 번호 일치 개수 계산",
            "유권자 출구조사 및 배심원단 무작위 선출 비율 검정",
            "생물학 표지 재포획법(Mark-Recapture) 야생동물 개체수 추정",
            "Fisher의 정확 검정(Fisher's Exact Test) 계산 기반"
        ],
        "links": [
            {"title": "Wikipedia: Hypergeometric distribution", "url": "https://en.wikipedia.org/wiki/Hypergeometric_distribution"},
            {"title": "SciPy Docs: stats.hypergeom", "url": "https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.hypergeom.html"}
        ]
    },
    "nbinom": {
        "name": "음이항분포 (Negative Binomial)",
        "type": "discrete",
        "formula_pdf": "P(X = k) = C(k + r - 1, k) * (1-p)^k * p^r, k ∈ {0, 1, 2, ...}",
        "formula_cdf": "F(k) = I_p(r, k+1)",
        "mean_expr": "E[X] = r(1 - p) / p",
        "var_expr": "Var(X) = r(1 - p) / p² > E[X] (과산포 모델링)",
        "skewness": "(2 - p) / √(r(1 - p))",
        "kurtosis": "6/r + p² / (r(1 - p))",
        "params": [
            {
                "symbol": "r (목표 성공 횟수)",
                "range": "r > 0",
                "default": 5.0, "min": 1.0, "max": 50.0, "step": 1.0,
                "desc": "달성하고자 하는 총 성공 횟수입니다."
            },
            {
                "symbol": "p (단일 시행 성공 확률)",
                "range": "0 < p < 1",
                "default": 0.5, "min": 0.05, "max": 0.95, "step": 0.05,
                "desc": "각 시행에서 성공할 확률입니다."
            }
        ],
        "explanation": """
<b>음이항분포</b>는 r번째 성공을 거둘 때까지 겪게 되는 <b>실패 횟수 k</b>의 확률분포입니다.<br>
포아송분포와 달리 <b>분산이 평균보다 큰 과산포(Overdispersion) 데이터</b>를 유연하게 적합할 수 있어 유전체학 및 데이터 분석에 필수적입니다.
""",
        "applications": [
            "RNA-Seq 유전자 발현 카운트 데이터 모델링",
            "전자상거래 고객의 연간 구매 횟수(과산포 카운트)",
            "병원 응급실 일일 환자 방문 수 모델링",
            "사격 선수가 표적을 10회 명중시킬 때까지 빗나간 발수"
        ],
        "links": [
            {"title": "Wikipedia: Negative binomial distribution", "url": "https://en.wikipedia.org/wiki/Negative_binomial_distribution"},
            {"title": "SciPy Docs: stats.nbinom", "url": "https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.nbinom.html"}
        ]
    },
    "randint": {
        "name": "이산균일분포 (Discrete Uniform)",
        "type": "discrete",
        "formula_pdf": "P(X = k) = 1 / (b - a + 1), k ∈ {a, a+1, ..., b}",
        "formula_cdf": "F(k) = (⌊k⌋ - a + 1) / (b - a + 1)",
        "mean_expr": "E[X] = (a + b) / 2",
        "var_expr": "Var(X) = ((b - a + 1)² - 1) / 12",
        "skewness": "0 (대칭)",
        "kurtosis": "-6((b-a+1)² + 1) / [5((b-a+1)² - 1)]",
        "params": [
            {
                "symbol": "a (최소 정수값)",
                "range": "a ∈ ℤ",
                "default": 1.0, "min": -20.0, "max": 20.0, "step": 1.0,
                "desc": "정의역의 시작 정수입니다."
            },
            {
                "symbol": "b (최대 정수값)",
                "range": "b ≥ a, b ∈ ℤ",
                "default": 6.0, "min": -10.0, "max": 30.0, "step": 1.0,
                "desc": "정의역의 끝 정수입니다."
            }
        ],
        "explanation": """
<b>이산균일분포</b>는 정수 범위 [a, b] 내의 모든 정수가 동일한 확률로 발생하는 분포입니다.<br>
대표적으로 6면체 공정한 주사위 던지기(a=1, b=6)가 이에 해당합니다.
""",
        "applications": [
            "정육면체 주사위 및 룰렛 번호 추첨",
            "암호학 및 난수 생성 알고리즘의 정수 셔플링",
            "모든 선택지가 동등하게 발생할 때의 베이지안 균일 사전확률"
        ],
        "links": [
            {"title": "Wikipedia: Discrete uniform distribution", "url": "https://en.wikipedia.org/wiki/Discrete_uniform_distribution"},
            {"title": "SciPy Docs: stats.randint", "url": "https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.randint.html"}
        ]
    }
}


class KnowledgeHubDialog(QDialog):
    """
    통계 지식 및 수식 사전 (Knowledge Hub Dialog)
    검색, 분류 탐색, 상세 수식/모수/적용사례 뷰어 및 외부 링크 연동 제공
    """
    def __init__(self, parent=None, initial_dist_key=None):
        super().__init__(parent)
        self.setWindowTitle("📚 통계 지식 & 수식 사전 (Statistical Knowledge Hub)")
        self.resize(900, 700)
        self.initial_dist_key = initial_dist_key
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # 상단 검색 바
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("🔍 <b>지식 검색:</b>"))
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("분포 이름, 모수(평균, 표준편차), 활용사례 검색...")
        self.search_input.textChanged.connect(self.filter_list)
        search_layout.addWidget(self.search_input)
        
        self.type_filter = QComboBox()
        self.type_filter.addItems(["전체 (All)", "연속형 분포 (Continuous)", "이산형 분포 (Discrete)"])
        self.type_filter.currentIndexChanged.connect(self.filter_list)
        search_layout.addWidget(self.type_filter)
        
        layout.addLayout(search_layout)
        
        # 본문 분할 화면
        splitter = QSplitter(Qt.Horizontal)
        
        # 좌측 분포 리스트
        self.dist_list = QListWidget()
        self.dist_list.setFixedWidth(280)
        self.dist_list.currentItemChanged.connect(self.on_dist_selected)
        splitter.addWidget(self.dist_list)
        
        # 우측 상세 뷰어 (HTML 렌더링 지원)
        self.detail_browser = QTextBrowser()
        self.detail_browser.setOpenExternalLinks(True)
        self.detail_browser.setStyleSheet("padding: 12px; font-size: 10.5pt; line-height: 1.5;")
        splitter.addWidget(self.detail_browser)
        
        splitter.setSizes([280, 620])
        layout.addWidget(splitter)
        
        # 하단 닫기 버튼
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        btn_close = QPushButton("닫기")
        btn_close.setFixedWidth(100)
        btn_close.clicked.connect(self.accept)
        bottom_layout.addWidget(btn_close)
        layout.addLayout(bottom_layout)
        
        self.populate_list()
        
        if self.initial_dist_key:
            self.select_dist_key(self.initial_dist_key)

    def populate_list(self):
        self.dist_list.clear()
        query = self.search_input.text().lower().strip()
        type_idx = self.type_filter.currentIndex()
        
        for key, info in DISTRIBUTION_KNOWLEDGE.items():
            if type_idx == 1 and info["type"] != "continuous":
                continue
            if type_idx == 2 and info["type"] != "discrete":
                continue
                
            match = (
                query in key.lower() or 
                query in info["name"].lower() or 
                query in info["explanation"].lower() or
                any(query in app.lower() for app in info["applications"])
            )
            
            if match:
                item = QListWidgetItem(info["name"])
                item.setData(Qt.UserRole, key)
                self.dist_list.addItem(item)
                
        if self.dist_list.count() > 0 and self.dist_list.currentRow() == -1:
            self.dist_list.setCurrentRow(0)

    def filter_list(self):
        self.populate_list()

    def select_dist_key(self, dist_key):
        for i in range(self.dist_list.count()):
            item = self.dist_list.item(i)
            if item.data(Qt.UserRole) == dist_key:
                self.dist_list.setCurrentItem(item)
                break

    def on_dist_selected(self, current, previous):
        if not current:
            self.detail_browser.clear()
            return
        
        dist_key = current.data(Qt.UserRole)
        info = DISTRIBUTION_KNOWLEDGE.get(dist_key)
        if not info:
            return
        
        # Build Rich HTML Document
        html = []
        html.append(f"<h2 style='color: #0d6efd; margin-bottom: 4px;'>{info['name']}</h2>")
        html.append(f"<p style='color: #666;'><b>분류:</b> {'연속형 확률분포 (Continuous)' if info['type']=='continuous' else '이산형 확률분포 (Discrete)'} | <b>식별키:</b> <code>{dist_key}</code></p>")
        html.append("<hr style='border: 0; border-top: 1px solid #ccc;'>")
        
        html.append("<h3>📖 개념 및 핵심 성질</h3>")
        html.append(f"<div style='background-color: rgba(13, 110, 253, 0.07); padding: 12px; border-radius: 6px;'>{info['explanation']}</div>")
        
        html.append("<h3>📐 수학적 정의 및 수식</h3>")
        html.append("<table style='width: 100%; border-collapse: collapse; margin-bottom: 12px;'>")
        func_label = "확률밀도함수 (PDF)" if info['type'] == 'continuous' else "확률질량함수 (PMF)"
        html.append(f"<tr><td style='padding: 6px; font-weight: bold; width: 190px; background: rgba(0,0,0,0.04);'>f(x) {func_label}:</td><td style='padding: 6px;'><code>{info['formula_pdf']}</code></td></tr>")
        html.append(f"<tr><td style='padding: 6px; font-weight: bold; background: rgba(0,0,0,0.04);'>F(x) 누적분포함수 (CDF):</td><td style='padding: 6px;'><code>{info['formula_cdf']}</code></td></tr>")
        html.append(f"<tr><td style='padding: 6px; font-weight: bold; background: rgba(0,0,0,0.04);'>기댓값 (평균 E[X]):</td><td style='padding: 6px;'><code>{info['mean_expr']}</code></td></tr>")
        html.append(f"<tr><td style='padding: 6px; font-weight: bold; background: rgba(0,0,0,0.04);'>분산 (Var(X)):</td><td style='padding: 6px;'><code>{info['var_expr']}</code></td></tr>")
        html.append(f"<tr><td style='padding: 6px; font-weight: bold; background: rgba(0,0,0,0.04);'>왜도 (Skewness):</td><td style='padding: 6px;'>{info['skewness']}</td></tr>")
        html.append(f"<tr><td style='padding: 6px; font-weight: bold; background: rgba(0,0,0,0.04);'>첨도 (Kurtosis):</td><td style='padding: 6px;'>{info['kurtosis']}</td></tr>")
        html.append("</table>")
        
        html.append("<h3>🎛️ 모수(Parameter) 상세 해설</h3>")
        html.append("<ul style='padding-left: 20px;'>")
        for p in info["params"]:
            html.append(f"<li><b>{p['symbol']}</b> (정의역: <code>{p['range']}</code>)<br><span style='color: #333;'>{p['desc']}</span></li><br>")
        html.append("</ul>")
        
        html.append("<h3>💡 주요 실생활 및 산업 적용 사례</h3>")
        html.append("<ul style='padding-left: 20px;'>")
        for app in info["applications"]:
            html.append(f"<li>{app}</li>")
        html.append("</ul>")
        
        html.append("<h3>🌐 신뢰할 수 있는 외부 레퍼런스</h3>")
        html.append("<ul style='padding-left: 20px;'>")
        for link in info["links"]:
            html.append(f"<li><a href='{link['url']}' style='color: #0d6efd; text-decoration: none; font-weight: bold;'>🔗 {link['title']}</a></li>")
        html.append("</ul>")
        
        self.detail_browser.setHtml("".join(html))
