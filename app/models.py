import os
import json
import datetime


def _today():
    return datetime.date.today().isoformat()


def _last7_labels():
    names = ['一', '二', '三', '四', '五', '六', '日']
    today = datetime.date.today()
    out = []
    for i in range(6, -1, -1):
        d = today - datetime.timedelta(days=i)
        out.append('今天' if i == 0 else '周' + names[d.weekday()])
    return out


DEFAULTS = {
    'profile': {
        'name': '小美',
        'height': 165,
        'gender': '女',
        'age': 26,
        'start_weight': 68.0,
        'target_weight': 58.0,
    },
    'goal': {
        'calories': 1600,
        'water_ml': 2000,
        'exercise_min': 45,
        'steps': 8000,
        'sleep_h': 8.0,
    },
    'today': {
        'date': _today(),
        'consumed': 1080,
        'carbs_g': 132, 'carbs_goal': 200,
        'protein_g': 61, 'protein_goal': 90,
        'fat_g': 34, 'fat_goal': 55,
        'exercise_min': 32,
        'calories_burned': 260,
        'water_ml': 1200,
        'steps': 6200,
        'sleep_h': 7.2,
    },
    'weight_now': 65.4,
    'weight_delta': -0.6,
    'weight_series': [67.8, 67.4, 67.1, 66.6, 66.5, 66.0, 65.4],
    'calories_series': [1520, 1680, 1450, 1720, 1600, 1380, 1080],
    'days': _last7_labels(),
    'food_log': [
        {'time': '08:10', 'name': '全麦面包 + 鸡蛋', 'kcal': 320},
        {'time': '12:30', 'name': '鸡胸肉沙拉', 'kcal': 480},
        {'time': '15:40', 'name': '无糖酸奶', 'kcal': 120},
        {'time': '18:20', 'name': '苹果', 'kcal': 160},
    ],
    'exercise_log': [
        {'time': '07:00', 'name': '慢跑', 'min': 20, 'kcal': 180},
        {'time': '19:30', 'name': '力量训练', 'min': 12, 'kcal': 80},
    ],
    'water_log': [
        {'time': '09:00', 'ml': 400},
        {'time': '13:00', 'ml': 400},
        {'time': '16:00', 'ml': 400},
    ],
}


class Store:
    def __init__(self, path):
        self.path = path
        self.data = json.loads(json.dumps(DEFAULTS))
        self.load()
        self._roll_day()

    # ------------------------------------------------------- persistence
    def load(self):
        try:
            if os.path.exists(self.path):
                with open(self.path, 'r', encoding='utf-8') as f:
                    saved = json.load(f)
                for k, v in saved.items():
                    if isinstance(v, dict) and isinstance(self.data.get(k), dict):
                        self.data[k].update(v)
                    else:
                        self.data[k] = v
        except Exception:
            pass

    def save(self):
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            with open(self.path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except Exception:
            pass

    def _roll_day(self):
        if self.data['today'].get('date') != _today():
            self.data['today'] = json.loads(json.dumps(DEFAULTS['today']))
            self.data['today']['date'] = _today()
            self.data['food_log'] = []
            self.data['exercise_log'] = []
            self.data['water_log'] = []
            self.save()

    # ------------------------------------------------------- accessors
    def profile(self):
        return self.data['profile']

    def goal(self):
        return self.data['goal']

    def today(self):
        return self.data['today']

    def get(self, key, default=None):
        return self.data.get(key, default)

    # ------------------------------------------------------- mutations
    def add_food(self, name, kcal):
        kcal = int(round(kcal))
        self.data['today']['consumed'] += kcal
        self.data['food_log'].append({'time': self._now(), 'name': name, 'kcal': kcal})
        self._touch_calories(kcal)
        self.save()
        return kcal

    def add_water(self, ml):
        self.data['today']['water_ml'] += int(ml)
        self.data['water_log'].append({'time': self._now(), 'ml': int(ml)})
        self.save()

    def add_exercise(self, name, minutes, kcal=None):
        minutes = int(minutes)
        kcal = int(kcal if kcal is not None else minutes * 8)
        self.data['today']['exercise_min'] += minutes
        self.data['today']['calories_burned'] += kcal
        self.data['exercise_log'].append(
            {'time': self._now(), 'name': name, 'min': minutes, 'kcal': kcal})
        self.save()
        return kcal

    def set_weight(self, weight):
        weight = round(float(weight), 1)
        prev = self.data['weight_now']
        self.data['weight_now'] = weight
        self.data['weight_delta'] = round(weight - prev, 1)
        s = self.data['weight_series']
        s.append(weight)
        del s[:-7]
        self.save()

    def set_goal(self, key, value):
        self.data['goal'][key] = value
        self.save()

    def set_profile(self, key, value):
        self.data['profile'][key] = value
        self.save()

    def remove_food(self, index):
        try:
            item = self.data['food_log'].pop(index)
            self.data['today']['consumed'] = max(
                0, self.data['today']['consumed'] - item['kcal'])
            self.save()
        except Exception:
            pass

    # ------------------------------------------------------- helpers
    def _touch_calories(self, delta):
        s = self.data['calories_series']
        if s:
            s[-1] = max(0, s[-1] + delta)

    def bmi(self):
        h = self.profile()['height'] / 100.0
        return round(self.data['weight_now'] / (h * h), 1)

    @staticmethod
    def _now():
        return datetime.datetime.now().strftime('%H:%M')
