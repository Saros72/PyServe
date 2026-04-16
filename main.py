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
import socket

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
        requests.get("http://127.0.0.1:9666", timeout=0.5)
        return True
    except:
        return False


# -----------------------
# 🔥 GET IP ADRESS
# -----------------------
def get_ip():
    try:
        hostname = socket.gethostname()
        ip = socket.gethostbyname(hostname)
        if ip.startswith("127."):
            raise Exception("fallback")
        return ip
    except:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(('8.8.8.8', 1))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return '127.0.0.1'


class App(MDApp):
    custom_blue = get_color_from_hex("#0D47A1")

    url_display = StringProperty("")
    button_text = StringProperty("START")

    running = BooleanProperty(False)
    ready = BooleanProperty(False)

    def build(self):
        self.log_buffer = []
        self.log_queue = []

        Clock.schedule_interval(self._process_log_queue, 0.2)

        self.is_tv = False

        try:
            if ANDROID:
                UiModeManager = autoclass('android.app.UiModeManager')
                Context = autoclass('android.content.Context')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')

                context = PythonActivity.mActivity
                ui_mode = context.getSystemService(Context.UI_MODE_SERVICE)

                if ui_mode.getCurrentModeType() == 4:
                    self.is_tv = True
        except:
            self.is_tv = False

        kv_file = "ui/layout_tv.kv" if self.is_tv else "ui/layout.kv"
        root = Builder.load_file(kv_file)

        Window.bind(on_key_down=self._on_keyboard)
        Window.bind(on_key_up=self._on_keyboard_up)
        Window.bind(on_joy_button_down=self._on_joy)

        return root

    def on_start(self):

        self.url_display = f"http://{get_ip()}:9666" if self.is_tv else "http://127.0.0.1:9666"
        self.add_log("=== APP START ===")

        if ANDROID:
            try:
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                activity = PythonActivity.mActivity

                if self.is_tv:
                    activity.setRequestedOrientation(0)
                else:
                    activity.setRequestedOrientation(1)

            except Exception as e:
                print(f"Orientation error: {e}")

        self.update_system_bars()

        # 🔥 JEDNOTNÁ KONTROLA
        self.check_and_prepare()

        if is_server_running():
            self.running = True
            self.button_text = "STOP"
            self.add_log("Server running OK")
        else:
            self.running = False
            self.button_text = "START"
            self.add_log("Server not running")

    # -----------------------
    # 🔥 KLÍČOVÁ FUNKCE
    # -----------------------
    def check_and_prepare(self):
        try:
            self.setup_plugin_folder()

            # 🔥 PERMISSION TEST
            test_file = os.path.join(BASE_DIR, ".perm_test")

            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)

            os.listdir(BASE_DIR)

            self.ready = True
            self.add_log("Setup OK")
            return True

        except Exception as e:
            self.ready = False
            self.add_error(f"Storage access ERROR: {e}")
            return False

    # -----------------------
    # 🎮 TV / REMOTE CONTROL
    # -----------------------
    def _trigger_button(self):

        if hasattr(self, "root") and self.root:
            try:
                btn = self.root.ids.start_button
                normal_color = btn.md_bg_color[:]

                btn.md_bg_color = [max(0, c * 0.65) for c in normal_color[:3]] + [1]

                def release(dt):
                    btn.trigger_action(duration=0.1)

                    def reset_color(dt2):
                        btn.md_bg_color = normal_color

                    Clock.schedule_once(reset_color, 0.1)

                Clock.schedule_once(release, 0.05)
                return

            except Exception as e:
                print(f"Error trigger: {e}")

        self.toggle_server()

    def _on_keyboard(self, window, key, scancode, codepoint, modifiers):
        return key in (13, 271, 23)

    def _on_keyboard_up(self, window, key, scancode):
        if key in (13, 271, 23, 1073741943):
            self._trigger_button()
            return True
        return False

    def _on_joy(self, window, stick_id, button_id):
        if button_id in (0, 96, 23):
            self._trigger_button()
            return True
        return False

    # -----------------------
    # 🎨 UI
    # -----------------------
    def update_system_bars(self):
        set_bars_colors(self.custom_blue, self.custom_blue, "Dark")

    # -----------------------
    # 📜 LOG SYSTEM
    # -----------------------
    def add_log(self, msg):
        if len(self.log_queue) < 500:
            self.log_queue.append(msg)

    def _process_log_queue(self, dt):
        if not self.log_queue:
            return

        msg = self.log_queue.pop(0)
        self.log_buffer.append(msg)

        try:
            log_label = self.root.ids.log_label
            scroll_view = log_label.parent

            log_label.text = "\n".join(self.log_buffer[-300:])

            def do_scroll(dt2):
                scroll_view.scroll_y = 0 if log_label.height > scroll_view.height else 1

            Clock.schedule_once(do_scroll, 0)

        except Exception as e:
            print(f"Log scroll error: {e}")

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
            self.add_log("\n=== SETUP START ===")

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

            # 🔥 vždy znovu ověřit (NE ready!)
            if not self.check_and_prepare():
                return

            Clock.schedule_once(lambda dt: check_plugins(self.add_log, self.add_error), 0)

            self.button_text = "STOP"
            self.add_log("\nServer START")

            if ANDROID:
                try:
                    service = autoclass('org.pyserve.pyserve.ServiceServer')
                    mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
                    service.start(mActivity, 'small_icon', 'PyServe', 'Server running...', '')
                except Exception as e:
                    self.add_error(f"SERVICE START ERROR: {e}")
                    return
            else:
                self.add_log("Service only on Android")
                return

            def check(dt):
                if is_server_running():
                    self.running = True
                    self.add_log("Server running OK")
                else:
                    self.running = False
                    self.button_text = "START"
                    self.add_error("Server failed")

            Clock.schedule_once(check, 0.5)

        else:
            self.button_text = "START"
            self.running = False
            self.add_log("Server STOP")

            if ANDROID:
                try:
                    service = autoclass('org.pyserve.pyserve.ServiceServer')
                    mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
                    service.stop(mActivity)
                except Exception as e:
                    self.add_error(f"SERVICE STOP ERROR: {e}")
            else:
                self.add_log("Service only on Android")

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