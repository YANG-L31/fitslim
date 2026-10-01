from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.uix.behaviors import ButtonBehavior
from kivy.graphics import Color, RoundedRectangle, Rectangle, Line, Ellipse
from kivy.graphics.texture import Texture
from kivy.properties import (
    ListProperty, NumericProperty, StringProperty, BooleanProperty,
)
from kivy.metrics import dp, sp
from kivy.animation import Animation
from kivy.clock import Clock

from .theme import C, PAD, GAP, RADIUS, CARD_PAD
from .fonts import FONT


# ---------------------------------------------------------------- helpers
def L(text='', fs=13, color=None, halign='left', valign='middle', fixed=True, **kw):
    # fixed=True aligns text within the widget box (needs an explicit size)
    lab = Label(
        text=text, font_name=FONT, font_size=sp(fs),
        color=color if color is not None else C.INK,
        halign=halign, valign=valign, **kw
    )
    if fixed:
        lab.bind(size=lambda s, v: setattr(s, 'text_size', v))
    return lab


_grad_cache = {}


def vgradient(top_color, bottom_color):
    key = (tuple(round(c, 3) for c in top_color), tuple(round(c, 3) for c in bottom_color))
    if key in _grad_cache:
        return _grad_cache[key]
    tex = Texture.create(size=(1, 256), colorfmt='rgba')
    buf = bytearray(4 * 256)
    for i in range(256):
        t = i / 255.0
        c = [bottom_color[k] * (1 - t) + top_color[k] * t for k in range(4)]
        for k in range(4):
            buf[i * 4 + k] = max(0, min(255, int(c[k] * 255 + 0.5)))
    tex.blit_buffer(bytes(buf), colorfmt='rgba', bufferfmt='ubyte')
    _grad_cache[key] = tex
    return tex


# ---------------------------------------------------------------- base card
class RoundedBox(FloatLayout):
    bg = ListProperty([1, 1, 1, 1])
    radius = NumericProperty(RADIUS)
    shadow = BooleanProperty(True)
    shadow_alpha = NumericProperty(0.07)
    grad_top = ListProperty([])
    grad_bottom = ListProperty([])
    border_color = ListProperty([0, 0, 0, 0])
    border_width = NumericProperty(0)

    def __init__(self, **kw):
        super().__init__(**kw)
        with self.canvas.before:
            self._sh2_col = Color(0, 0, 0, 0)
            self._sh2 = RoundedRectangle(radius=[self.radius + dp(2)])
            self._sh1_col = Color(0, 0, 0, 0)
            self._sh1 = RoundedRectangle(radius=[self.radius + dp(1)])
            self._bg_col = Color(*self.bg)
            self._bg = RoundedRectangle(radius=[self.radius])
            self._bd_col = Color(*self.border_color)
            self._bd = Line(width=self.border_width)
        self.bind(pos=self._update, size=self._update, bg=self._update,
                  radius=self._update, shadow=self._update, grad_top=self._update,
                  grad_bottom=self._update, border_color=self._update,
                  border_width=self._update)
        self._update()

    def fill(self, widget):
        self._content = widget
        self.add_widget(widget)
        self._fill_content()

    def _fill_content(self):
        c = getattr(self, '_content', None)
        if c is not None:
            c.pos = self.pos
            c.size = self.size

    def _update(self, *a):
        x, y = self.pos
        w, h = self.size
        r = self.radius
        if self.shadow:
            self._sh2_col.rgba = (0.14, 0.20, 0.30, self.shadow_alpha * 0.5)
            self._sh2.pos = (x - dp(2), y - dp(6))
            self._sh2.size = (w + dp(4), h + dp(8))
            self._sh2.radius = [r + dp(3)]
            self._sh1_col.rgba = (0.14, 0.20, 0.30, self.shadow_alpha)
            self._sh1.pos = (x - dp(1), y - dp(3))
            self._sh1.size = (w + dp(2), h + dp(4))
            self._sh1.radius = [r + dp(1)]
        else:
            self._sh2_col.rgba = (0, 0, 0, 0)
            self._sh1_col.rgba = (0, 0, 0, 0)

        if self.grad_top and self.grad_bottom:
            self._bg_col.rgba = (1, 1, 1, 1)
            self._bg.texture = vgradient(tuple(self.grad_top), tuple(self.grad_bottom))
        else:
            self._bg_col.rgba = tuple(self.bg)
            self._bg.texture = None
        self._bg.pos = (x, y)
        self._bg.size = (w, h)
        self._bg.radius = [r]

        self._bd_col.rgba = tuple(self.border_color)
        self._bd.width = max(0.0001, self.border_width)
        if self.border_width > 0:
            self._bd.rounded_rectangle = (x, y, w, h, r)
            self._bd.points = []
        else:
            self._bd.points = []
        self._fill_content()


