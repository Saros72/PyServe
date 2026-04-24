from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.core.window import Window
from kivymd.utils.set_bars_colors import set_bars_colors
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDFlatButton, MDRaisedButton
from kivymd.toast import toast
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
ERROR_LOG_FILE = os.path.join(BASE_DIR, "app_log.txt")


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
def open_app_details():
    activity = PythonActivity.mActivity
    intent = Intent(Settings.ACTION_APPLICATION_DETAILS_SETTINGS)
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

    dialog = None
    back_pressed_once = False

    LOG_SCROLL_STEP = 0.06

    def build(self):
        self.log_buffer = []
        self.log_queue = []

        Clock.schedule_interval(self._process_log_queue, 0.2)


        # -----------------------
        # TV / MOBILE
        # -----------------------
        self.is_tv = False

        try:
            UiModeManager = autoclass('android.app.UiModeManager')
            Context = autoclass('android.content.Context')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')

            context = PythonActivity.mActivity
            ui_mode = context.getSystemService(Context.UI_MODE_SERVICE)

            # TV mode = 4
            if ui_mode.getCurrentModeType() == 4:
                self.is_tv = True
        except:
            self.is_tv = False

        kv_file = "ui/layout_tv.kv" if self.is_tv else "ui/layout.kv"

        root = Builder.load_file(kv_file)

        # 👉 TV / GAMEPAD
        Window.bind(on_key_down=self._on_keyboard)
        Window.bind(on_key_up=self._on_keyboard_up)
        Window.bind(on_joy_button_down=self._on_joy)

        return root

    def on_start(self):

        self.url_display = f"http://{get_ip()}:9666" if self.is_tv else "http://127.0.0.1:9666"
        self.add_log("=== APP START ===")

        self.update_system_bars()
        if not self.check_and_prepare():
            Clock.schedule_once(lambda dt: self.show_permission_dialog(), 1)

        if is_server_running():
            self.running = True
            self.button_text = "STOP"
            self.add_log("Server running OK")
        else:
            self.running = False
            self.button_text = "START"
            self.add_log("Server not running")

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
    # 🎮 TV / REMOTE CONTROL
    # -----------------------
    def _trigger_button(self):

        if hasattr(self, "root") and self.root:
            try:
                btn = self.root.ids.start_button

                normal_color = btn.md_bg_color[:]

                btn.md_bg_color = [
                    max(0, c * 0.65) for c in normal_color[:3]
                ] + [1]

                def release(dt):
                    btn.trigger_action(duration=0.1)

                    def reset_color(dt2):
                        btn.md_bg_color = normal_color

                    Clock.schedule_once(reset_color, 0.1)

                Clock.schedule_once(release, 0.05)
                return

            except Exception as e:
                print(f"Error trigger: {e}")

        # fallback
        self.toggle_server()

    def reset_back_button(self, dt):
        self.back_pressed_once = False

    def _on_keyboard(self, window, key, scancode, codepoint, modifiers):
        if key == 27:  # Back button
            if self.dialog and self.dialog.parent:
                self.dialog.dismiss()
                return True
            
            if not self.back_pressed_once:
                self.back_pressed_once = True
                toast("Press back again to exit")
                Clock.schedule_once(self.reset_back_button, 2)
                return True
            if self.running:
                toast("Server continues running in background")
            return False

        if key in (13, 271, 23):
            return True
        return False

    def _on_keyboard_up(self, window, key, scancode):
        if key in (13, 271, 23, 1073741943):
            if self.dialog and self.dialog.parent:
                self.allow_permissions()
            else:
                self._trigger_button()
            return True
        return False

    def _on_joy(self, window, stick_id, button_id):
        # OK Gamepad
        if button_id in (0, 96, 23):
            if self.dialog and self.dialog.parent:
                self.allow_permissions()
            else:
                self._trigger_button()
            return True

        if button_id == 4:  # Back button
            if self.dialog and self.dialog.parent:
                self.dialog.dismiss()
                return True
            
            if not self.back_pressed_once:
                self.back_pressed_once = True
                toast("Press back again to exit")
                Clock.schedule_once(self.reset_back_button, 2)
            else:
                if self.running:
                    toast("Server continues running in background")
                Clock.schedule_once(lambda dt: self.stop(), 0.5)
                return True
            return False

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
            webbrowser.open(self.url_display + "/demo")
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
        # 1. Definujeme tlačítko ALLOW (to tam je vždy)
        allow_button = MDRaisedButton(
            text="ALLOW",
            md_bg_color=self.custom_blue,
            on_release=lambda x: self.allow_permissions()
        )

        # 2. Rozhodneme, jaká tlačítka se zobrazí
        if self.is_tv:
            # Pro TV režim jen jedno tlačítko
            buttons_to_show = [allow_button]
        else:
            # Pro mobil/jiné režimy dvě tlačítka (LATER a ALLOW)
            later_button = MDFlatButton(
                text="LATER",
                theme_text_color="Custom",
                text_color=self.custom_blue,
                on_release=lambda x: self.dialog.dismiss()
            )
            buttons_to_show = [later_button, allow_button]

        # 3. Vytvoříme dialog s dynamickým seznamem tlačítek
        self.dialog = MDDialog(
            title="Warning",
            text=(
                "This app runs a local server in a foreground service.\n"
                "To work properly, it requires access to all files.\n\n"
                "Allow access in system settings?"
            ),
            radius=[16, 16, 16, 16],
            buttons=buttons_to_show, # Použijeme připravený seznam
        )

        # 4. Styling (zůstává stejný)
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
        if self.is_tv:
            open_app_details()
        else:
            open_all_files_permission()


if __name__ == "__main__":
    App().run()
