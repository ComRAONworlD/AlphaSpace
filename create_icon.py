"""
AlphaSpace Icon & Splash Asset Generator / Validator
"""
import os
from PIL import Image

def create_app_icon():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    icon_png = os.path.join(base_dir, 'app_icon.png')
    icon_ico = os.path.join(base_dir, 'app_icon.ico')
    
    if os.path.exists(icon_png):
        img = Image.open(icon_png).convert('RGBA')
        sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
        img.save(icon_ico, format='ICO', sizes=sizes)
        print(f"Successfully generated {icon_ico} from {icon_png}")
    else:
        print(f"Warning: {icon_png} not found.")

if __name__ == '__main__':
    create_app_icon()