# ---------------------------------------------------------------- icons
class Icon(Widget):
    name = StringProperty('home')
    color = ListProperty([0, 0, 0, 1])
    lw = NumericProperty(dp(2))

    def __init__(self, **kw):
        super().__init__(**kw)
        self.bind(pos=self._redraw, size=self._redraw, name=self._redraw,
                  color=self._redraw, lw=self._redraw)
        Clock.schedule_once(lambda *_: self._redraw(), 0)

    def _p(self, x, y):
        return (self.x + (x / 100.0) * self.width, self.y + (y / 100.0) * self.height)

    def _ln(self, pts, closed=False):
        p = []
        for (x, y) in pts:
            px, py = self._p(x, y)
            p += [px, py]
        Line(points=p, width=self.lw, cap='round', joint='round', close=closed)

    def _arc(self, cx, cy, r, a0, a1):
        px, py = self._p(cx, cy)
        pr = (r / 100.0) * min(self.width, self.height)
        Line(circle=(px, py, pr, a0, a1), width=self.lw, cap='round')

    def _circle(self, cx, cy, r, fill=False):
        px, py = self._p(cx, cy)
        pr = (r / 100.0) * min(self.width, self.height)
        if fill:
            from kivy.graphics import Ellipse
            Ellipse(pos=(px - pr, py - pr), size=(pr * 2, pr * 2))
        else:
            Line(circle=(px, py, pr, 0, 360), width=self.lw)

    def _redraw(self, *a):
        self.canvas.clear()
        if self.width <= 1 or self.height <= 1:
            return
        with self.canvas:
            Color(*self.color)
            n = self.name
            if n == 'home':
                self._ln([(14, 60), (50, 86), (86, 60)])
                self._ln([(22, 60), (22, 22), (78, 22), (78, 60)])
                self._ln([(41, 22), (41, 45), (59, 45), (59, 22)])
            elif n in ('chart', 'bars'):
                self._ln([(14, 86), (14, 14), (86, 14)])
                self._ln([(38, 14), (38, 50)])
                self._ln([(54, 14), (54, 74)])
                self._ln([(70, 14), (70, 34)])
            elif n == 'user':
                self._circle(50, 66, 14)
                self._arc(50, 16, 26, 28, 152)
            elif n == 'plus':
                self._ln([(50, 26), (50, 74)])
                self._ln([(26, 50), (74, 50)])
            elif n == 'flame':
                self._ln([(50, 90), (62, 70), (56, 60), (70, 46),
                          (62, 26), (50, 16), (38, 26), (30, 46),
                          (44, 60), (38, 70)], closed=True)
            elif n == 'drop':
                self._ln([(50, 90), (30, 45)])
                self._ln([(50, 90), (70, 45)])
                self._arc(50, 38, 24, 42, 318)
            elif n in ('run', 'activity'):
                self._ln([(8, 50), (30, 50), (40, 80), (58, 20),
                          (68, 50), (92, 50)])
            elif n == 'trend':
                self._ln([(12, 72), (42, 44), (58, 58), (88, 26)])
                self._ln([(88, 26), (74, 26)])
                self._ln([(88, 26), (88, 40)])
            elif n == 'scale':
                self._ln([(50, 90), (50, 14)])
                self._ln([(36, 14), (64, 14)])
                self._ln([(16, 74), (84, 74)])
                self._ln([(16, 74), (16, 66)])
                self._ln([(84, 74), (84, 66)])
                self._ln([(4, 66), (28, 66), (16, 48)], closed=True)
                self._ln([(72, 66), (96, 66), (84, 48)], closed=True)
            elif n == 'bell':
                self._arc(50, 56, 22, 0, 180)
                self._ln([(28, 56), (28, 36)])
                self._ln([(72, 56), (72, 36)])
                self._ln([(22, 36), (78, 36)])
                self._arc(50, 36, 8, 180, 360)
            elif n == 'target':
                self._circle(50, 50, 30)
                self._circle(50, 50, 18)
                self._circle(50, 50, 6, fill=True)
            elif n == 'chevron':
                self._ln([(42, 30), (60, 50), (42, 70)])
            elif n == 'heart':
                self._arc(38, 58, 13, 0, 180)
                self._arc(62, 58, 13, 0, 180)
                self._ln([(25, 58), (50, 24), (75, 58)])
            elif n == 'camera':
                self._bd_round(18, 26, 64, 46, 12)
                self._circle(50, 49, 13)
                self._ln([(36, 72), (44, 80), (56, 80), (64, 72)])
            elif n == 'edit':
                self._ln([(26, 74), (26, 26), (74, 26)])
                self._ln([(40, 60), (72, 28)])

    def _bd_round(self, x, y, w, h, r):
        px, py = self._p(x, y)
        pw = (w / 100.0) * self.width
        ph = (h / 100.0) * self.height
        rr = (r / 100.0) * min(self.width, self.height)
        Line(rounded_rectangle=(px, py, pw, ph, rr), width=self.lw)


