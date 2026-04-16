import os
import importlib.util
import traceback

# 📂 Plugin root
PLUGIN_DIR = "/storage/emulated/0/PyServe"

# 🧠 cache of loaded plugins
loaded_plugins = set()


# -----------------------
# PLUGIN CHECK
# -----------------------
def check_plugins(log_func, error_func):

    log_func("=== PLUGIN CHECK ===")

    try:
        folders = os.listdir(PLUGIN_DIR)
    except Exception as e:
        log_func(f"PLUGIN ACCESS ERROR: {e}")
        return

    for folder in folders:
        plugin_path = os.path.join(PLUGIN_DIR, folder)

        if not os.path.isdir(plugin_path):
            continue

        main_file = os.path.join(plugin_path, "main.py")

        if not os.path.exists(main_file):
            main_file = os.path.join(plugin_path, "default.py")

        if not os.path.exists(main_file):
            log_func(f"{folder}: no entry file")
            continue

        try:
            spec = importlib.util.spec_from_file_location(folder, main_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            log_func(f"{folder}: OK")

        except Exception as e:
            # UI krátké
            error_func(f"{folder}: ERROR")

            tb = traceback.extract_tb(e.__traceback__)

            file_info = ""
            if tb:
                last = tb[-1]
                file_info = f'File "{last.filename}", line {last.lineno}, in {last.name}'

            try:
                with open("/storage/emulated/0/PyServe/error_log.txt", "a", encoding="utf-8") as f:
                    f.write("\n" + "=" * 40 + "\n")
                    f.write(f"PLUGIN: {folder}\n")
                    f.write(f"{file_info}\n")
                    f.write(f"ERROR: {str(e)}\n")
            except:
                pass


# -----------------------
# PLUGIN LOADER
# -----------------------
def load_plugins(app):
    print(f"🔌 Loading plugins from: {PLUGIN_DIR}")

    try:
        folders = os.listdir(PLUGIN_DIR)
    except Exception as e:
        print(f"❌ PLUGIN LOAD ERROR: {e}")
        return

    for folder in folders:
        plugin_path = os.path.join(PLUGIN_DIR, folder)

        if not os.path.isdir(plugin_path):
            continue

        # 🔥 entry file resolve
        main_file = os.path.join(plugin_path, "main.py")
        if not os.path.exists(main_file):
            main_file = os.path.join(plugin_path, "default.py")

        if not os.path.exists(main_file):
            print(f"⚠️ No entry script in plugin: {folder}")
            continue

        if folder in loaded_plugins:
            print(f"⚠️ Plugin already loaded: {folder}")
            continue

        try:
            spec = importlib.util.spec_from_file_location(folder, main_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            # 🔥 plugin init
            if hasattr(module, "register"):
                module.register(app)
                loaded_plugins.add(folder)
                print(f"✅ Loaded plugin: {folder}")
            else:
                print(f"⚠️ Plugin {folder} has no register()")

        except Exception as e:
            print(f"❌ Plugin error: {folder}")
            print(traceback.format_exc())

            try:
                with open("/storage/emulated/0/PyServe/error_log.txt", "a", encoding="utf-8") as f:
                    f.write("\n" + "=" * 40 + "\n")
                    f.write(f"PLUGIN LOAD ERROR: {folder}\n")
                    f.write(f"ERROR: {str(e)}\n")
                    f.write(traceback.format_exc())
            except:
                pass