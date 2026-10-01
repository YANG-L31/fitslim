import datetime

from kivy.clock import Clock
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.widget import Widget
from kivy.uix.scrollview import ScrollView
from kivy.uix.screenmanager import ScreenManager, Screen, FadeTransition
from kivy.graphics import Color, Rectangle
from kivy.metrics import dp, sp

from .theme import C, PAD, GAP, RADIUS, NAV_H, CARD_PAD, STAT_H

PAD4 = [CARD_PAD, CARD_PAD, CARD_PAD, CARD_PAD]
from .widgets import (RoundedBox, Icon, L, ProgressRing, MacroBar, StatCard,
                      GoalRow, NavBar, InfoRow, ListRow, Segmented, Stepper,
                      TapButton, PrimaryButton, TextField, vgradient, section,
                      AnnouncementPopup)
from .charts import LineChart, BarChart
from .steps import StepService


def greeting():
    h = datetime.datetime.now().hour
    if h < 6:
        return '凌晨好，'
    if h < 12:
        return '早上好，'
    if h < 18:
        return '下午好，'
    return '晚上好，'


# ===================================================================== base
class Page(Screen):
    def __init__(self, store, **kw):
        super().__init__(**kw)
        self.store = store
        root = FloatLayout()
        self.add_widget(root)
        self.sv = ScrollView(do_scroll_x=False, bar_width=dp(2),
                             bar_color=(0.6, 0.7, 0.85, 0.5))
        self.box = BoxLayout(orientation='vertical', size_hint_y=None,
                             spacing=GAP, padding=[PAD, dp(8), PAD, dp(18)])
        self.box.bind(minimum_height=self.box.setter('height'))
        self.sv.add_widget(self.box)
        self.sv.bind(width=lambda s, v: setattr(self.box, 'width', v))
        root.add_widget(self.sv)

    def refresh(self):
        self.box.clear_widgets()
        self.build(self.box)

    def defer(self):
        Clock.schedule_once(lambda *_: self.refresh(), 0)

    def title(self, text, sub=''):
        h = BoxLayout(orientation='vertical', size_hint_y=None,
                      height=dp(58) if sub else dp(40))
        h.add_widget(L(text, fs=24, color=C.INK, fixed=True, size_hint_y=None,
                       height=sp(36)))
        if sub:
            h.add_widget(L(sub, fs=12, color=C.MUTED, fixed=True,
                           size_hint_y=None, height=sp(18)))
        return h

    def build(self, box):
        pass