# ---------------------------------------------------------------- progress ring
class ProgressRing(FloatLayout):
    progress = NumericProperty(0.0)
    thickness = NumericProperty(dp(13))
    track_color = ListProperty(list(C.TRACK))
    ring_color = ListProperty(list(C.GREEN))
    start_angle = NumericProperty(90)

    def __init__(self, **kw):
        super().__init__(**kw)
        with self.canvas:
            self._tc = Color(*self.track_color)
            self._track = Line(width=self.thickness, cap='round')
            self._rc = Color(*self.ring_color)
            self._ring = Line(width=self.thickness, cap='round')
        self.bind(pos=self._update, size=self._update, progress=self._update,
                  thickness=self._update, track_color=self._update,
                  ring_color=self._update)
        self._update()

    def _update(self, *a):
        cx, cy = self.center
        r = min(self.width, self.height) / 2.0 - self.thickness / 2.0 - dp(2)
        self._tc.rgba = tuple(self.track_color)
        self._rc.rgba = tuple(self.ring_color)
        self._track.width = self.thickness
        self._ring.width = self.thickness
        self._track.circle = (cx, cy, r, 0, 360)
        ang = max(0.0, min(1.0, self.progress)) * 360.0
        if ang <= 0.6:
            self._ring.points = []
        else:
            self._ring.circle = (cx, cy, r, self.start_angle, self.start_angle - ang)


# ---------------------------------------------------------------- macro bar
class MacroBar(FloatLayout):
    label = StringProperty('')
    value_text = StringProperty('')
    progress = NumericProperty(0.0)
    bar_color = ListProperty([1, 1, 1, 0.95])
    track_color = ListProperty([1, 1, 1, 0.25])
    text_color = ListProperty([1, 1, 1, 0.9])

    def __init__(self, **kw):
        super().__init__(**kw)
        self._lab = L(self.label, fs=11, color=self.text_color, fixed=True,
                      size_hint=(None, None), size=(dp(34), sp(15)))
        self._val = L(self.value_text, fs=10.5, color=self.text_color,
                      halign='right', fixed=True,
                      size_hint=(1, None), height=sp(15))
        self.add_widget(self._lab)
        self.add_widget(self._val)
        self._lab.pos_hint = {'x': 0, 'top': 1}
        self._val.pos_hint = {'right': 1, 'top': 1}
        self.bind(label=lambda s, v: setattr(self._lab, 'text', v),
                  value_text=lambda s, v: setattr(self._val, 'text', v))
        with self.canvas.before:
            self._tcol = Color(*self.track_color)
            self._trk = RoundedRectangle(radius=[dp(3)])
            self._fcol = Color(*self.bar_color)
            self._fil = RoundedRectangle(radius=[dp(3)])
        self.bind(pos=self._upd, size=self._upd, progress=self._upd)
        self._upd()

    def _upd(self, *a):
        x, y, w, h = self.x, self.y, self.width, self.height
        bh = dp(5)
        by = y
        self._tcol.rgba = tuple(self.track_color)
        self._fcol.rgba = tuple(self.bar_color)
        self._trk.pos = (x, by)
        self._trk.size = (w, bh)
        self._trk.radius = [bh / 2.0]
        fw = max(bh, w * max(0.0, min(1.0, self.progress)))
        self._fil.pos = (x, by)
        self._fil.size = (fw, bh)
        self._fil.radius = [bh / 2.0]


