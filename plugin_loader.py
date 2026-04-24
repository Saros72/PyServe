import os
import importlib.util
import traceback
import logging

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
            log_func(f"{folder}: ERROR")


# -----------------------
# PLUGIN LOADER
# -----------------------

plugin_log = logging.getLogger("PLUGINS")


def load_plugins(app):
    print(f"🔌 Loading plugins from: {PLUGIN_DIR}")
#    plugin_log.info("\n=== PLUGIN LOAD START ===")

    try:
        folders = os.listdir(PLUGIN_DIR)
    except Exception:
        print("❌ PLUGIN LOAD ERROR")
        plugin_log.error("PLUGIN ACCESS ERROR")
        return

    for folder in folders:
        plugin_path = os.path.join(PLUGIN_DIR, folder)

        if not os.path.isdir(plugin_path):
            continue

        main_file = os.path.join(plugin_path, "main.py")
        if not os.path.exists(main_file):
            main_file = os.path.join(plugin_path, "default.py")

        if not os.path.exists(main_file):
            print(f"⚠️ No entry: {folder}")
            plugin_log.warning(f"{folder}: no entry file")
            continue

        if folder in loaded_plugins:
            print(f"⚠️ Already loaded: {folder}")
            plugin_log.warning(f"{folder}: already loaded")
            continue

        try:
            spec = importlib.util.spec_from_file_location(folder, main_file)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if hasattr(module, "register"):
                module.register(app)
                loaded_plugins.add(folder)

                print(f"✅ Loaded: {folder}")
                plugin_log.info(f"{folder}: OK")
            else:
                print(f"⚠️ No register(): {folder}")
                plugin_log.warning(f"{folder}: no register()")

        except Exception as e:
            print(f"❌ Plugin error: {folder}")
            tb = traceback.extract_tb(e.__traceback__)

            if tb:
                last = tb[-1]
                file = os.path.basename(last.filename)
                line = last.lineno
                func = last.name
            else:
                file = "unknown"
                line = "?"

            plugin_log.error(f"{folder}: ERROR")
            plugin_log.error(f"{type(e).__name__}: {e}")
            plugin_log.error(f"{file}:{line} in {func}")