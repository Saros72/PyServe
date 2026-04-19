from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.utils.set_bars_colors import set_bars_colors
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivy.utils import get_color_from_hex
from kivy.properties import StringProperty, BooleanProperty, ListProperty
from kivy.clock import Clock
from plugin_loader import check_plugins
from jnius import autoclass
from android.runnable import run_on_ui_thread
from kivy.storage.jsonstore import JsonStore

import os
import requests
import webbrowser
import socket

Window.fullscreen = False

# 📂 PATHS
BASE_DIR = "/storage/emulated/0/PyServe"
PLUGIN_DIR = os.path.join(BASE_DIR, "demo")
ERROR_LOG_FILE = os.path.join(BASE_DIR, "error_log.txt")
kv_file = "ui/layout.kv"


Intent = autoclass('android.content.Intent')
PythonActivity = autoclass('org.kivy.android.PythonActivity')
String = autoclass('java.lang.String')
Settings = autoclass('android.provider.Settings')
Uri = autoclass('android.net.Uri')


@run_on_ui_thread
def open_all_files_permission():
    activity = PythonActivity.mActivity

    intent = Intent(Settings.ACTION_MANAGE_APP_ALL_FILES_ACCESS_PERMISSION)
    uri = Uri.parse("package:" + activity.getPackageName())

    intent.setData(uri)
    activity.startActivity(intent)


@run_on_ui_thread
def share_text(text):
    activity = PythonActivity.mActivity

    intent = Intent()
    intent.setAction(Intent.ACTION_SEND)
    intent.setType("text/plain")

    intent.putExtra(Intent.EXTRA_SUBJECT, String("PyServe"))
    intent.putExtra(Intent.EXTRA_TEXT, String(text))

    chooser = Intent.createChooser(intent, String("Share PyServe"))

    activity.startActivity(chooser)


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

    LOG_SCROLL_STEP = 0.06

    def build(self):
        self.log_buffer = []
        self.log_queue = []

        Clock.schedule_interval(self._process_log_queue, 0.2)
        self.store = JsonStore("app_state.json")
        root = Builder.load_file(kv_file)

        return root

    def on_start(self):

        first_run = False

        self.url_display = "http://127.0.0.1:9666"
        self.add_log("=== APP START ===")

        self.update_system_bars()
        self.check_and_prepare()

        if is_server_running():
            self.running = True
            self.button_text = "STOP"
            self.add_log("Server running OK")
        else:
            self.running = False
            self.button_text = "START"
            self.add_log("Server not running")

        if self.store.exists("app"):
            first_run = self.store.get("app").get("first_run", True)

        if first_run:
            Clock.schedule_once(lambda dt: self.show_permission_dialog(), 0.5)
            self.store.put("app", first_run=False)

    # -----------------------
    # 🔥 CHECK PERMISSION
    # -----------------------
    def check_and_prepare(self):
        try:
            self.setup_plugin_folder()

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

            if not self.check_and_prepare():
                return

            self.button_text = "STOP"
            self.add_log("\nServer START")

            Clock.schedule_once(lambda dt: check_plugins(self.add_log, self.add_error), 0)

            try:
                service = autoclass('org.pyserve.pyserve.ServiceServer')
                mActivity = autoclass('org.kivy.android.PythonActivity').mActivity
                service.start(mActivity, 'small_icon', 'PyServe', 'Server running...', '')
            except Exception as e:
                self.add_error(f"SERVICE START ERROR: {e}")
                return

            def check(dt):
                if is_server_running():
                    self.running = True
                    self.add_log("Server running OK")
                else:
                    self.running = False
                    self.button_text = "START"
                    self.add_error("Server failed")

            Clock.schedule_once(check, 2)

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
        except Exception as e:
            self.add_error(f"OPEN WEB ERROR: {e}")

    # -----------------------
    # 📂 DRAWER ACTIONS
    # -----------------------
    def open_github(self):
        try:
            webbrowser.open("https://github.com/Saros72/PyServe")
        except Exception as e:
            self.add_error(f"GITHUB ERROR: {e}")

    def open_plugins(self):
        try:
            webbrowser.open("https://github.com/Saros72/PyServe-Plugins")
        except Exception as e:
            self.add_error(f"GITHUB ERROR: {e}")

    def send_email(self):
        try:
            webbrowser.open("mailto:ss72@seznam.cz")
        except Exception as e:
            self.add_error(f"EMAIL ERROR: {e}")

    def open_paypal(self):
        try:
            webbrowser.open("https://paypal.me/petrsarka")
            self.add_log("Opening PayPal.Me")
        except Exception as e:
            self.add_error(f"PAYPAL ERROR: {e}")

    def open_share(self):
        try:
            url = "https://github.com/Saros72/PyServe/releases/latest"
            share_text(str(url))
        except Exception as e:
            self.add_error(f"SHARE ERROR: {e}")


    # -----------------------
    # 🔑 PERMISSION DIALOG 
    # -----------------------
    def show_permission_dialog(self):

        self.dialog = MDDialog(
            title="Warning",
            text=(
                "This app runs a local server in a foreground service.\n"
                "To work properly, it requires access to all files.\n\n"
                "Allow access in system settings?"
            ),
            radius=[16, 16, 16, 16],
            buttons=[
                MDFlatButton(
                    text="LATER",
                    theme_text_color="Custom",
                    text_color=self.custom_blue,
                    on_release=lambda x: self.dialog.dismiss()
                ),
                MDRaisedButton(
                    text="ALLOW",
                    md_bg_color=self.custom_blue,
                    on_release=lambda x: self.allow_permissions()
                ),
            ],
        )
        self.dialog.ids.title.theme_text_color = "Custom"
        self.dialog.ids.title.text_color = [0.9, 0.2, 0.2, 1] 
        self.dialog.ids.text.theme_text_color = "Custom"
        self.dialog.ids.text.text_color = [0, 0, 0, 1]

        self.dialog.open()

    # -----------------------
    # OPEN SETTINGS
    # -----------------------
    def allow_permissions(self):
        self.dialog.dismiss()
        open_all_files_permission()


if __name__ == "__main__":
    App().run()