# ---------------------------------------------------------------- stat card
class StatCard(RoundedBox):
    icon = StringProperty('flame')
    value = StringProperty('0')
    unit = StringProperty('')
    name = StringProperty('')

    def __init__(self, **kw):
        kw.setdefault('bg', list(C.CARD))
        kw.setdefault('radius', RADIUS)
        super().__init__(**kw)
        self._chip = RoundedBox(size_hint=(None, None), size=(dp(34), dp(34)),
                                radius=dp(12), bg=list(C.MINT), shadow=False)
        self._icon = Icon(name=self.icon, color=list(C.GREEN), lw=dp(2),
                          size_hint=(0.58, 0.58),
                          pos_hint={'center_x': 0.5, 'center_y': 0.5})
        self._chip.add_widget(self._icon)

        self._name = L(self.name, fs=12, color=C.MUTED, fixed=True,
                       size_hint=(None, None), size=(dp(96), dp(17)),
                       halign='left', valign='middle')
        self._val = L(self.value, fs=19, color=C.INK, fixed=True,
                      size_hint=(None, None), size=(dp(50), dp(26)),
                      halign='left', valign='middle')
        self._unit = L(self.unit, fs=10.5, color=C.MUTED, fixed=True,
                       size_hint=(None, None), size=(dp(30), dp(18)),
                       halign='left', valign='middle')

        for w in (self._chip, self._name, self._val, self._unit):
            self.add_widget(w)
        self.bind(pos=self._layout, size=self._layout,
                  value=self._set_val, unit=self._set_unit, name=self._set_name)
        self._layout()

    def _set_val(self, s, v):
        self._val.text = v

    def _set_unit(self, s, v):
        self._unit.text = v

    def _set_name(self, s, v):
        self._name.text = v

    def _layout(self, *a):
        pad = CARD_PAD
        self._chip.pos = (self.x + pad, self.y + self.height - pad - self._chip.height)
        self._name.pos = (self.x + pad, self.y + pad)
        self._val.pos = (self.x + pad, self.y + pad + dp(21))
        self._unit.pos = (self.x + pad + dp(48), self._val.y + dp(4))


# ---------------------------------------------------------------- goal row
class GoalRow(FloatLayout):
    name = StringProperty('')
    value_text = StringProperty('')
    progress = NumericProperty(0.0)
    bar_color = ListProperty(list(C.GREEN))
    icon = StringProperty('')

    def __init__(self, **kw):
        super().__init__(**kw)
        with self.canvas.before:
            self._tcol = Color(*C.TRACK)
            self._trk = RoundedRectangle(radius=[dp(4)])
            self._fcol = Color(*self.bar_color)
            self._fil = RoundedRectangle(radius=[dp(4)])
        self._name = L(self.name, fs=12.5, color=C.INK2, fixed=True,
                       size_hint=(1, None), height=sp(18))
        self._val = L(self.value_text, fs=12, color=C.MUTED,
                      halign='right', fixed=True,
                      size_hint=(None, None), size=(dp(150), sp(18)))
        self.add_widget(self._name)
        self.add_widget(self._val)
        self._name.pos_hint = {'x': 0, 'top': 1}
        self._val.pos_hint = {'right': 1, 'top': 1}
        self.bind(name=lambda s, v: setattr(self._name, 'text', v),
                  value_text=lambda s, v: setattr(self._val, 'text', v))
        self.bind(pos=self._upd, size=self._upd, progress=self._upd,
                  bar_color=self._upd)
        self._upd()

    def _upd(self, *a):
        x, y, w = self.x, self.y, self.width
        bh = dp(7)
        self._tcol.rgba = tuple(C.TRACK)
        self._fcol.rgba = tuple(self.bar_color)
        self._trk.pos = (x, y)
        self._trk.size = (w, bh)
        self._trk.radius = [bh / 2.0]
        fw = max(bh, w * max(0.0, min(1.0, self.progress)))
        self._fil.pos = (x, y)
        self._fil.size = (fw, bh)
        self._fil.radius = [bh / 2.0]