# ===================================================================== home
class HomePage(Page):
    def build(self, box):
        self._header(box)
        self._hero(box)
        self._stats(box)
        self._goals(box)
        self._tip(box)

    def _header(self, box):
        h = FloatLayout(size_hint_y=None, height=dp(60))
        prof = self.store.profile()
        left = BoxLayout(orientation='vertical', size_hint=(0.6, None),
                         height=dp(46), pos_hint={'x': 0, 'center_y': 0.5})
        left.add_widget(L(greeting(), fs=12, color=C.MUTED, fixed=True,
                          size_hint_y=None, height=sp(17)))
        left.add_widget(L(prof['name'], fs=21, color=C.INK, fixed=True,
                          size_hint_y=None, height=sp(28)))
        h.add_widget(left)

        right = BoxLayout(orientation='horizontal', spacing=dp(8),
                          size_hint=(None, None), size=(dp(96), dp(44)),
                          pos_hint={'right': 1, 'center_y': 0.5})
        bell = RoundedBox(size_hint=(None, None), size=(dp(42), dp(42)),
                          radius=dp(14), bg=list(C.CARD), shadow=True)
        bell.add_widget(Icon(name='bell', color=list(C.INK2), lw=dp(2),
                             size_hint=(0.5, 0.5),
                             pos_hint={'center_x': 0.5, 'center_y': 0.5}))
        avatar = RoundedBox(size_hint=(None, None), size=(dp(44), dp(44)),
                            radius=dp(22), shadow=True,
                            grad_top=list(C.GOLD), grad_bottom=list(C.ORANGE))
        avatar.fill(L(prof['name'][0], fs=17, color=C.WHITE,
                      halign='center', fixed=True, size_hint=(1, 1)))
        right.add_widget(bell)
        right.add_widget(avatar)
        h.add_widget(right)
        box.add_widget(h)

    def _hero(self, box):
        t = self.store.today()
        goal = self.store.goal()
        remaining = max(0, goal['calories'] - t['consumed'])
        pct = min(1.0, t['consumed'] / float(goal['calories']))

        hero = RoundedBox(size_hint_y=None, height=dp(196), radius=RADIUS,
                          grad_top=list(C.GREEN_L), grad_bottom=list(C.GREEN))
        v = BoxLayout(orientation='vertical', spacing=dp(8),
                      padding=PAD4)
        hero.fill(v)

        top = BoxLayout(orientation='horizontal', spacing=dp(4),
                        size_hint_y=None, height=dp(116))
        left = BoxLayout(orientation='vertical')
        left.add_widget(L('今日热量', fs=12.5, color=C.WHITE_D, fixed=True,
                          size_hint_y=None, height=sp(18)))
        left.add_widget(Widget())
        left.add_widget(L('还可摄入', fs=11, color=C.WHITE_M, fixed=True,
                          size_hint_y=None, height=sp(15)))
        numbox = BoxLayout(orientation='horizontal', spacing=dp(4),
                           size_hint_y=None, height=dp(46))
        numbox.add_widget(L(str(remaining), fs=38, color=C.WHITE, fixed=True,
                            size_hint=(None, None), size=(dp(74), dp(46)),
                            halign='left'))
        numbox.add_widget(L('kcal', fs=13, color=C.WHITE_D, fixed=True,
                            size_hint=(None, None), size=(dp(40), dp(46)),
                            halign='left'))
        numbox.add_widget(Widget())
        left.add_widget(numbox)
        left.add_widget(L('目标 %d kcal' % goal['calories'], fs=11,
                          color=C.WHITE_M, fixed=True,
                          size_hint_y=None, height=sp(15)))
        top.add_widget(left)

        ring = ProgressRing(progress=pct, thickness=dp(12),
                            track_color=[1, 1, 1, 0.25],
                            ring_color=[1, 1, 1, 0.96],
                            size_hint=(None, None), size=(dp(112), dp(112)))
        ring.add_widget(L('%d%%' % round(pct * 100), fs=21, color=C.WHITE,
                          halign='center', fixed=True, size_hint=(1, None),
                          height=dp(24),
                          pos_hint={'center_x': 0.5, 'center_y': 0.60}))
        ring.add_widget(L('已摄入', fs=10, color=C.WHITE_M, halign='center',
                          fixed=True, size_hint=(1, None), height=dp(14),
                          pos_hint={'center_x': 0.5, 'center_y': 0.38}))
        top.add_widget(ring)
        v.add_widget(top)
        v.add_widget(RoundedBox(bg=list(C.WHITE_L), radius=dp(1), shadow=False,
                                size_hint_y=None, height=dp(1)))

        macros = BoxLayout(orientation='horizontal', spacing=dp(12),
                           size_hint_y=None, height=dp(34))
        for label, cur, gl in [
            ('碳水', t['carbs_g'], t['carbs_goal']),
            ('蛋白', t['protein_g'], t['protein_goal']),
            ('脂肪', t['fat_g'], t['fat_goal']),
        ]:
            mb = MacroBar(size_hint_x=1, label=label,
                          bar_color=[1, 1, 1, 0.95],
                          track_color=[1, 1, 1, 0.22],
                          text_color=[1, 1, 1, 0.92],
                          progress=cur / float(gl))
            mb.value_text = '%d/%d g' % (cur, gl)
            macros.add_widget(mb)
        v.add_widget(macros)
        box.add_widget(hero)

    def _stats(self, box):
        t = self.store.today()
        row = BoxLayout(orientation='horizontal', spacing=GAP,
                        size_hint_y=None, height=STAT_H)
        row.add_widget(StatCard(icon='scale', name='体重',
                                value='%.1f' % self.store.get('weight_now'),
                                unit='kg'))
        row.add_widget(StatCard(icon='run', name='运动',
                                value=str(t['exercise_min']), unit='min'))
        row.add_widget(StatCard(icon='drop', name='喝水',
                                value='%.1f' % (t['water_ml'] / 1000.0),
                                unit='L'))
        box.add_widget(row)

    def _goals(self, box):
        t = self.store.today()
        goal = self.store.goal()
        box.add_widget(section('今日目标', action='查看全部'))

        card = RoundedBox(bg=list(C.CARD), radius=RADIUS, size_hint_y=None,
                          height=dp(226))
        v = BoxLayout(orientation='vertical', spacing=dp(10),
                      padding=PAD4)
        card.fill(v)

        def row(name, value_text, progress, color):
            r = GoalRow(size_hint_y=None, height=dp(42), name=name,
                        progress=progress, bar_color=list(color))
            r.value_text = value_text
            return r

        self._steps_row = row('步数', '%d / %d' % (t['steps'], goal['steps']),
                              t['steps'] / float(goal['steps']), C.BLUE)
        v.add_widget(self._steps_row)
        v.add_widget(row('饮水量', '%.1f / %.1f L' % (t['water_ml'] / 1000.0,
                         goal['water_ml'] / 1000.0),
                         t['water_ml'] / float(goal['water_ml']), C.TEAL))
        v.add_widget(row('运动', '%d / %d 分钟' % (t['exercise_min'], goal['exercise_min']),
                         t['exercise_min'] / float(goal['exercise_min']), C.ORANGE))
        v.add_widget(row('睡眠', '%.1f / %.1f 小时' % (t['sleep_h'], goal['sleep_h']),
                         t['sleep_h'] / float(goal['sleep_h']), C.PURPLE))
        box.add_widget(card)

    def update_steps(self, steps):
        row = getattr(self, '_steps_row', None)
        if row is None:
            return
        goal = self.store.goal()['steps']
        row.value_text = '%d / %d' % (steps, goal)
        row.progress = steps / float(goal)

    def _tip(self, box):
        card = RoundedBox(radius=RADIUS, size_hint_y=None, height=dp(84),
                          grad_top=list(C.MINT), grad_bottom=list(C.WHITE))
        h = BoxLayout(orientation='horizontal', spacing=dp(12),
                      padding=PAD4)
        card.fill(h)
        chip = RoundedBox(size_hint=(None, None), size=(dp(42), dp(42)),
                          radius=dp(14), bg=list(C.CARD), shadow=False)
        chip.add_widget(Icon(name='target', color=list(C.GREEN), lw=dp(2),
                             size_hint=(0.56, 0.56),
                             pos_hint={'center_x': 0.5, 'center_y': 0.5}))
        h.add_widget(chip)
        texts = BoxLayout(orientation='vertical', spacing=dp(2))
        texts.add_widget(L('今日小贴士', fs=13.5, color=C.INK, fixed=True,
                           size_hint_y=None, height=sp(20)))
        texts.add_widget(L('多喝水有助于提升代谢，下午加餐可以选一小把坚果。',
                           fs=11.5, color=C.MUTED, fixed=True,
                           size_hint_y=None, height=dp(34)))
        h.add_widget(texts)
        box.add_widget(card)


