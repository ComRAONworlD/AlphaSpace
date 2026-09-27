import os
import platform
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm

# Matplotlib Backend 안전 설정 (최초 1회만 설정)
try:
    if matplotlib.get_backend().lower() != 'qtagg':
        matplotlib.use('QtAgg')
except Exception:
    pass

_FONT_INITIALIZED = False

def setup_matplotlib(is_dark=False):
    global _FONT_INITIALIZED
    
    # 운영체제별 안정적인 한글 폰트 적용 (리스트 순서대로 Fallback)
    if not _FONT_INITIALIZED and platform.system() == 'Windows':
        font_path = 'C:/Windows/Fonts/malgun.ttf'
        if os.path.exists(font_path):
            try:
                font_entry = fm.FontEntry(fname=font_path, name='Malgun Gothic')
                fm.fontManager.ttflist.insert(0, font_entry)
            except Exception:
                pass
        _FONT_INITIALIZED = True

    if platform.system() == 'Windows':
        font_family = ['Malgun Gothic', '맑은 고딕', 'NanumGothic', 'Gulim', 'Segoe UI']
    elif platform.system() == 'Darwin':
        font_family = ['AppleGothic', 'NanumGothic', 'Helvetica Neue']
    else:
        font_family = ['NanumGothic', 'Noto Sans CJK KR', 'UnDotum', 'DejaVu Sans']

    # 1. 테마 적용
    if is_dark:
        plt.style.use('dark_background')
        bg_color = '#2b2b2b'
        fg_color = '#E0E0E0'
        grid_color = '#444444'
        cycle_colors = ['#82AAFF', '#C3E88D', '#F07178', '#C792EA', '#FFCB6B', '#F78C6C', '#89DDFF', '#B2CCD6']
    else:
        try:
            plt.style.use('seaborn-v0_8-whitegrid')
        except Exception:
            try:
                plt.style.use('seaborn-whitegrid')
            except Exception:
                pass
        bg_color = '#ffffff'
        fg_color = '#333333'
        grid_color = '#EAEAEA'
        cycle_colors = ['#0d6efd', '#198754', '#dc3545', '#6f42c1', '#fd7e14', '#20c997', '#d63384', '#0dcaf0']

    # 2. 폰트 및 마이너스 부호 설정 재적용
    matplotlib.rcParams['font.family'] = 'sans-serif'
    current_sans = matplotlib.rcParams.get('font.sans-serif', [])
    matplotlib.rcParams['font.sans-serif'] = font_family + [f for f in current_sans if f not in font_family]
    matplotlib.rcParams['axes.unicode_minus'] = False

    # 3. 고품질 차트 스타일 세팅
    matplotlib.rcParams.update({
        'axes.spines.top': False,
        'axes.spines.right': False,
        'axes.edgecolor': grid_color,
        'axes.titleweight': 'bold',
        'axes.titlesize': 11,
        'axes.labelsize': 9.5,
        'axes.labelcolor': fg_color,
        'text.color': fg_color,
        'xtick.color': fg_color,
        'ytick.color': fg_color,
        'grid.color': grid_color,
        'grid.linestyle': '--',
        'grid.alpha': 0.6,
        'figure.facecolor': bg_color,
        'axes.facecolor': bg_color,
        'figure.autolayout': True,
        'axes.prop_cycle': matplotlib.cycler(color=cycle_colors)
    })