# ---------------------------------------------------------------- nav
class NavItem(ButtonBehavior, FloatLayout):
    icon = StringProperty('home')
    label = StringProperty('')
    active = BooleanProperty(False)

    def __init__(self, **kw):
        super().__init__(**kw)
        with self.canvas.before:
            self._pill_col = Color(0, 0, 0, 0)
            self._pill = RoundedRectangle(radius=[dp(14)])
        self._icon = Icon(name=self.icon, color=C.MUTED, lw=dp(2.0),
                          size_hint=(None, None), size=(dp(23), dp(23)))
        self._lab = L(self.label, fs=10.5, color=C.MUTED, halign='center',
                      fixed=True, size_hint=(None, None), size=(dp(64), dp(14)))
        self.add_widget(self._icon)
        self.add_widget(self._lab)
        self.bind(pos=self._layout, size=self._layout, active=self._layout)
        self._layout()

    def _layout(self, *a):
        if self.active:
            self._pill_col.rgba = tuple(C.MINT)
            self._icon.color = list(C.GREEN)
            self._lab.color = list(C.GREEN_D)
        else:
            self._pill_col.rgba = (0, 0, 0, 0)
            self._icon.color = list(C.MUTED)
            self._lab.color = list(C.MUTED)
        cx = self.center_x
        self._pill.pos = (cx - dp(24), self.top - dp(38))
        self._pill.size = (dp(48), dp(30))
        self._icon.center_x = cx
        self._icon.top = self.top - dp(10)
        self._lab.center_x = cx
        self._lab.top = self._icon.y - dp(3)

    def on_release(self):
        if self.parent and hasattr(self.parent, 'on_select'):
            self.parent.on_select(self)


class NavBar(RoundedBox):
    def __init__(self, **kw):
        kw.setdefault('bg', list(C.CARD))
        kw.setdefault('radius', dp(0))
        kw.setdefault('shadow', True)
        super().__init__(**kw)
        self._items = {}
        for key, label, icon in [('home', '首页', 'home'),
                                 ('record', '记录', 'plus'),
                                 ('stats', '趋势', 'chart'),
                                 ('profile', '我的', 'user')]:
            it = NavItem(icon=icon, label=label, size_hint=(None, None),
                         size=(dp(64), dp(56)))
            it.key = key
            self._items[key] = it
            self.add_widget(it)
        self.bind(pos=self._layout, size=self._layout)

    def _layout(self, *a):
        n = len(self._items)
        w = self.width / n
        for i, it in enumerate(self._items.values()):
            it.size = (w, dp(56))
            it.pos = (self.x + i * w, self.y + dp(9))

    def set_active(self, key):
        for k, it in self._items.items():
            it.active = (k == key)

    def on_select(self, item):
        if hasattr(self, 'callback') and self.callback:
            self.callback(item.key)


# ---------------------------------------------------------------- segmented
class SegItem(ButtonBehavior, Label):
    def __init__(self, **kw):
        kw.setdefault('font_name', FONT)
        kw.setdefault('halign', 'center')
        kw.setdefault('valign', 'middle')
        kw.setdefault('size_hint', (None, None))
        super().__init__(**kw)
        self.bind(size=lambda s, v: setattr(s, 'text_size', v))

    def on_release(self):
        if hasattr(self.parent, 'select'):
            self.parent.select(self.index)


class Segmented(FloatLayout):
    options = ListProperty([])
    index = NumericProperty(0)

    def __init__(self, options=None, callback=None, **kw):
        kw.setdefault('size_hint_y', None)
        kw.setdefault('height', dp(46))
        super().__init__(**kw)
        self.callback = callback
        self.options = options or []
        self._items = []
        with self.canvas.before:
            self._track_col = Color(*C.TRACK)
            self._track = RoundedRectangle(radius=[dp(15)])
            self._pill_col = Color(*C.WHITE)
            self._pill = RoundedRectangle(radius=[dp(13)])
        self._build()
        self.bind(pos=self._layout, size=self._layout, index=self._layout)
        self._layout()

    def _build(self):
        for w in self._items:
            self.remove_widget(w)
        self._items = []
        for i, opt in enumerate(self.options):
            it = SegItem(text=opt, font_size=sp(13), color=list(C.MUTED))
            it.index = i
            self._items.append(it)
            self.add_widget(it)
        if self.options:
            self.select(min(self.index, len(self.options) - 1), fire=False)

    def select(self, i, fire=True):
        self.index = i
        for k, it in enumerate(self._items):
            it.color = list(C.INK) if k == i else list(C.MUTED)
        self._layout()
        if fire and self.callback:
            self.callback(i)

    def _layout(self, *a):
        if not self._items:
            return
        self._track_col.rgba = tuple(C.TRACK)
        self._track.pos = (self.x, self.y)
        self._track.size = (self.width, self.height)
        n = len(self._items)
        w = (self.width - dp(8)) / n
        for k, it in enumerate(self._items):
            it.pos = (self.x + dp(4) + k * w, self.y + dp(4))
            it.size = (w, self.height - dp(8))
        sel = self._items[max(0, min(self.index, n - 1))]
        self._pill_col.rgba = tuple(C.WHITE)
        self._pill.pos = sel.pos
        self._pill.size = sel.size