# ===================================================================== record
class RecordPage(Page):
    def __init__(self, store, **kw):
        self.seg_index = 0
        super().__init__(store, **kw)

    def build(self, box):
        box.add_widget(self.title('记录', '记录今天的饮食、体重与运动'))
        self._summary(box)
        seg = Segmented(['饮食', '体重', '运动', '喝水'],
                        callback=self._seg_changed)
        seg.index = self.seg_index
        seg.select(self.seg_index, fire=False)
        box.add_widget(seg)
        self._form(box)
        self._log(box)

    def _summary(self, box):
        t = self.store.today()
        row = BoxLayout(orientation='horizontal', spacing=GAP,
                        size_hint_y=None, height=STAT_H)
        row.add_widget(StatCard(icon='flame', name='已摄入',
                                value=str(t['consumed']), unit='kcal'))
        row.add_widget(StatCard(icon='run', name='已消耗',
                                value=str(t['calories_burned']), unit='kcal'))
        row.add_widget(StatCard(icon='drop', name='饮水',
                                value='%.1f' % (t['water_ml'] / 1000.0),
                                unit='L'))
        box.add_widget(row)

    def _seg_changed(self, i):
        self.seg_index = i
        self.defer()

    def _form(self, box):
        i = self.seg_index
        if i == 0:
            self.f_name = TextField(hint='食物名称，如：燕麦粥', height=dp(50))
            self.f_kcal = TextField(hint='热量 (kcal)', input_filter='float',
                                    height=dp(50))
            btn = PrimaryButton('添加饮食')
            btn.callback = self._add_food
            box.add_widget(self._form_card(200, [self.f_name, self.f_kcal, btn]))
        elif i == 1:
            self.f_weight = TextField(hint='体重 (kg)，如 65.4',
                                      input_filter='float', height=dp(50))
            btn = PrimaryButton('记录体重')
            btn.callback = self._add_weight
            box.add_widget(self._form_card(142, [self.f_weight, btn]))
        elif i == 2:
            self.f_ex = TextField(hint='运动项目，如：慢跑', height=dp(50))
            self.f_min = TextField(hint='时长 (分钟)', input_filter='int',
                                   height=dp(50))
            btn = PrimaryButton('添加运动')
            btn.callback = self._add_exercise
            box.add_widget(self._form_card(200, [self.f_ex, self.f_min, btn]))
        else:
            t = self.store.today()
            info = L('今日已喝水 %.1f / %.1f L' % (t['water_ml'] / 1000.0,
                     self.store.goal()['water_ml'] / 1000.0),
                     fs=13, color=C.INK2, fixed=True,
                     size_hint_y=None, height=dp(24))
            r = BoxLayout(orientation='horizontal', spacing=dp(12),
                          size_hint_y=None, height=dp(52))
            b1 = TapButton('+250 ml', bg=list(C.BLUE_L), fg=list(C.BLUE), fs=15)
            b1.callback = lambda: self._add_water(250)
            b2 = TapButton('+500 ml', bg=list(C.MINT), fg=list(C.GREEN_D), fs=15)
            b2.callback = lambda: self._add_water(500)
            r.add_widget(b1)
            r.add_widget(b2)
            box.add_widget(self._form_card(114, [info, r]))

    def _form_card(self, height, children):
        card = RoundedBox(bg=list(C.CARD), radius=RADIUS, size_hint_y=None,
                          height=dp(height))
        v = BoxLayout(orientation='vertical', spacing=dp(10),
                      padding=PAD4)
        card.fill(v)
        for c in children:
            v.add_widget(c)
        return card

    # -- actions
    def _add_food(self):
        name = (self.f_name.text or '').strip() or '食物'
        try:
            kcal = float(self.f_kcal.text or 0)
        except ValueError:
            kcal = 0
        if kcal <= 0:
            return
        self.store.add_food(name, kcal)
        self.defer()

    def _add_weight(self):
        try:
            w = float(self.f_weight.text or 0)
        except ValueError:
            w = 0
        if w <= 0:
            return
        self.store.set_weight(w)
        self.defer()

    def _add_exercise(self):
        name = (self.f_ex.text or '').strip() or '运动'
        try:
            m = int(float(self.f_min.text or 0))
        except ValueError:
            m = 0
        if m <= 0:
            return
        self.store.add_exercise(name, m)
        self.defer()

    def _add_water(self, ml):
        self.store.add_water(ml)
        self.defer()

    def _log(self, box):
        box.add_widget(section('今日记录'))
        entries = []
        for it in self.store.get('food_log'):
            entries.append((it['time'], 'flame', list(C.ORANGE), list(C.ORANGE_L),
                            it['name'], it['time'], '+%d kcal' % it['kcal']))
        for it in self.store.get('exercise_log'):
            entries.append((it['time'], 'run', list(C.GREEN), list(C.MINT),
                            it['name'], it['time'], '%d 分钟' % it['min']))
        for it in self.store.get('water_log'):
            entries.append((it['time'], 'drop', list(C.BLUE), list(C.BLUE_L),
                            '喝水', it['time'], '+%d ml' % it['ml']))
        entries.sort(key=lambda e: e[0], reverse=True)

        if not entries:
            card = RoundedBox(bg=list(C.CARD), radius=RADIUS, size_hint_y=None,
                              height=dp(80))
            card.fill(L('今天还没有记录，快去添加吧', fs=13, color=C.MUTED,
                        halign='center', fixed=True, size_hint=(1, 1)))
            box.add_widget(card)
            return

        card = RoundedBox(bg=list(C.CARD), radius=RADIUS, size_hint_y=None,
                          height=dp(len(entries) * 56 + 12))
        v = BoxLayout(orientation='vertical', size_hint_y=None,
                      height=dp(len(entries) * 56),
                      padding=[dp(6), dp(6), dp(6), dp(6)])
        card.fill(v)
        for _, icon, col, tint, title, time, value in entries:
            v.add_widget(ListRow(icon=icon, title=title, subtitle=time,
                                 value=value, color=col, tint=tint))
        box.add_widget(card)


