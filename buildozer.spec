[app]

title = PyServe
package.name = pyserve
package.domain = org.pyserve

version = 0.1.0

# --- SOURCE ---
source.dir = .
source.include_exts = py,png,jpg,kv,json,txt
android.add_asset_dirs = assets

# --- REQUIREMENTS ---
requirements = python3,kivy,bottle,requests,kivymd,pillow,pyjnius,plyer,bs4,websocket-client

# --- SERVICES ---
services = server:service.py:foreground:sticky

# --- UI ---
# portrait or landscape
orientation = landscape
fullscreen = 0

# --- ANDROID SDK ---
android.api = 31
android.minapi = 21
android.target = 31

# --- ANDROID PERMISSION ---
android.permissions = INTERNET,POST_NOTIFICATIONS,FOREGROUND_SERVICE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,MANAGE_EXTERNAL_STORAGE

# --- ARCH ---
android.archs = arm64-v8a,armeabi-v7a

# --- ICON ---
icon.filename = assets/icon.png
# --- SPLASH ---
# splash.png or splash_tv.png
presplash.filename = assets/splash.png
android.presplash_color = #FFFFFF

android.manifest_template = android/AndroidManifest.tmpl.xml

# --- BOOTSTRAP ---
p4a.bootstrap = sdl2

# --- DEBUG ---
log_level = 2

android.allow_backup = False