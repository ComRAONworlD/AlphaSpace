# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# 필수 데이터 파일 수집
datas = [
    ('app_icon.ico', '.'),
    ('app_icon.png', '.'),
]
datas += collect_data_files('statsmodels')
datas += collect_data_files('patsy')

# 필수 숨은 임포트 수집
hiddenimports = [
    'pandas',
    'openpyxl',
    'statsmodels',
    'statsmodels.api',
    'statsmodels.tsa.api',
    'statsmodels.formula.api',
    'scipy.stats',
    'scipy.special',
    'scipy.optimize',
    'matplotlib',
    'matplotlib.backends.backend_qtagg',
    'patsy',
    'patsy.builtins',
]
hiddenimports += collect_submodules('statsmodels')

# 불필요한 대용량 모듈 배제 (용량 다이어트 & 빌드 속도 향상)
excludes = [
    # GUI 대용량 미사용 라이브러리
    'tkinter',
    'PyQt5',
    'PyQt6',
    # PySide6 내부 미사용 3D / Web / Qml / Quick 모듈 (약 150MB+ 절약)
    'PySide6.QtQuick',
    'PySide6.QtQml',
    'PySide6.Qt3DCore',
    'PySide6.Qt3DRender',
    'PySide6.Qt3DInput',
    'PySide6.Qt3DLogic',
    'PySide6.Qt3DAnimation',
    'PySide6.Qt3DExtras',
    'PySide6.QtNetworkAuth',
    'PySide6.QtVirtualKeyboard',
    'PySide6.QtBluetooth',
    'PySide6.QtNfc',
    'PySide6.QtPositioning',
    'PySide6.QtSensors',
    'PySide6.QtSerialPort',
    'PySide6.QtWebEngineCore',
    'PySide6.QtWebEngineWidgets',
    'PySide6.QtWebEngineQuick',
    'PySide6.QtPdf',
    'PySide6.QtPdfWidgets',
    'PySide6.QtDesigner',
    'PySide6.QtHelp',
    'PySide6.QtTest',
    # 개발 및 인터랙티브 전용 도구 (unittest, pydoc, sqlite3 등 런타임 필수 모듈 제외 금지)
    'IPython',
    'ipykernel',
    'jupyter',
    'notebook',
    'pytest',
    'pylint',
    'jedi',
]

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=excludes,
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
    optimize=1,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# 단일 독립 실행 파일(Onefile) 모드 구성
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='AlphaSpace',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='app_icon.ico',
)
