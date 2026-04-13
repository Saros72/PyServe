[app]

title = PyServe
package.name = pyserve
package.domain = org.pyserve

version = 1.0

# --- SOURCE ---
source.dir = .
source.include_exts = py,png,jpg,kv,json,txt
android.add_asset_dirs = assets

# --- REQUIREMENTS ---
requirements = python3,kivy,bottle,requests,kivymd,pillow,pyjnius,plyer,bs4,websocket-client

# --- SERVICES ---
services = server:service.py:foreground:sticky

# --- UI ---
orientation = all
fullscreen = 0

# --- ANDROID ---
android.api = 30
android.minapi = 21
android.target = 30

# permissions
android.permissions = INTERNET,POST_NOTIFICATIONS,FOREGROUND_SERVICE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE

# --- ARCH ---
android.archs = arm64-v8a,armeabi-v7a

# --- BOOTSTRAP ---
p4a.bootstrap = sdl2

# --- DEBUG ---
log_level = 2

android.allow_backup = False