# ---------------------------------------------------------------- tap button
class TapButton(ButtonBehavior, FloatLayout):
    def __init__(self, text='', bg=None, fg=None, radius=None, fs=15, **kw):
        super().__init__(**kw)
        self._bg = list(bg) if bg else list(C.MINT)
        self._fg = list(fg) if fg else list(C.GREEN_D)
        self._radius = radius if radius is not None else dp(16)
        self.callback = None
        with self.canvas.before:
            self._col = Color(*self._bg)
            self._rect = RoundedRectangle(radius=[self._radius])
        self._lab = L(text, fs=fs, color=self._fg, halign='center', fixed=True,
                      size_hint=(None, None), size=self.size)
        self.add_widget(self._lab)
        self.bind(pos=self._upd, size=self._upd)
        self._upd()

    def _upd(self, *a):
        self._col.rgba = tuple(self._bg)
        self._rect.pos = self.pos
        self._rect.size = self.size
        self._rect.radius = [self._radius]
        self._lab.pos = self.pos
        self._lab.size = self.size

    def _shift(self, d):
        return [max(0.0, c + d) if k < 3 else c for k, c in enumerate(self._bg)]

    def on_press(self):
        self._col.rgba = tuple(self._shift(-0.06))

    def on_release(self):
        self._col.rgba = tuple(self._bg)
        if self.callback:
            self.callback()


# ---------------------------------------------------------------- primary button
class PrimaryButton(ButtonBehavior, RoundedBox):
    def __init__(self, text='', **kw):
        kw.setdefault('grad_top', list(C.GREEN_L))
        kw.setdefault('grad_bottom', list(C.GREEN))
        kw.setdefault('radius', dp(18))
        kw.setdefault('size_hint_y', None)
        kw.setdefault('height', dp(52))
        super().__init__(**kw)
        self.callback = None
        self.fill(L(text, fs=16, color=C.WHITE, halign='center', fixed=True,
                    size_hint=(1, 1)))

    def on_press(self):
        self.grad_top = list(C.GREEN)
        self.grad_bottom = list(C.GREEN_D)

    def on_release(self):
        self.grad_top = list(C.GREEN_L)
        self.grad_bottom = list(C.GREEN)
        if self.callback:
            self.callback()


# ---------------------------------------------------------------- text field
class TextField(RoundedBox):
    def __init__(self, hint='', input_filter='text', **kw):
        kw.setdefault('bg', list(C.WHITE))
        kw.setdefault('radius', dp(16))
        kw.setdefault('shadow', False)
        kw.setdefault('border_width', dp(1.4))
        kw.setdefault('border_color', list(C.LINE))
        kw.setdefault('size_hint_y', None)
        kw.setdefault('height', dp(50))
        super().__init__(**kw)
        self.ti = TextInput(
            multiline=False, hint_text=hint, input_filter=input_filter,
            font_name=FONT, font_size=sp(14.5), background_color=(0, 0, 0, 0),
            foreground_color=list(C.INK), cursor_color=list(C.GREEN),
            hint_text_color=list(C.MUTED), padding=[dp(14), dp(12)],
            write_tab=False)
        self.ti.bind(focus=self._focus)
        self.fill(self.ti)

    def _focus(self, inst, val):
        self.border_color = list(C.GREEN) if val else list(C.LINE)

    @property
    def text(self):
        return self.ti.text

    @text.setter
    def text(self, v):
        self.ti.text = v


