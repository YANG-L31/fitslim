import os

os.environ.setdefault('KIVY_NO_ARGS', '1')

from kivy.config import Config
from kivy.utils import platform

if platform not in ('android', 'ios'):
    Config.set('graphics', 'width', '400')
    Config.set('graphics', 'height', '840')
    Config.set('graphics', 'resizable', '1')
    Config.set('graphics', 'minimum_width', '360')
    Config.set('graphics', 'minimum_height', '640')

from kivy.app import App
from kivy.core.window import Window

from app.fonts import register_fonts
from app.theme import C
from app.models import Store
from app.screens import Root


class FitSlimApp(App):
    name = 'FitSlim'
    title = '轻食记 · FitSlim'

    def build(self):
        register_fonts()
        Window.clearcolor = C.BG
        path = os.path.join(self.user_data_dir, 'fitslim_data.json')
        self.store = Store(path)
        return Root(self.store)


if __name__ == '__main__':
    FitSlimApp().run()