# ===================================================================== stats
class StatsPage(Page):
    def build(self, box):
        box.add_widget(self.title('趋势', '看看你的变化曲线'))
        self._summary(box)
        self._weight_chart(box)
        self._calorie_chart(box)

    def _summary(self, box):
        ws = self.store.get('weight_series')
        cal = self.store.get('calories_series')
        goal = self.store.goal()['calories']
        delta = round(ws[-1] - ws[0], 1)
        avg = int(sum(cal) / len(cal)) if cal else 0
        days = sum(1 for c in cal if c <= goal)

        row = BoxLayout(orientation='horizontal', spacing=GAP,
                        size_hint_y=None, height=STAT_H)
        row.add_widget(StatCard(icon='scale', name='本周减重',
                                value=('%.1f' % abs(delta)) if delta else '0.0',
                                unit='kg'))
        row.add_widget(StatCard(icon='flame', name='平均摄入',
                                value=str(avg), unit='kcal'))
        row.add_widget(StatCard(icon='target', name='达标天数',
                                value='%d/7' % days, unit=''))
        box.add_widget(row)

    def _weight_chart(self, box):
        box.add_widget(section('体重趋势'))
        card = RoundedBox(bg=list(C.CARD), radius=RADIUS, size_hint_y=None,
                          height=dp(210))
        v = BoxLayout(orientation='vertical', spacing=dp(6),
                      padding=PAD4)
        card.fill(v)
        head = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(26))
        head.add_widget(L('近 7 天 (kg)', fs=12.5, color=C.INK2, fixed=True,
                          size_hint_x=1, size_hint_y=None, height=sp(26)))
        head.add_widget(L('当前 %.1f' % self.store.get('weight_now'), fs=12.5,
                          color=C.GREEN, halign='right', fixed=True,
                          size_hint=(None, None), size=(dp(90), dp(26))))
        v.add_widget(head)
        chart = LineChart(data=list(self.store.get('weight_series')),
                          labels=list(self.store.get('days')),
                          color=list(C.GREEN),
                          fill=[0.08, 0.76, 0.56, 0.16],
                          size_hint_y=None, height=dp(150))
        v.add_widget(chart)
        box.add_widget(card)

    def _calorie_chart(self, box):
        box.add_widget(section('热量摄入'))
        card = RoundedBox(bg=list(C.CARD), radius=RADIUS, size_hint_y=None,
                          height=dp(210))
        v = BoxLayout(orientation='vertical', spacing=dp(6),
                      padding=PAD4)
        card.fill(v)
        head = BoxLayout(orientation='horizontal', size_hint_y=None, height=dp(26))
        head.add_widget(L('近 7 天 (kcal)', fs=12.5, color=C.INK2, fixed=True,
                          size_hint_x=1, size_hint_y=None, height=sp(26)))
        head.add_widget(L('目标 %d' % self.store.goal()['calories'], fs=12.5,
                          color=C.ORANGE, halign='right', fixed=True,
                          size_hint=(None, None), size=(dp(90), dp(26))))
        v.add_widget(head)
        chart = BarChart(data=list(self.store.get('calories_series')),
                         labels=list(self.store.get('days')),
                         color=[0.30, 0.60, 1.0, 0.85], goal=self.store.goal()['calories'],
                         size_hint_y=None, height=dp(150))
        v.add_widget(chart)
        box.add_widget(card)


