import os
import time
import threading
import logging

# -----------------------
# 📂 ROOT + LOG
# -----------------------
BASE_DIR = "/storage/emulated/0/PyServe"
os.makedirs(BASE_DIR, exist_ok=True)

LOG_FILE = os.path.join(BASE_DIR, "service_log.txt")

# 🔥 root config
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.INFO,
    format="%(asctime)s | %(name)s | %(levelname)s | %(message)s",
)

# 🔥 loggers
server_log = logging.getLogger("SERVER")
plugin_log = logging.getLogger("PLUGINS")


# -----------------------
# 🔥 Bottle
# -----------------------
from bottle import Bottle
from plugin_loader import load_plugins

app = Bottle()

# -----------------------
# 🔥 WebDAV SAFE IMPORT
# -----------------------
DAV_AVAILABLE = False

try:
    from wsgidav.wsgidav_app import WsgiDAVApp
    from cheroot import wsgi
    DAV_AVAILABLE = True
except Exception as e:
    server_log.error(f"WebDAV import failed")

# -----------------------
# 🔥 DAV SERVER
# -----------------------
def start_dav():
    if not DAV_AVAILABLE:
        server_log.warning("WebDAV disabled")
        return

    try:
        config = {
            "provider_mapping": {"/": BASE_DIR},
            "simple_dc": {"user_mapping": {"*": True}},
            "verbose": 0,
        }

        dav_app = WsgiDAVApp(config)

        server = wsgi.Server(
            bind_addr=("0.0.0.0", 9667),
            wsgi_app=dav_app
        )

        server_log.info("WebDAV started on :9667")

        server.start()

    except Exception:
        server_log.error("WebDAV FAILED")

def start_dav_thread():
    threading.Thread(target=start_dav, daemon=True).start()

# -----------------------
# 🔥 BOTTLE SERVER
# -----------------------
def start_bottle():
    try:
        load_plugins(app)

        import logging as pylogging
        pylogging.getLogger('bottle').setLevel(pylogging.WARNING)
        server_log.info("Bottle started on :9666")
        app.run(host='0.0.0.0', port=9666, quiet=True)

    except Exception:
        server_log.error("Bottle FAILED")

def start_bottle_thread():
    threading.Thread(target=start_bottle, daemon=True).start()

# -----------------------
# 🔥 MAIN
# -----------------------
if __name__ == '__main__':
    start_dav_thread()
    start_bottle_thread()

    while True:
        time.sleep(1)