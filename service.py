import os
import time
import threading
import html

# 🔥 Bottle
from bottle import Bottle
from plugin_loader import load_plugins

# 🔥 WebDAV
from wsgidav.wsgidav_app import WsgiDAVApp
from cheroot import wsgi


# 📂 ROOT
BASE_DIR = "/storage/emulated/0/PyServe"

app = Bottle()


# -----------------------
# DAV SERVER
# -----------------------
def start_dav():
    print("🔥 WebDAV start")

    try:
        config = {
            "provider_mapping": {
                "/": BASE_DIR
            },
            "simple_dc": {
                "user_mapping": {
                    "*": True
                }
            },
        }

        dav_app = WsgiDAVApp(config)

        server = wsgi.Server(
            bind_addr=("0.0.0.0", 9667),
            wsgi_app=dav_app
        )

        print("✅ WebDAV běží na :9667")
        server.start()

    except Exception as e:
        print("❌ DAV ERROR:", e)


def start_dav_thread():
    t = threading.Thread(target=start_dav, daemon=True)
    t.start()


# -----------------------
# BOTTLE SERVER
# -----------------------
def start_bottle():
    print("🔥 Bottle start")

    load_plugins(app)

    app.run(host='0.0.0.0', port=9666, quiet=True)


def start_bottle_thread():
    t = threading.Thread(target=start_bottle, daemon=True)
    t.start()


# -----------------------
# MAIN
# -----------------------
if __name__ == '__main__':
    start_dav_thread()      # WebDAV
    start_bottle_thread()   # PyServe + pluginy

    print("🚀 SERVER READY")

    while True:
        time.sleep(1)