# ===================================================================== profile
class ProfilePage(Page):
    def build(self, box):
        box.add_widget(self.title('我的'))
        self._profile_card(box)
        self._goal_card(box)
        self._body_card(box)
        self._more(box)

    def _profile_card(self, box):
        prof = self.store.profile()
        card = RoundedBox(bg=list(C.CARD), radius=RADIUS, size_hint_y=None,
                          height=dp(96))
        h = BoxLayout(orientation='horizontal', spacing=dp(14),
                      padding=PAD4)
        card.fill(h)
        avatar = RoundedBox(size_hint=(None, None), size=(dp(60), dp(60)),
                            radius=dp(30), shadow=False,
                            grad_top=list(C.GOLD), grad_bottom=list(C.ORANGE))
        avatar.fill(L(prof['name'][0], fs=24, color=C.WHITE,
                      halign='center', fixed=True, size_hint=(1, 1)))
        h.add_widget(avatar)
        col = BoxLayout(orientation='vertical', spacing=dp(3))
        col.add_widget(L(prof['name'], fs=19, color=C.INK, fixed=True,
                         size_hint_y=None, height=sp(24)))
        col.add_widget(L('BMI %.1f · 身高 %dcm · %d岁' % (
            self.store.bmi(), prof['height'], prof['age']),
            fs=12, color=C.MUTED, fixed=True, size_hint_y=None, height=sp(18)))
        col.add_widget(L('目标体重 %.1f kg' % prof['target_weight'], fs=12,
                         color=C.GREEN, fixed=True, size_hint_y=None, height=sp(18)))
        h.add_widget(col)
        box.add_widget(card)

    def _goal_card(self, box):
        goal = self.store.goal()
        prof = self.store.profile()
        box.add_widget(section('目标设置'))
        card = RoundedBox(bg=list(C.CARD), radius=RADIUS, size_hint_y=None,
                          height=dp(238))
        v = BoxLayout(orientation='vertical', spacing=dp(6),
                      padding=PAD4)
        card.fill(v)

        v.add_widget(Stepper(name='目标体重', value=prof['target_weight'],
                             step=0.5, unit='kg', fmt='{:.1f}',
                             minimum=30, maximum=150,
                             callback=lambda val: self._save_profile('target_weight', val)))
        v.add_widget(Stepper(name='每日热量', value=goal['calories'], step=50,
                             unit='kcal', fmt='{:.0f}', minimum=800, maximum=4000,
                             callback=lambda val: self._save_goal('calories', int(val))))
        v.add_widget(Stepper(name='每日饮水', value=goal['water_ml'] / 1000.0,
                             step=0.25, unit='L', fmt='{:.2f}', minimum=0.5,
                             maximum=6, callback=lambda val: self._save_goal('water_ml', int(val * 1000))))
        v.add_widget(Stepper(name='每日运动', value=goal['exercise_min'], step=5,
                             unit='分钟', fmt='{:.0f}', minimum=10, maximum=300,
                             callback=lambda val: self._save_goal('exercise_min', int(val))))
        box.add_widget(card)

    def _body_card(self, box):
        prof = self.store.profile()
        box.add_widget(section('身体数据'))
        card = RoundedBox(bg=list(C.CARD), radius=RADIUS, size_hint_y=None,
                          height=dp(196))
        v = BoxLayout(orientation='vertical', spacing=dp(4),
                      padding=PAD4)
        card.fill(v)
        v.add_widget(InfoRow(label='身高', value='%d cm' % prof['height']))
        v.add_widget(InfoRow(label='起始体重', value='%.1f kg' % prof['start_weight']))
        v.add_widget(InfoRow(label='当前体重', value='%.1f kg' % self.store.get('weight_now')))
        v.add_widget(InfoRow(label='目标体重', value='%.1f kg' % prof['target_weight'],
                             value_color=list(C.GREEN)))
        box.add_widget(card)

    def _more(self, box):
        box.add_widget(section('更多'))
        card = RoundedBox(bg=list(C.CARD), radius=RADIUS, size_hint_y=None,
                          height=dp(180))
        v = BoxLayout(orientation='vertical', size_hint_y=None, height=dp(168),
                      padding=[dp(6), dp(6), dp(6), dp(6)])
        card.fill(v)
        v.add_widget(ListRow(icon='bell', title='提醒设置', subtitle='喝水 · 运动 · 打卡',
                             value='', color=list(C.BLUE)))
        v.add_widget(ListRow(icon='chart', title='数据导出', subtitle='导出为 CSV',
                             value='', color=list(C.PURPLE)))
        v.add_widget(ListRow(icon='user', title='关于轻食记', subtitle='版本 1.0',
                             value='', color=list(C.GREEN)))
        box.add_widget(card)

    def _save_goal(self, key, value):
        self.store.set_goal(key, value)

    def _save_profile(self, key, value):
        self.store.set_profile(key, value)


