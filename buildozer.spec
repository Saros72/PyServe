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
orientation = portrait
fullscreen = 0

# --- ANDROID SDK ---
android.minapi = 21
android.target = 33
android.api = 33

# --- ANDROID PERMISSION ---
android.permissions = INTERNET,POST_NOTIFICATIONS,FOREGROUND_SERVICE,MANAGE_EXTERNAL_STORAGE

# --- ARCH ---
android.archs = arm64-v8a

android.ndk = 25b

# --- ICON ---
icon.filename = assets/icon.png

# --- SPLASH ---
# splash.png or splash_tv.png
#presplash.filename = assets/splash.png
android.presplash_screen = presplash
android.add_resources = %(source.dir)s/res
android.presplash_color = #FFFFFF

# --- p4a ---
p4a.bootstrap = sdl2
p4a.branch = master

# --- DEBUG ---
log_level = 2

android.allow_backup = False