# ---------------------------------------------------------------- stepper
class Stepper(FloatLayout):
    name = StringProperty('')
    value = NumericProperty(0)
    step = NumericProperty(1)
    minimum = NumericProperty(0)
    maximum = NumericProperty(100000)
    unit = StringProperty('')
    fmt = StringProperty('{:.0f}')

    def __init__(self, name='', value=0, step=1, unit='', minimum=0,
                 maximum=100000, fmt='{:.0f}', callback=None, **kw):
        kw.setdefault('size_hint_y', None)
        kw.setdefault('height', dp(48))
        super().__init__(**kw)
        self.name = name
        self.value = value
        self.step = step
        self.unit = unit
        self.minimum = minimum
        self.maximum = maximum
        self.fmt = fmt
        self.callback = callback
        self._name = L(name, fs=13.5, color=C.INK2, fixed=True,
                       size_hint=(None, None), size=(dp(120), dp(22)))
        self._minus = TapButton('-', bg=list(C.TRACK), fg=list(C.INK2),
                                radius=dp(15), fs=18,
                                size_hint=(None, None), size=(dp(30), dp(30)))
        self._minus.callback = lambda: self._change(-self.step)
        self._plus = TapButton('+', bg=list(C.MINT), fg=list(C.GREEN_D),
                               radius=dp(15), fs=18,
                               size_hint=(None, None), size=(dp(30), dp(30)))
        self._plus.callback = lambda: self._change(self.step)
        self._val = L('', fs=15, color=C.INK, halign='center', fixed=True,
                      size_hint=(None, None), size=(dp(96), dp(24)))
        for w in (self._name, self._minus, self._val, self._plus):
            self.add_widget(w)
        self.bind(pos=self._layout, size=self._layout)
        self._update_val()
        self._layout()

    def _change(self, d):
        v = max(self.minimum, min(self.maximum, self.value + d))
        v = round(v, 2)
        if v != self.value:
            self.value = v
            self._update_val()
            if self.callback:
                self.callback(v)

    def _update_val(self):
        txt = self.fmt.format(self.value)
        if self.unit:
            txt += ' ' + self.unit
        self._val.text = txt

    def _layout(self, *a):
        cy = self.center_y
        self._name.x = self.x
        self._name.center_y = cy
        self._plus.center_x = self.x + self.width - dp(19)
        self._plus.center_y = cy
        self._val.center_x = self._plus.center_x - dp(69)
        self._val.center_y = cy
        self._minus.center_x = self._val.center_x - dp(69)
        self._minus.center_y = cy


# ---------------------------------------------------------------- list row
class ListRow(FloatLayout):
    def __init__(self, icon='', title='', subtitle='', value='', tint=None,
                 color=None, **kw):
        kw.setdefault('size_hint_y', None)
        kw.setdefault('height', dp(56))
        super().__init__(**kw)
        tint = tint or list(C.MINT)
        color = color or list(C.GREEN)
        chip = RoundedBox(size_hint=(None, None), size=(dp(38), dp(38)),
                          radius=dp(13), bg=tint, shadow=False)
        chip.add_widget(Icon(name=icon, color=color, lw=dp(1.9),
                             size_hint=(0.55, 0.55),
                             pos_hint={'center_x': 0.5, 'center_y': 0.5}))
        self.add_widget(chip)
        t = L(title, fs=13.5, color=C.INK, fixed=True,
              size_hint=(None, None), size=(dp(160), dp(18)))
        s = L(subtitle, fs=11, color=C.MUTED, fixed=True,
              size_hint=(None, None), size=(dp(160), dp(15)))
        val = L(value, fs=13, color=C.INK2, halign='right', fixed=True,
                size_hint=(None, None), size=(dp(110), dp(20)))
        self.add_widget(t)
        self.add_widget(s)
        self.add_widget(val)
        self.bind(pos=self._layout, size=self._layout)
        self._layout()

    def _layout(self, *a):
        chip = self.children[-1]
        chip.x = self.x + dp(4)
        chip.center_y = self.center_y
        Ls = self.children
        val = Ls[0]
        s = Ls[1]
        t = Ls[2]
        tx = chip.x + chip.width + dp(12)
        t.x = tx
        t.y = self.center_y + dp(1)
        s.x = tx
        s.y = self.center_y - dp(1) - s.height
        val.x = self.x + self.width - dp(4) - val.width
        val.center_y = self.center_y


