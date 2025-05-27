import PyInstaller.__main__
import os
import shutil
import sys

def build_app():
    # Clean previous builds
    if os.path.exists("dist"):
        shutil.rmtree("dist")
    if os.path.exists("build"):
        shutil.rmtree("build")

    # Determine platform-specific settings
    if sys.platform == "win32":
        icon_file = "assets/icon.ico"
        output_name = "AI Diary Assistant.exe"
    else:  # macOS
        icon_file = "assets/icon.icns"
        output_name = "AI Diary Assistant"

    # PyInstaller arguments
    args = [
        "desktop_app.py",
        "--name", output_name,
        "--icon", icon_file,
        "--windowed",
        "--onefile",
        "--add-data", f"assets{os.pathsep}assets",
        "--hidden-import", "streamlit",
        "--hidden-import", "google.generativeai",
    ]

    # Add platform specific arguments
    if sys.platform == "win32":
        args.extend([
            "--add-binary", f"{os.path.dirname(sys.executable)}\\tcl86t.dll{os.pathsep}.",
            "--add-binary", f"{os.path.dirname(sys.executable)}\\tk86t.dll{os.pathsep}.",
        ])

    # Run PyInstaller
    PyInstaller.__main__.run(args)

if __name__ == "__main__":
    build_app() 