import time
import threading
import html
import os

from bottle import Bottle
from plugin_loader import load_plugins

# 📂 ROOT
BASE_DIR = "/storage/emulated/0/PyServe"


# -----------------------
# APP
# -----------------------
app = Bottle()


# -----------------------
# HELPERS
# -----------------------
def safe_join(base, *paths):
    return os.path.normpath(os.path.join(base, *paths))


def is_hidden(name):
    return name == "__pycache__"


# -----------------------
# BROWSER
# -----------------------
@app.route('/')
@app.route('/browse')
@app.route('/browse/<path:path>')
def browse(path=""):

    if ".." in path:
        return "blocked"

    current = safe_join(BASE_DIR, path)

    if not os.path.exists(current):
        return "Not found"

    items = []

    try:
        entries = os.listdir(current)

        # folders first
        entries.sort(key=lambda x: (not os.path.isdir(os.path.join(current, x)), x.lower()))

        for name in entries:

            if is_hidden(name):
                continue

            full = os.path.join(current, name)
            rel = os.path.join(path, name).replace("\\", "/")

            if os.path.isdir(full):
                items.append(f"""
                <a class="row folder" href="/browse/{rel}">
                    <span class="icon">📁</span>
                    <span class="name">{name}</span>
                    <span class="arrow">›</span>
                </a>
                """)
            else:
                items.append(f"""
                <a class="row file" href="/file/{rel}">
                    <span class="icon">📄</span>
                    <span class="name">{name}</span>
                </a>
                """)

    except Exception as e:
        return f"Error: {e}"

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                margin: 0;
                background: #000;
                color: #fff;
                font-family: Arial, sans-serif;
            }}

            .path {{
                padding: 10px;
                font-size: 14px;
                color: #aaa;
                border-bottom: 1px solid #111;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
            }}

            .row {{
                display: flex;
                align-items: center;
                padding: 12px;
                text-decoration: none;
                color: #fff;
                border-bottom: 1px solid #111;
                font-size: 14px;
            }}

            .row:active {{
                background: #111;
            }}

            .icon {{
                width: 28px;
            }}

            .name {{
                flex: 1;
                overflow: hidden;
                text-overflow: ellipsis;
                white-space: nowrap;
            }}

            .arrow {{
                color: #777;
            }}

            .file {{
                color: #ddd;
            }}

            .folder {{
                color: #fff;
            }}
        </style>
    </head>

    <body>
        <div class="path">{"/" if not path else path}</div>
        {''.join(items)}
    </body>
    </html>
    """


# -----------------------
# FILE VIEWER (IMPORTANT FIX)
# -----------------------
@app.route('/file/<path:path>')
def view_file(path):

    if ".." in path:
        return "blocked"

    full = safe_join(BASE_DIR, path)

    if not os.path.exists(full):
        return "Not found"

    try:
        with open(full, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return f"Cannot open file: {e}"

    # 🔥 critical: preserve formatting + prevent HTML rendering
    content = html.escape(content)

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                margin: 0;
                background: #000;
                color: #fff;
                font-family: monospace;
            }}

            pre {{
                margin: 0;
                padding: 12px;
                white-space: pre;
                overflow-x: auto;
                font-size: 13px;
                line-height: 1.4;
            }}
        </style>
    </head>

    <body>
        <pre>{content}</pre>
    </body>
    </html>
    """


# -----------------------
# SERVER
# -----------------------
def start_server():
    load_plugins(app)
    app.run(host='0.0.0.0', port=9666, quiet=True)


if __name__ == '__main__':
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    while True:
        time.sleep(1)