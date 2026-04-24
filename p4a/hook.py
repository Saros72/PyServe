import os
from pathlib import Path
from pythonforandroid.toolchain import ToolchainCL

def after_apk_build(toolchain: ToolchainCL):
    manifest_file = Path(toolchain._dist.dist_dir) / "src" / "main" / "AndroidManifest.xml"
    
    if not manifest_file.exists():
        return

    content = manifest_file.read_text(encoding="utf-8")

    # 1. Přidání LEANBACK_LAUNCHER (pro zobrazení v TV menu)
    if 'android.intent.category.LEANBACK_LAUNCHER' not in content:
        content = content.replace(
            '<category android:name="android.intent.category.LAUNCHER" />',
            '<category android:name="android.intent.category.LAUNCHER" />\n                <category android:name="android.intent.category.LEANBACK_LAUNCHER" />'
        )
        
    # 2. Nastavení VLASTNÍHO BANNERU
    # Místo @drawable/presplash teď ukážeme na tvůj @drawable/banner
    if 'android:banner' not in content:
        content = content.replace(
            '<activity ',
            '<activity android:banner="@drawable/tv_banner" '
        )
    
    manifest_file.write_text(content, encoding="utf-8")
    print("============================================== HOOK: Banner nastaven na @drawable/banner")
