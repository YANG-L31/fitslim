import os
from kivy.core.text import LabelBase

FONT = 'CN'

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

_CANDIDATES = [
    os.path.join(_ROOT, 'assets', 'fonts', 'SourceHanSansCN-Regular.otf'),
    os.path.join(_ROOT, 'assets', 'fonts', 'NotoSansSC-Regular.ttf'),
    '/system/fonts/NotoSansCJK-Regular.ttc',
    '/system/fonts/NotoSansSC-Regular.otf',
    '/system/fonts/NotoSansSC-Regular.ttf',
    '/system/fonts/DroidSansFallbackFull.ttf',
    '/system/fonts/DroidSansFallback.ttf',
    r'C:\Windows\Fonts\msyh.ttc',
    r'C:\Windows\Fonts\Deng.ttf',
    r'C:\Windows\Fonts\simhei.ttf',
]


def register_fonts():
    for path in _CANDIDATES:
        if path and os.path.exists(path):
            try:
                LabelBase.register(name=FONT, fn_regular=path)
                return path
            except Exception:
                continue
    return None
