import os
import platform
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

def setup_matplotlib(is_dark=False):
    # 운영체제별 안정적인 한글 폰트 적용 (리스트 순서대로 Fallback)
    if platform.system() == 'Windows':
        # Matplotlib 캐시에 맑은 고딕이 누락되는 현상을 방지하기 위해 폰트 강제 주입
        font_path = 'C:/Windows/Fonts/malgun.ttf'
        if os.path.exists(font_path):
            try:
                # addfont 대신 명시적인 등록을 위해 ttflist 맨 앞에 삽입
                font_entry = fm.FontEntry(fname=font_path, name='Malgun Gothic')
                fm.fontManager.ttflist.insert(0, font_entry)
            except Exception:
                pass
        font_family = ['Malgun Gothic', '맑은 고딕', 'NanumGothic', 'Gulim']
    elif platform.system() == 'Darwin':
        font_family = ['AppleGothic', 'NanumGothic']
    else:
        font_family = ['NanumGothic', 'Noto Sans CJK KR', 'UnDotum']

    matplotlib.use('QtAgg')

    # 1. 테마 적용 (이 때 기존 폰트 설정이 제거될 수 있음)
    if is_dark:
        plt.style.use('dark_background')
        bg_color = '#2b2b2b'
        fg_color = '#E0E0E0'
        grid_color = '#444444'
        cycle_colors = ['#82AAFF', '#C3E88D', '#F07178', '#C792EA', '#FFCB6B', '#F78C6C', '#89DDFF', '#B2CCD6']
    else:
        # 모던 데이터 시각화 스타일을 위한 seaborn 스타일 설정
        try:
            plt.style.use('seaborn-v0_8-whitegrid')
        except:
            try:
                plt.style.use('seaborn-whitegrid')
            except:
                pass # fallback
        bg_color = 'white'
        fg_color = '#333333'
        grid_color = '#EAEAEA'
        cycle_colors = ['#4C72B0', '#55A868', '#C44E52', '#8172B3', '#937860', '#DA8BC3', '#8C8C8C', '#CCB974']

    # 2. 강제로 폰트 및 마이너스 부호 설정 재적용
    # Seaborn 스타일이 font.sans-serif를 Arial로 고정시키는 것을 방지
    matplotlib.rcParams['font.family'] = 'sans-serif'
    # 기존 리스트 덮어쓰기 보다는 앞에 추가하는 방식 사용
    matplotlib.rcParams['font.sans-serif'] = font_family + matplotlib.rcParams.get('font.sans-serif', [])
    matplotlib.rcParams['axes.unicode_minus'] = False

    # 3. 전체적인 차트 세팅 (Minitab/Tableau 느낌)
    matplotlib.rcParams.update({
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.edgecolor': grid_color,
        'axes.titleweight': 'bold',
        'axes.titlesize': 12,
        'axes.labelsize': 10,
        'axes.labelcolor': fg_color,
        'text.color': fg_color,
        'xtick.color': fg_color,
        'ytick.color': fg_color,
        'grid.color': grid_color,
        'grid.linestyle': '--',
        'grid.alpha': 0.7,
        'figure.facecolor': bg_color,
        'axes.facecolor': bg_color,
        'figure.autolayout': True,  # tight_layout 대체 효과
        'axes.prop_cycle': matplotlib.cycler(color=cycle_colors)
    })


