# PyServe 🚀
Android application with a local Python server and plugin system

---

## 📱 About

PyServe is an Android application that runs a local Python server (built with Bottle) directly on the device and allows dynamic loading of plugins.

It is designed as a lightweight mobile backend framework for testing, prototyping, and local API development.

---

## ⚙️ How it works

- The app starts a local server at: http://127.0.0.1:9666
- Backend is built using Bottle
- On startup, the application scans the plugin directory
- Each plugin is dynamically imported using Python import system
- Plugins can extend server functionality (routes, logic, APIs)

---

## 🔌 Plugin system

Plugins are located at:

/storage/emulated/0/PyServe/

Each plugin is a separate folder:

```
PyServe/
 ├── demo/
 │   └── default.py
 └── my_plugin/
     └── main.py
```

---

## 📦 Demo plugin

The application automatically creates a **demo plugin** on first launch.

- Located in: `/storage/emulated/0/PyServe/demo/`
- File: `default.py`

### 🌐 Demo endpoint

The demo plugin provides a basic example endpoint available at:

http://127.0.0.1:9666/demo

This allows you to immediately verify that the server is running correctly.

You can open it directly using the **web button inside the app**.

---

## 📦 Plugin structure

Each plugin must include:

1. Entry file:
- main.py (recommended)
- or default.py (fallback)

2. Optional function:

```python
def register(app):
    pass
```

This function is called when the plugin is loaded.

---

## 🧠 How plugin loading works

- The app scans the plugin directory
- Each folder is treated as a separate plugin
- Python files are loaded via importlib
- Plugin errors:
  - are shown in the UI log
  - are written to an error log file
  - do NOT crash the main application

---

## 🌐 Server

Runs locally at:
http://127.0.0.1:9666

Built using:
- Bottle (routing and API)
- Python standard library

---

## 📌 Allowed Python modules in plugins

You can use:

### ✔ Standard library
- json
- time
- os
- threading
- datetime

### ✔ Additional modules
- bs4
- websocket-client

### ✔ Server / networking
- bottle
- requests

---

## 📱 Android requirements

To ensure the app works correctly on Android:

### 🔐 Permissions
- You must allow **"All files access"**
- Required because plugins are stored in:
  `/storage/emulated/0/PyServe/`

### ⚙️ Foreground service
- Server runs as a **foreground service**
- Prevents Android killing it in background
- Persistent notification is shown while running

### 🔋 Battery optimization
- Disable battery optimization for best stability
- Otherwise Android may stop the server

---

## ⚠️ Important notes

- Plugins run in the same Python runtime as the app
- Broken plugin does NOT crash the server
- Errors are isolated and logged
- Intended for local development use only

---

## 📂 Project structure

```
PyServe/
 ├── main.py
 ├── plugin_loader.py
 ├── service.py (Bottle backend)
 ├── ui/
 │    └── layout.kv
 ├── assets/
 └── /storage/emulated/0/PyServe/
      ├── demo/
      └── plugins...
```

---

## 📱 Features

- Start / stop local server
- Plugin system with dynamic loading
- Error isolation per plugin
- UI logging system
- Android foreground service support
- Open local web interface

---

## 🧪 Example plugin

```python

def register(app):

    @route("/hello")
    def hello():
        return "Hello from plugin!"
```

---

## 🔥 Use cases

- Local API testing on Android
- Backend prototyping
- Plugin-based architecture experiments
- Offline server tools
- Learning Bottle and Python web servers
```
```