# 🌌 AlphaSpace (알파스페이스)
### 차세대 통계 확률 분포 인터랙티브 시뮬레이션 및 데이터 분석 도구
> **Interactive Probability Distributions Simulation, Data Fitting & Hypothesis Testing Platform**

<p align="center">
  <img src="https://img.shields.io/badge/Version-v2.1.0_Enterprise-00F2FE?style=for-the-badge" alt="Version"/>
  <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version"/>
  <img src="https://img.shields.io/badge/GUI-PySide6%20(Qt6)-41CD52?style=for-the-badge&logo=qt&logoColor=white" alt="PySide6 GUI"/>
  <img src="https://img.shields.io/badge/SciPy-1.15+-8CAAE6?style=for-the-badge&logo=scipy&logoColor=white" alt="SciPy"/>
  <img src="https://img.shields.io/badge/Docs-GitHub_Pages-4FACFE?style=for-the-badge&logo=github&logoColor=white" alt="GitHub Pages Docs"/>
  <img src="https://img.shields.io/badge/Package-Single%20Standalone%20EXE-FF6F00?style=for-the-badge" alt="Standalone"/>
  <img src="https://img.shields.io/badge/License-MIT-blue.svg?style=for-the-badge" alt="License"/>
</p>

> 🌐 **[AlphaSpace 공식 사용자 매뉴얼 & 인터랙티브 웹 시뮬레이터 바로가기 (GitHub Pages)](https://comraonworld.github.io/AlphaSpace/)**  
> *프로그램 설치 없이 웹 브라우저에서 21종 확률 분포, AIC 적합, 가설 검정 기각역을 즉시 시뮬레이션해 보세요.*

---

## 📖 목차 (Table of Contents)
- [프로젝트 개요 (Overview)](#-프로젝트-개요-overview)
- [핵심 주요 기능 (Key Features)](#-핵심-주요-기능-key-features)
  - [1. 1초 스플래시 인트로 & 프리미엄 브랜딩](#1-1초-스플래시-인트로--프리미엄-브랜딩)
  - [2. 확률 분포 인터랙티브 시뮬레이션 (Simulation)](#2-확률-분포-인터랙티브-시뮬레이션-simulation)
  - [3. 데이터 분포 적합 & AIC/BIC 랭킹 (Distribution Fitting)](#3-데이터-분포-적합--aicbic-랭킹-distribution-fitting)
  - [4. 가설 검정 및 기각역 동적 시각화 (Hypothesis Testing)](#4-가설-검정-및-기각역-동적-시각화-hypothesis-testing)
  - [5. 통계 지식 허브 & NIST 레퍼런스 (Knowledge Hub)](#5-통계-지식-허브--nist-레퍼런스-knowledge-hub)
  - [6. 현대적인 UI/UX & 다크/라이트 테마](#6-현대적인-uiux--다크라이트-테마)
- [지원 통계 분포 목록 (Supported Distributions)](#-지원-통계-분포-목록-supported-distributions)
- [지원 통계 검정 목록 (Supported Hypothesis Tests)](#-지원-통계-검정-목록-supported-hypothesis-tests)
- [프로젝트 구조 (Repository Structure)](#-프로젝트-구조-repository-structure)
- [시작하기 (Getting Started)](#-시작하기-getting-started)
- [단일 실행 파일 빌드 방법 (Build Guide)](#-단일-실행-파일-빌드-방법-build-guide)
- [기술 스택 (Tech Stack)](#-기술-스택-tech-stack)
- [라이선스 (License)](#-라이선스-license)

---

## 🔭 프로젝트 개요 (Overview)

**AlphaSpace**는 복잡하고 추상적인 통계학 및 확률 분포 개념을 직관적인 비주얼과 인터랙티브 조작으로 학습하고 실제 데이터 분석에 적용할 수 있는 올인원(All-in-One) 통계 분석 데스크톱 플랫폼입니다.

수학교육, 데이터 사이언스, 신뢰성 공학, 품질 관리(QC), 생물통계, 금융 공학 등 다양한 도메인에서 활용할 수 있도록 **21종의 확률 분포 시뮬레이션**, **최대우도추정(MLE) 기반 데이터 적합**, **유의수준 기각역 동적 시각화 가설 검정**, **NIST 연계 수식 백과사전**을 제공합니다.

---

## ✨ 핵심 주요 기능 (Key Features)

### 1. 확률 분포 인터랙티브 시뮬레이션 (Simulation)
- **21종 연속형/이산형 분포 지원**: 모수(Parameter) 슬라이더를 실시간으로 조작하여 분포의 모양 변화를 즉시 체감
- **이중 차트 시각화**: 확률밀도함수(PDF)/확률질량함수(PMF) 및 누적분포함수(CDF) 동시 렌더링
- **구간 확률 계산기**: $P(X \le a)$, $P(a \le X \le b)$, $P(X \ge b)$의 확률을 실시간 수치 계산 및 면적 음영(Shading) 표시
- **몬테카를로 표본 추출 시뮬레이션**: 표본 크기($N$)와 시드(Seed)를 지정하여 무작위 표본을 추출하고 히스토그램과 이론적 밀도 함수를 겹쳐 대수의 법칙 및 중심극한정리 검증
- **이론적 통계량 자동 산출**: 평균($\mu$), 분산($\sigma^2$), 왜도(Skewness), 첨도(Kurtosis), 중위수(Median), 최빈값(Mode) 즉시 확인

### 2. 데이터 분포 적합 & AIC/BIC 랭킹 (Distribution Fitting)
- **다양한 데이터 로더**: CSV, Excel(`.xlsx`, `.xls`), 텍스트 파일 불러오기 및 실무 프리셋 데이터셋 제공 (부품 수명 시험, 환자 반응률, 서버 트래픽 등)
- **모형 적합도 자동 랭킹**:
  - **AIC (Akaike Information Criterion)** 및 **BIC (Bayesian Information Criterion)** 자동 계산 및 최적 모델 순위 선정
  - **로그 우도(Log-Likelihood)** 및 모수 추정치(MLE) 리포트
- **적합도 검정 (Goodness-of-fit Tests)**:
  - **콜모고로프-스미르노프(Kolmogorov-Smirnov, K-S) 검정** (연속형)
  - **카이제곱($\chi^2$) 적합도 검정** (이산형)
- **정밀 시각 진단 플롯**:
  - 실측 히스토그램 vs 적합 곡선 오버레이
  - **Q-Q 플롯 (Quantile-Quantile Plot)**
  - **P-P 플롯 (Probability-Probability Plot)**

### 3. 가설 검정 및 기각역 동적 시각화 (Hypothesis Testing)
- **광범위한 가설 검정 알고리즘**:
  - 모수 검정: 단일표본 t-검정, 독립 이표본 t-검정(Student & Welch), 대응표본 t-검정, 일원배치 분산분석(One-way ANOVA)
  - 비모수 검정: 맨-휘트니 U 검정(Mann-Whitney U), 윌콕슨 부호순위 검정(Wilcoxon Signed-Rank)
  - 범주형/적합성: 카이제곱 독립성 검정($\chi^2$ Test of Independence)
  - 연관성/인과성: 피어슨/스피어만 상관분석, OLS 다중/단순 선형회귀분석
- **유의수준($\alpha$) 동적 슬라이더**: 슬라이더를 움직이면 검정 통계량 분포(t, F, $\chi^2$, z) 위의 **임계치(Critical Value)**와 **기각역(Critical Region)**이 실시간으로 확장/축소되며 p-값과의 관계를 한눈에 파악
- **해석 리포트 자동 생성**: 통계적 의사결정(귀무가설 기각/채택), 신뢰구간, 비즈니스 및 연구 관점의 실질적 해석 가이드 제공

### 4. 통계 지식 허브 & NIST 레퍼런스 (Knowledge Hub)
- **내장 통계 사전**: 각 확률 분포의 수학적 정의, 수식(LaTeX 표기), 모수 의미, 실무 활용 사례, 팁 내장
- **공식 학술 레퍼런스 원클릭 연결**:
  - 미국 국립표준기술원(NIST) e-Handbook of Statistical Methods
  - SciPy 공식 통계 패키지 문서

### 5. 현대적인 UI/UX & 다크/라이트 테마
- **원클릭 테마 전환**: 시스템 기본 테마 자동 감지, 다크 모드(Dark Mode), 라이트 모드(Light Mode) 완벽 지원
- **차트 테마 동기화**: 테마 변경 시 Matplotlib 차트의 배경, 축 레이블, 눈금선, 범례 색상이 실시간으로 자연스럽게 전환
- **작업 표시줄 아이콘 매핑**: Windows 전용 고해상도 앱 아이콘 및 독립 프로세스 AppUserModelID 적용

---

## 📊 지원 통계 분포 목록 (Supported Distributions)

| 구분 | 분포명 | 파라미터 (Parameters) | 주요 적용 분야 |
| :--- | :--- | :--- | :--- |
| **연속형 (15종)** | **정규분포 (Normal)** | $\mu$ (평균), $\sigma$ (표준편차) | 자연현상, 시험 성적, 측정 오차 |
| | **로그정규분포 (Lognormal)** | $\mu_{\log}$, $\sigma_{\log}$ | 소득 분포, 주가 변동, 입자 크기 |
| | **t-분포 (Student's t)** | $\nu$ (자유도), $\mu$, $\sigma$ | 소표본 평균 검정, 금융 시계열 |
| | **카이제곱분포 (Chi-squared)** | $k$ (자유도) | 분산 검정, 적합도/독립성 검정 |
| | **F-분포 (Fisher-Snedecor)** | $d_1, d_2$ (자유도) | ANOVA 분산분석, 회귀모형 유의성 |
| | **지수분포 (Exponential)** | $\lambda$ (발생률) | 대기시간, 고장 간격, 방사성 붕괴 |
| | **감마분포 (Gamma)** | $\alpha$ (형태), $\beta$ (척도) | 누적 사건 대기시간, 강우량 모델링 |
| | **와이불분포 (Weibull)** | $k$ (형태), $\lambda$ (척도) | 부품 신뢰성 공학, 재료 수명 예측 |
| | **균일분포 (Uniform)** | $a$ (최소), $b$ (최대) | 난수 생성, 계측기 균등 양자화 오차 |
| | **베타분포 (Beta)** | $\alpha, \beta$ (형태 모수) | 베이지안 사전/사후확률, 프로젝트 일정 관리(PERT) |
| | **코시분포 (Cauchy)** | $x_0$ (위치), $\gamma$ (척도) | 분광학 스펙트럼 폭, 헤비 테일 모델링 |
| | **라플라스분포 (Laplace)** | $\mu$ (위치), $b$ (척도) | 신호 처리, 금융 급변동 모델링 |
| | **로지스틱분포 (Logistic)** | $\mu$ (위치), $s$ (척도) | 로지스틱 회귀, 개체수 성장 모델 |
| | **파레토분포 (Pareto)** | $\alpha$ (형태), $x_m$ (척도) | 80/20 법칙, 부의 분배, 극단값 통계 |
| | **레일리분포 (Rayleigh)** | $\sigma$ (척도) | 풍속 모델링, 무선 통신 다중경로 페이딩 |
| **이산형 (6종)** | **이항분포 (Binomial)** | $n$ (시행수), $p$ (성공확률) | 품질 검사(불량품수), 동전 던지기 |
| | **포아송분포 (Poisson)** | $\lambda$ (평균 발생률) | 단위시간당 서버 트래픽, 콜센터 인입수 |
| | **기하분포 (Geometric)** | $p$ (성공확률) | 첫 번째 성공까지의 시도 횟수 |
| | **초기하분포 (Hypergeometric)** | $N$ (모집단), $K$ (성공수), $n$ (추출수) | 비복원 추출, 로또 복권, 카드 패 분석 |
| | **음이항분포 (Negative Binomial)** | $r$ (목표성공수), $p$ (성공확률) | $r$번 성공할 때까지의 실패 횟수 |
| | **이산균일분포 (Discrete Uniform)** | $a$ (최소정수), $b$ (최대정수) | 주사위 던지기, 무작위 표본 추출 |

---

## ⚖️ 지원 통계 검정 목록 (Supported Hypothesis Tests)

| 검정 분류 | 검정 방법 | 검정 통계량 | 귀무가설 ($H_0$) 및 용도 |
| :--- | :--- | :--- | :--- |
| **단일 표본** | One-sample t-test | $t$ 통계량 | 모집단 평균이 기준값 $\mu_0$와 같은지 검정 |
| **이표본 검정** | Two-sample t-test (독립표본) | $t$ (Student/Welch) | 두 독립 집단의 평균 차이 검정 (A/B 테스트) |
| | Paired t-test (대응표본) | $t$ 통계량 | 사전-사후 처치 효과 비교 (동일 대상 반복 측정) |
| **분산 분석** | One-way ANOVA | $F$ 통계량 | 3개 이상 다중 그룹 간의 평균 차이 유의성 검정 |
| **범주형 검정** | $\chi^2$ 독립성 검정 | $\chi^2$ 통계량 | 두 범주형 변수 간의 연관성/독립성 검정 |
| **비모수 검정** | Mann-Whitney U 검정 | $U$ 통계량 | 정규성을 만족하지 않는 두 독립 표본의 중위수 비교 |
| | Wilcoxon 부호순위 검정 | $W$ 통계량 | 정규성을 만족하지 않는 대응 표본 비교 |
| **상관 및 회귀** | 피어슨/스피어만 상관분석 | $r, \rho$ | 두 연속형 변수 간의 선형/단조 연관성 분석 |
| | OLS 선형회귀분석 | $t, F, R^2$ | 독립변수와 종속변수 간의 인과 및 예측 모델링 |

---

## 📂 프로젝트 구조 (Repository Structure)

```plaintext
AlphaSpace/
│
├── main.py                   # 메인 윈도우 UI, 1초 스플래시 인트로, 테마 엔진 및 진입점
├── simulation_tab.py         # 탭 1: 확률 분포 인터랙티브 시뮬레이션 및 분위수 계산기
├── fitting_tab.py            # 탭 2: 데이터 분포 피팅, AIC/BIC 랭킹, 5종 진단 플롯
├── hypothesis_tab.py         # 탭 3: 가설 검정 및 동적 기각역 시각화 리포트
├── core_distributions.py     # 21종 확률 분포 모수 맵핑 및 이론 통계량 엔진
├── knowledge_base.py         # 통계 수식 사전 데이터 및 KnowledgeHub 다이얼로그
├── utils.py                  # Matplotlib 폰트 설정 및 한글 폰트(맑은 고딕 등) 호환 유틸리티
├── create_icon.py            # 멀티 해상도 아이콘 생성 및 리소스 검증 스크립트
│
├── splash.png                # 1초 스플래시 스크린 브랜딩 이미지 (Alpha Space Data Analytics)
├── app_icon.ico              # Windows 애플리케이션 멀티 해상도(16~256px) 실행 아이콘
├── app_icon.png              # UI 및 다이얼로그용 리소스 아이콘 (512x512)
│
├── docs/                     # GitHub Pages 공식 인터랙티브 웹 사용자 매뉴얼
│   ├── index.html            # 웹 매뉴얼 및 인터랙티브 웹 시뮬레이터 (Live Simulator)
│   ├── style.css             # 글래스모피즘 & 다크/라이트 테마 웹 스타일시트
│   ├── app.js                # 웹 캔버스 차트 렌더링 및 통계 계산 엔진
│   └── assets/               # 웹 매뉴얼 이미지 및 실제 프로그램 구동 스크린샷
│
├── requirements.txt          # Python 의존성 패키지 명세
├── AlphaSpace.spec           # PyInstaller 단일 독립 실행 파일(Onefile) 빌드 스펙
├── build.bat                 # 원클릭 단일 실행 파일 자동 빌드 배치 파일
└── README.md                 # 프로젝트 기술 문서
```

---

## 🚀 시작하기 (Getting Started)

### 방법 1: 무설치 단일 실행 파일 (Recommended)
파이썬 환경이 설치되어 있지 않은 Windows PC에서도 즉시 실행 가능합니다.

1. GitHub의 [Releases](../../releases) 페이지에서 최신 **`AlphaSpace.exe`** 파일을 다운로드합니다.
2. 다운로드한 `AlphaSpace.exe`를 더블 클릭하여 즉시 실행합니다. (무설치 포터블)

### 방법 2: 소스 코드 직접 실행 (Python 개발 환경)

Python 3.10 이상이 설치된 환경에서 다음 명령어로 프로젝트를 구동할 수 있습니다.

```bash
# 1. 저장소 클론
git clone https://github.com/your-username/AlphaSpace.git
cd AlphaSpace

# 2. 가상환경 생성 및 활성화
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Windows CMD:
.venv\Scripts\activate.bat

# 3. 필수 라이브러리 설치
pip install -r requirements.txt

# 4. 애플리케이션 실행
python main.py
```

---

## 🔨 단일 실행 파일 빌드 방법 (Build Guide)

직접 독립 실행 파일(`.exe`)을 패키징하려면 포함된 자동 빌드 스크립트를 사용합니다.

```cmd
# Windows CMD / PowerShell에서 빌드 스크립트 실행
build.bat
```

또는 PyInstaller 명령어를 직접 실행할 수 있습니다:

```bash
python -m PyInstaller --noconfirm --clean AlphaSpace.spec
```

빌드가 완료되면 **`dist\AlphaSpace.exe`** 경로에 약 130MB 크기의 **완전 독립형 단일 실행 파일**이 생성됩니다.

> [!TIP]
> `AlphaSpace.spec`에는 필수 데이터(아이콘 및 statsmodels 모듈)가 포함되어 있으며, 불필요한 대용량 Qt 모듈(QtWebEngine, Qt3D, QtQuick 등 약 150MB+)이 자동 배제되어 최적의 크기와 빠른 기동 속도를 제공합니다.

---

## 🛠 기술 스택 (Tech Stack)

- **언어 (Language)**: Python 3.11
- **GUI 프레임워크**: [PySide6 (Qt for Python 6)](https://wiki.qt.io/Qt_for_Python)
- **과학 계산 & 통계 엔진**:
  - [SciPy](https://scipy.org/) (`scipy.stats`, `scipy.optimize`)
  - [NumPy](https://numpy.org/) (수치 배열 연산 및 몬테카를로 난수 생성)
  - [Statsmodels](https://www.statsmodels.org/) (OLS 회귀분석 및 시계열/추론 통계)
- **데이터 핸들링**: [Pandas](https://pandas.pydata.org/), [OpenPyXL](https://openpyxl.readthedocs.io/)
- **데이터 시각화**: [Matplotlib](https://matplotlib.org/) (`backend_qtagg` 인터랙티브 캔버스)
- **배포 & 패키징**: [PyInstaller](https://pyinstaller.org/) (Standalone Onefile Executable)

---

## 📄 라이선스 (License)

이 프로젝트는 [MIT License](LICENSE)에 따라 자유롭게 사용, 수정 및 배포할 수 있습니다.
자세한 내용은 저장소의 LICENSE 파일을 참조하십시오.

---

<p align="center">
  <b>AlphaSpace</b>와 함께 통계학의 세계를 직관적이고 인터랙티브하게 탐험해 보세요! 🚀
</p>
