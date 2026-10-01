import random

from kivy.clock import Clock
from kivy.utils import platform


class StepService:
    """Collect the phone's step count.

    - On Android: reads the hardware TYPE_STEP_COUNTER sensor (cumulative
      steps since boot) and converts it to today's steps.
    - On desktop (preview only): simulates steps so the UI can be demonstrated.
    """

    def __init__(self, store, on_update=None):
        self.store = store
        self.on_update = on_update
        self.available = False
        self.source = 'none'
        self._listener = None
        self._tick = None
        self.start()

    # ------------------------------------------------------------------ start
    def start(self):
        if platform == 'android':
            if self._start_android():
                self.available = True
                self.source = 'sensor'
                return
        self._start_sim()
        self.source = 'sim'

    # ------------------------------------------------------------------ android
    def _start_android(self):
        try:
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.ACTIVITY_RECOGNITION])
        except Exception:
            pass
        try:
            from jnius import autoclass, PythonJavaClass, java_method
            Context = autoclass('android.content.Context')
            SensorManager = autoclass('android.hardware.SensorManager')
            Sensor = autoclass('android.hardware.Sensor')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            activity = PythonActivity.mActivity
            self._sm = activity.getSystemService(Context.SENSOR_SERVICE)
            self._sensor = self._sm.getDefaultSensor(Sensor.TYPE_STEP_COUNTER)
            if self._sensor is None:
                return False
            service = self

            class _Listener(PythonJavaClass):
                __javainterfaces__ = ['android/hardware/SensorEventListener']

                @java_method('(Landroid/hardware/SensorEvent;)V')
                def onSensorChanged(self, event):
                    try:
                        service._on_counter(float(event.values[0]))
                    except Exception:
                        pass

                @java_method('(Landroid/hardware/Sensor;I)V')
                def onAccuracyChanged(self, sensor, accuracy):
                    pass

            self._listener = _Listener()
            self._sm.registerListener(self._listener, self._sensor,
                                      SensorManager.SENSOR_DELAY_NORMAL)
            return True
        except Exception:
            return False

    def _on_counter(self, counter):
        base = self.store.get('steps_baseline') or {}
        today = self.store.today()['date']
        if base.get('date') != today or 'value' not in base:
            base = {'date': today, 'value': counter}
            self.store.data['steps_baseline'] = base
            self.store.save()
        steps = int(max(0.0, counter - base.get('value', counter)))
        self.store.data['today']['steps'] = steps
        if self.on_update:
            self.on_update(steps)

    # ------------------------------------------------------------------ desktop sim
    def _start_sim(self):
        self._tick = Clock.schedule_interval(self._sim_step, 3.0)

    def _sim_step(self, dt):
        t = self.store.today()
        t['steps'] = min(int(t['steps']) + random.randint(1, 4), 30000)
        if self.on_update:
            self.on_update(t['steps'])

    def stop(self):
        if self._tick:
            self._tick.cancel()
            self._tick = None
