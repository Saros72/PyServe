from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.utils.set_bars_colors import set_bars_colors
from kivy.utils import get_color_from_hex
from kivy.properties import StringProperty, BooleanProperty
from kivy.clock import Clock
from plugin_loader import check_plugins

import os
import requests
import webbrowser

# -----------------------
# ANDROID DETECTION
# -----------------------
try:
    from jnius import autoclass
    ANDROID = True
except ImportError:
    ANDROID = False

Window.fullscreen = False

# 📂 PATHS
BASE_DIR = "/storage/emulated/0/PyServe"
PLUGIN_DIR = os.path.join(BASE_DIR, "demo")
ERROR_LOG_FILE = os.path.join(BASE_DIR, "error_log.txt")


# -----------------------
# 🔥 SERVER CHECK
# -----------------------
def is_server_running():
    try:
        requests.get("http://127.0.0.1:9666", timeout=1)
        return True
    except:
        return False


class App(MDApp):
    custom_blue = get_color_from_hex("#0D47A1")

    url_display = StringProperty("")
    button_text = StringProperty("START")

    # 🔥 důležité pro KV (ikona + button)
    running = BooleanProperty(False)

    def build(self):
        self.log_buffer = []
        self.log_queue = []

        # 👉 postupné vypisování logu
        Clock.schedule_interval(self._process_log_queue, 0.2)

        return Builder.load_file("ui/layout.kv")

    def on_start(self):
        self.url_display = "http://localhost:9666"
        self.add_log("=== APP START ===")

        self.update_system_bars()
        self.setup_plugin_folder()

        if is_server_running():
            self.running = True
            self.button_text = "STOP"
            self.add_log("Server running OK")
        else:
            self.running = False
            self.button_text = "START"
            self.add_log("Server not running")

    # -----------------------
    # 🎨 UI
    # -----------------------
    def update_system_bars(self):
        set_bars_colors(self.custom_blue, self.custom_blue, "Dark")

    # -----------------------
    # 📜 LOG SYSTEM (QUEUE)
    # -----------------------
    def add_log(self, msg):
        self.log_queue.append(msg)

    def _process_log_queue(self, dt):
        if not self.log_queue:
            return

        msg = self.log_queue.pop(0)
        self.log_buffer.append(msg)

        try:
            self.root.ids.log_label.text = "\n".join(self.log_buffer[-200:])
        except:
            pass

    def add_error(self, msg, ui=True):
        if ui:
            self.add_log(msg)
        try:
            os.makedirs(BASE_DIR, exist_ok=True)
            with open(ERROR_LOG_FILE, "a", encoding="utf-8") as f:
                f.write(msg + "\n")
        except:
            pass

    # -----------------------
    # 📂 PLUGIN SETUP
    # -----------------------
    def setup_plugin_folder(self):
        try:
            self.add_log("=== SETUP START ===")

            if not os.path.exists(BASE_DIR):
                os.makedirs(BASE_DIR)
                self.add_log("BASE DIR CREATED")

            if not os.path.exists(PLUGIN_DIR):
                os.makedirs(PLUGIN_DIR)
                self.add_log("PLUGIN DIR CREATED")

            assets_dir = os.path.join(os.getcwd(), "assets")

            if not os.path.exists(assets_dir):
                self.add_error("assets folder NOT FOUND")
                return

            demo_src = os.path.join(assets_dir, "demo_plugin.txt")
            demo_dst = os.path.join(PLUGIN_DIR, "default.py")

            if not os.path.exists(demo_src):
                self.add_error("demo_plugin.txt NOT FOUND")
                return

            if not os.path.exists(demo_dst):
                with open(demo_src, "r", encoding="utf-8") as f:
                    code = f.read()

                with open(demo_dst, "w", encoding="utf-8") as f:
                    f.write(code)

                self.add_log("Demo plugin COPIED")

        except Exception as e:
            self.add_error(f"SETUP ERROR: {e}")

    # -----------------------
    # ▶️ SERVER
    # -----------------------
    def toggle_server(self):
        if not self.running:
            check_plugins(self.add_log, self.add_error)

            self.button_text = "STOP"
            self.add_log("Server START")

            try:
                service = autoclass('org.pyserve.pyserve.ServiceServer')
                mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
                service.start(mActivity, 'small_icon', 'PyServe', 'Server running...', '')
            except Exception as e:
                self.add_error(f"SERVICE START ERROR: {e}")
                return

            self.add_log("Checking server...")

            def check(dt):
                if is_server_running():
                    self.running = True
                    self.add_log("Server running OK")
                else:
                    self.running = False
                    self.button_text = "START"
                    self.add_error("Server failed")

            Clock.schedule_once(check, 1.5)

        else:
            self.button_text = "START"
            self.running = False
            self.add_log("Server STOP")

            try:
                service = autoclass('org.pyserve.pyserve.ServiceServer')
                mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
                service.stop(mActivity)
            except Exception as e:
                self.add_error(f"SERVICE STOP ERROR: {e}")

    # -----------------------
    # 🌐 OPEN WEB
    # -----------------------
    def open_web(self):
        if not self.running:
            return

        try:
            webbrowser.open(self.url_display)
            self.add_log("Opening web")
        except Exception as e:
            self.add_error(f"OPEN WEB ERROR: {e}")

    # -----------------------
    # 📂 DRAWER ACTIONS
    # -----------------------
    def open_github(self):
        try:
            webbrowser.open("https://github.com/Saros72/PyServe")
            self.add_log("Opening GitHub/PyServe")
        except Exception as e:
            self.add_error(f"GITHUB ERROR: {e}")

    def open_plugins(self):
        try:
            webbrowser.open("https://github.com/")
            self.add_log("Opening GitHub/Plugins")
        except Exception as e:
            self.add_error(f"GITHUB ERROR: {e}")

    def send_email(self):
        try:
            webbrowser.open("mailto:ss72@seznam.cz")
            self.add_log("Opening email client")
        except Exception as e:
            self.add_error(f"EMAIL ERROR: {e}")


if __name__ == "__main__":
    App().run()