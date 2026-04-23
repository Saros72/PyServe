import os
import time
import threading
import html
import logging

# -----------------------
# 📂 ROOT + LOG
# -----------------------
BASE_DIR = "/storage/emulated/0/PyServe"
os.makedirs(BASE_DIR, exist_ok=True)

LOG_FILE = os.path.join(BASE_DIR, "service.log")

logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

logging.info("=== SERVICE START ===")

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
    logging.info("WebDAV available")
except Exception as e:
    logging.error(f"WebDAV import failed: {e}")


# -----------------------
# 🔥 DAV SERVER
# -----------------------
def start_dav():
    if not DAV_AVAILABLE:
        logging.warning("WebDAV disabled")
        return

    logging.info("WebDAV starting...")

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
            "verbose": 1,
        }

        dav_app = WsgiDAVApp(config)

        server = wsgi.Server(
            bind_addr=("0.0.0.0", 9667),
            wsgi_app=dav_app
        )

        logging.info("WebDAV running on port 9667")
        server.start()

    except Exception as e:
        logging.exception(f"WebDAV ERROR: {e}")


def start_dav_thread():
    t = threading.Thread(target=start_dav, daemon=True)
    t.start()


# -----------------------
# 🔥 BOTTLE SERVER
# -----------------------
def start_bottle():
    logging.info("Bottle starting...")

    try:
        load_plugins(app)
        logging.info("Plugins loaded")

        app.run(host='0.0.0.0', port=9666, quiet=True)

    except Exception as e:
        logging.exception(f"Bottle ERROR: {e}")


def start_bottle_thread():
    t = threading.Thread(target=start_bottle, daemon=True)
    t.start()


# -----------------------
# 🔥 MAIN
# -----------------------
if __name__ == '__main__':
    try:
        start_dav_thread()
        start_bottle_thread()

        logging.info("SERVER READY")

        while True:
            time.sleep(1)

    except Exception as e:
        logging.exception(f"MAIN LOOP ERROR: {e}")