import customtkinter as ctk
import streamlit.web.bootstrap as bootstrap
import sys
import os
import threading
import webbrowser
from PIL import Image
import pystray
from pystray import MenuItem as item

class DiaryDesktopApp:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("AI Diary Assistant")
        self.root.geometry("1200x800")
        
        # Set theme
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create system tray icon
        self.setup_tray()
        
        # Create main frame
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Add title
        self.title = ctk.CTkLabel(
            self.main_frame, 
            text="AI Diary Assistant",
            font=("Helvetica", 24, "bold")
        )
        self.title.pack(pady=20)
        
        # Start Streamlit thread
        self.streamlit_thread = threading.Thread(target=self.run_streamlit, daemon=True)
        self.streamlit_thread.start()
        
        # Add embedded web view (opens default browser for now)
        self.start_button = ctk.CTkButton(
            self.main_frame,
            text="Open Diary",
            command=self.open_diary
        )
        self.start_button.pack(pady=20)

    def run_streamlit(self):
        bootstrap.run(
            file=os.path.join(os.path.dirname(__file__), "app.py"),
            command_line=[],
            args=[],
            flag_options={},
        )

    def open_diary(self):
        webbrowser.open("http://localhost:8501")

    def setup_tray(self):
        image = Image.open("assets/icon.png")
        menu = (
            item('Open', self.open_diary),
            item('Quit', self.quit_app)
        )
        self.icon = pystray.Icon("AI Diary", image, "AI Diary Assistant", menu)
        self.tray_thread = threading.Thread(target=self.icon.run, daemon=True)
        self.tray_thread.start()

    def quit_app(self):
        self.icon.stop()
        self.root.quit()

    def run(self):
        self.root.mainloop()

if __name__ == "__main__":
    app = DiaryDesktopApp()
    app.run() 