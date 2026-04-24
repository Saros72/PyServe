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

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {
                margin: 0;
                background: #000;
                color: #fff;
                font-family: Arial, sans-serif;
            }

            .header {
                background: #0D47A1;
                padding: 14px;
                font-size: 18px;
                font-weight: bold;
            }

            .card {
                margin: 12px;
                padding: 14px;
                background: #111;
                border-radius: 10px;
                font-size: 14px;
            }

            .row {
                margin-top: 8px;
            }

            .ok {
                color: #4CAF50;
            }

            .link {
                display: block;
                margin-top: 10px;
                padding: 10px;
                background: #0D47A1;
                border-radius: 8px;
                text-align: center;
                text-decoration: none;
                color: #fff;
                font-weight: bold;
            }

            .link:active {
                background: #1565C0;
            }
        </style>
    </head>

    <body>

        <div class="header">PyServe</div>

        <div class="card">
            <b>Server Status</b>
            <div class="row">Bottle: <span class="ok">RUNNING</span></div>
            <div class="row">WebDAV: <span class="ok">RUNNING</span></div>
        </div>

        <div class="card">
            <b>Access</b>

            <a class="link" href="#" onclick="openDav()">Open WebDAV</a>
        </div>

        <div class="card">
            <b>Plugins</b>

            <a class="link" href="/demo">Demo Plugin</a>
        </div>

        <script>
            function openDav() {
                const url = "http://" + location.hostname + ":9667";
                window.location.href = url;
            }
        </script>

    </body>
    </html>
    """

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