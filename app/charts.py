from kivy.uix.floatlayout import FloatLayout
from kivy.graphics import Color, Line, Ellipse, Quad, RoundedRectangle
from kivy.properties import ListProperty, NumericProperty
from kivy.metrics import dp

from .theme import C
from .widgets import L


class LineChart(FloatLayout):
    data = ListProperty([])
    labels = ListProperty([])
    color = ListProperty(list(C.GREEN))
    fill = ListProperty([0.08, 0.76, 0.56, 0.16])
    line_width = NumericProperty(dp(3))

    def __init__(self, **kw):
        super().__init__(**kw)
        self._labels = []
        self.bind(pos=self._redraw, size=self._redraw,
                  data=self._redraw, labels=self._redraw)
        self._redraw()

    def _ensure_labels(self):
        if len(self._labels) != len(self.labels):
            for w in self._labels:
                self.remove_widget(w)
            self._labels = [
                L(t, fs=10, color=C.MUTED, halign='center', fixed=True,
                  size_hint=(None, None), size=(dp(44), dp(14)))
                for t in self.labels
            ]
            for w in self._labels:
                self.add_widget(w)

    def _redraw(self, *a):
        self.canvas.clear()
        self._ensure_labels()
        n = len(self.data)
        if n < 2 or self.width <= 1 or self.height <= 1:
            return
        pl, pr, pt, pb = dp(8), dp(8), dp(18), dp(20)
        x0 = self.x + pl
        x1 = self.x + self.width - pr
        y0 = self.y + pb
        y1 = self.y + self.height - pt
        lo, hi = min(self.data), max(self.data)
        if hi - lo < 0.001:
            hi = lo + 1.0
        pad = (hi - lo) * 0.28
        lo, hi = lo - pad, hi + pad

        def mx(i):
            return x0 + (x1 - x0) * i / (n - 1)

        def my(v):
            return y0 + (y1 - y0) * (v - lo) / (hi - lo)

        pts = []
        for i, v in enumerate(self.data):
            pts += [mx(i), my(v)]

        with self.canvas:
            Color(0.09, 0.16, 0.28, 0.06)
            for t in (0.0, 0.5, 1.0):
                gy = y0 + (y1 - y0) * t
                Line(points=[x0, gy, x1, gy], width=dp(1))
            Color(*self.fill)
            for i in range(n - 1):
                ax, ay = pts[2 * i], pts[2 * i + 1]
                bx, by = pts[2 * i + 2], pts[2 * i + 3]
                Quad(points=[ax, ay, bx, by, bx, y0, ax, y0])
            Color(*self.color)
            Line(points=pts, width=self.line_width, joint='round', cap='round')
            for i in range(n):
                cx, cy = pts[2 * i], pts[2 * i + 1]
                Ellipse(pos=(cx - dp(3.6), cy - dp(3.6)), size=(dp(7.2), dp(7.2)))

        for i, w in enumerate(self._labels):
            w.center_x = mx(i)
            w.y = self.y + dp(2)


class BarChart(FloatLayout):
    data = ListProperty([])
    labels = ListProperty([])
    color = ListProperty(list(C.BLUE))
    accent = ListProperty(list(C.GREEN))
    goal = NumericProperty(0)
    goal_color = ListProperty([1.0, 0.52, 0.36, 0.9])

    def __init__(self, **kw):
        super().__init__(**kw)
        self._labels = []
        self.bind(pos=self._redraw, size=self._redraw,
                  data=self._redraw, labels=self._redraw, goal=self._redraw)
        self._redraw()

    def _ensure_labels(self):
        if len(self._labels) != len(self.labels):
            for w in self._labels:
                self.remove_widget(w)
            self._labels = [
                L(t, fs=10, color=C.MUTED, halign='center', fixed=True,
                  size_hint=(None, None), size=(dp(44), dp(14)))
                for t in self.labels
            ]
            for w in self._labels:
                self.add_widget(w)

    def _redraw(self, *a):
        self.canvas.clear()
        self._ensure_labels()
        n = len(self.data)
        if n < 1 or self.width <= 1 or self.height <= 1:
            return
        pl, pr, pt, pb = dp(8), dp(8), dp(16), dp(20)
        x0 = self.x + pl
        x1 = self.x + self.width - pr
        y0 = self.y + pb
        y1 = self.y + self.height - pt
        hi = max(max(self.data), self.goal, 1) * 1.15
        slot = (self.width - pl - pr) / n
        bw = min(slot * 0.52, dp(20))
        peak = max(self.data)

        with self.canvas:
            Color(0.09, 0.16, 0.28, 0.06)
            for t in (0.5, 1.0):
                gy = y0 + (y1 - y0) * t
                Line(points=[x0, gy, x1, gy], width=dp(1))
            for i, v in enumerate(self.data):
                cx = x0 + slot * (i + 0.5)
                h = max(dp(4), (y1 - y0) * v / hi)
                if v == peak and i == n - 1:
                    Color(*self.accent)
                else:
                    Color(*self.color)
                RoundedRectangle(pos=(cx - bw / 2.0, y0), size=(bw, h),
                                 radius=[bw / 2.0])
            if self.goal > 0:
                gy = y0 + (y1 - y0) * self.goal / hi
                Color(*self.goal_color)
                Line(points=[x0, gy, x1, gy],
                     width=dp(1.3), dash_length=dp(6), dash_offset=dp(4))

        for i, w in enumerate(self._labels):
            w.center_x = x0 + slot * (i + 0.5)
            w.y = self.y + dp(2)