# ---------------------------------------------------------------- popup
class AnnouncementPopup(FloatLayout):
    """Modal announcement shown once every time the app launches.

    message uses '；' or ';' as a line separator.
    """

    def __init__(self, title='温馨提示', message='', on_close=None, **kw):
        kw.setdefault('size_hint', (1, 1))
        super().__init__(**kw)
        self._on_close = on_close
        with self.canvas.before:
            self._dim = Color(0.09, 0.14, 0.22, 0.45)
            self._bg = Rectangle(pos=self.pos, size=self.size)
        self.bind(pos=self._upd, size=self._upd)
        self._upd()

        lines = [s.strip() for s in message.replace(';', '；').split('；') if s.strip()]
        height = dp(206) + dp(30) * len(lines)
        card = RoundedBox(bg=list(C.CARD), radius=dp(22), shadow=True,
                          size_hint=(None, None), size=(dp(300), height),
                          pos_hint={'center_x': 0.5, 'center_y': 0.5})
        v = BoxLayout(orientation='vertical', spacing=dp(8),
                      padding=[dp(22), dp(24), dp(22), dp(20)])
        card.fill(v)

        chip_row = BoxLayout(orientation='horizontal', size_hint_y=None,
                             height=dp(52))
        chip_row.add_widget(Widget())
        chip = RoundedBox(size_hint=(None, None), size=(dp(52), dp(52)),
                          radius=dp(26), bg=list(C.MINT), shadow=False)
        chip.add_widget(Icon(name='target', color=list(C.GREEN), lw=dp(2),
                             size_hint=(0.5, 0.5),
                             pos_hint={'center_x': 0.5, 'center_y': 0.5}))
        chip_row.add_widget(chip)
        chip_row.add_widget(Widget())
        v.add_widget(chip_row)

        v.add_widget(L(title, fs=16, color=C.INK, halign='center', fixed=True,
                       size_hint_y=None, height=dp(24)))
        for line in lines:
            v.add_widget(L(line, fs=14, color=C.INK2, halign='center',
                           fixed=True, size_hint_y=None, height=dp(20)))
        v.add_widget(Widget())
        btn = PrimaryButton('我知道了')
        btn.callback = self.close
        v.add_widget(btn)

        self.add_widget(card)

    def _upd(self, *a):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def close(self):
        if self.parent:
            self.parent.remove_widget(self)
        if self._on_close:
            self._on_close()

    def on_touch_down(self, touch):
        if super().on_touch_down(touch):
            return True
        return True

    def on_touch_move(self, touch):
        return True

    def on_touch_up(self, touch):
        super().on_touch_up(touch)
        return True


# ---------------------------------------------------------------- info row
class InfoRow(FloatLayout):
    def __init__(self, label='', value='', value_color=None, **kw):
        kw.setdefault('size_hint_y', None)
        kw.setdefault('height', dp(42))
        super().__init__(**kw)
        self._l = L(label, fs=13, color=C.INK2, fixed=True,
                    size_hint=(None, None), size=(dp(180), dp(20)))
        self._v = L(value, fs=13.5, color=value_color or C.INK, halign='right',
                    fixed=True, size_hint=(None, None), size=(dp(160), dp(20)))
        self.add_widget(self._l)
        self.add_widget(self._v)
        self.bind(pos=self._layout, size=self._layout)
        self._layout()

    def _layout(self, *a):
        self._l.x = self.x
        self._l.center_y = self.center_y
        self._v.x = self.x + self.width - self._v.width
        self._v.center_y = self.center_y


# ---------------------------------------------------------------- helpers
def section(title, action=None, on_action=None, height=None):
    h = FloatLayout(size_hint_y=None, height=height or dp(24))
    t = L(title, fs=15.5, color=C.INK, fixed=True, size_hint_y=None, height=sp(24))
    t.pos_hint = {'x': 0, 'center_y': 0.5}
    h.add_widget(t)
    if action:
        a = L(action, fs=12, color=C.GREEN, halign='right', fixed=True,
              size_hint=(None, None), size=(dp(64), dp(24)))
        a.pos_hint = {'right': 1, 'center_y': 0.5}
        h.add_widget(a)
    return h
