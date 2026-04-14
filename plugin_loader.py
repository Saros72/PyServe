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

    if not os.path.exists(PLUGIN_DIR):
        error_func("Plugin directory not found")
        return

    # 🔥 OŠETŘENÍ PERMISSION
    try:
        folders = os.listdir(PLUGIN_DIR)
    except PermissionError:
        error_func("No permission to access plugin directory")
        return
    except Exception as e:
        error_func(f"PLUGIN ACCESS ERROR: {e}")
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
            # UI jen krátce
            error_func(f"{folder}: ERROR")

            # FILE log jen čisté info
            try:
                with open("/storage/emulated/0/PyServe/error_log.txt", "a", encoding="utf-8") as f:
                    f.write("\n" + "=" * 40 + "\n")
                    f.write(f"PLUGIN: {folder}\n")
                    f.write(f"FILE: {main_file}\n")
                    f.write(f"ERROR: {str(e)}\n")
            except:
                pass


# -----------------------
# PLUGIN LOADER
# -----------------------
def load_plugins(app):
    print(f"🔌 Loading plugins from: {PLUGIN_DIR}")

    if not os.path.exists(PLUGIN_DIR):
        print("❌ Plugin directory not found")
        return

    # 🔥 OŠETŘENÍ PERMISSION
    try:
        folders = os.listdir(PLUGIN_DIR)
    except PermissionError:
        print("❌ No permission to access plugin directory")
        return
    except Exception as e:
        print(f"❌ PLUGIN ACCESS ERROR: {e}")
        return

    for folder in folders:
        plugin_path = os.path.join(PLUGIN_DIR, folder)

        if not os.path.isdir(plugin_path):
            continue

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

            if hasattr(module, "register"):
                module.register(app)
                loaded_plugins.add(folder)
                print(f"✅ Loaded plugin: {folder}")
            else:
                print(f"⚠️ Plugin {folder} has no register()")

        except Exception as e:
            print(f"❌ Plugin error: {folder}")
            print(traceback.format_exc())

            # log i do souboru
            try:
                with open("/storage/emulated/0/PyServe/error_log.txt", "a", encoding="utf-8") as f:
                    f.write("\n" + "=" * 40 + "\n")
                    f.write(f"PLUGIN LOAD ERROR: {folder}\n")
                    f.write(f"ERROR: {str(e)}\n")
                    f.write(traceback.format_exc())
            except:
                pass