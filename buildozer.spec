[app]

# ---- 基本信息 ----
title = 轻食记
package.name = fitslim
package.domain = org.fitslim

# ---- 源码 ----
source.dir = .
source.include_exts = py,png,jpg,jpeg,kv,atlas,json,ttf,otf,xml
source.include_patterns = assets/*,app/*
source.exclude_dirs = bin,.buildozer,__pycache__,data,.git,.github
source.exclude_patterns = preview.html,run.bat,*.pyc,*.md

version = 1.0.0

# ---- 依赖 ----
requirements = hostpython3==3.11.5,python3==3.11.5,kivy==2.3.1

# ---- 显示 / 方向 ----
orientation = portrait
fullscreen = 1
android.entrypoint = org.kivy.android.PythonActivity

# ---- 覆盖尽可能多的安卓系统 ----
# minapi 21 = Android 5.0，可覆盖 99% 以上设备
android.api = 34
android.minapi = 21
android.ndk_api = 21
# 覆盖所有主流手机/平板架构（含旧 32 位机型）
android.archs = arm64-v8a, armeabi-v7a

# ---- 权限（含计步传感器所需）----
android.permissions = INTERNET,ACCESS_NETWORK_STATE,ACTIVITY_RECOGNITION,VIBRATE,WAKE_LOCK,POST_NOTIFICATIONS

# ---- 其它 ----
android.allow_backup = True
android.wakelock = True
android.presplash_color = #F8FBFF
android.apptheme = @android:style/Theme.NoTitleBar.Fullscreen
android.accept_sdk_license = True

# ---- python-for-android ----
# p4a develop + fix for the broken build-venv pip (PR #3360 / issue #3364)
p4a.branch = develop
p4a.commit = d2ee8c54d9d42375a95f18159e950a119671cf63
p4a.bootstrap = sdl2