# ===================================================================== root
class Root(FloatLayout):
    def __init__(self, store, **kw):
        super().__init__(**kw)
        self.store = store
        with self.canvas.before:
            self._bg_col = Color(1, 1, 1, 1)
            self._bg = Rectangle(texture=vgradient(C.BG_TOP, C.BG_BOT))
        self.bind(pos=self._bg_upd, size=self._bg_upd)
        self._bg_upd()

        self.sm = ScreenManager(transition=FadeTransition(duration=0.16),
                                size_hint=(None, None))
        self.pages = {
            'home': HomePage(store, name='home'),
            'record': RecordPage(store, name='record'),
            'stats': StatsPage(store, name='stats'),
            'profile': ProfilePage(store, name='profile'),
        }
        for page in self.pages.values():
            self.sm.add_widget(page)
        self.add_widget(self.sm)

        self.nav = NavBar(size_hint=(None, None))
        self.nav.callback = self._switch
        self.add_widget(self.nav)

        self.bind(pos=self._layout, size=self._layout)
        self._layout()
        self.pages['home'].refresh()
        self.nav.set_active('home')

        # collect the phone's steps (sensor on Android / simulated on desktop)
        self.steps = StepService(store, on_update=self._on_steps)

        # announcement popup, shown every time the app starts
        self.popup = AnnouncementPopup(
            title='温馨提示',
            message='减肥要慢慢来；不要伤害身体')
        self.add_widget(self.popup)

    def _on_steps(self, steps):
        if getattr(self, 'sm', None) and self.sm.current == 'home':
            page = self.pages.get('home')
            if page:
                page.update_steps(steps)

    def _bg_upd(self, *a):
        self._bg.pos = self.pos
        self._bg.size = self.size

    def _layout(self, *a):
        self.sm.pos = (self.x, self.y + NAV_H)
        self.sm.size = (self.width, max(0, self.height - NAV_H))
        self.nav.pos = (self.x, self.y)
        self.nav.size = (self.width, NAV_H)

    def _switch(self, key):
        self.pages[key].refresh()
        self.sm.current = key
        self.nav.set_active(key)
