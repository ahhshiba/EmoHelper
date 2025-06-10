import customtkinter as ctk           # 現代化的 Tkinter 介面庫 / Modern Tkinter UI library
import streamlit.web.bootstrap as bootstrap  # Streamlit 網頁應用程式啟動器 / Streamlit web app bootstrap
import sys                               # 系統相關功能 / System-related functions
import os                                # 作業系統介面 / Operating system interface
import threading                         # 多執行緒支援 / Multi-threading support
import webbrowser                        # 網頁瀏覽器控制 / Web browser control
from PIL import Image                    # 圖片處理庫 / Image processing library
import pystray                          # 系統托盤圖示庫 / System tray icon library
from pystray import MenuItem as item    # 托盤選單項目 / Tray menu items

class DiaryDesktopApp:
    """
    AI 日記助手桌面應用程式
    AI Diary Assistant desktop application.
    
    這個類別結合了 CustomTkinter 桌面介面和 Streamlit 網頁應用程式，
    提供完整的桌面日記體驗，包含系統托盤功能。
    
    This class combines CustomTkinter desktop interface with Streamlit web app,
    providing a complete desktop diary experience with system tray functionality.
    """
    
    def __init__(self):
        """
        初始化桌面應用程式
        Initialize desktop application.
        
        設定主視窗、外觀主題、系統托盤圖示，並啟動 Streamlit 伺服器
        Set up main window, appearance theme, system tray icon, and start Streamlit server
        """
        # 建立主視窗使用 CustomTkinter
        # Create main window using CustomTkinter
        self.root = ctk.CTk()
        self.root.title("AI Diary Assistant")                    # 設定視窗標題 / Set window title
        self.root.geometry("1200x800")                          # 設定視窗大小 / Set window size
        
        # 設定外觀主題
        # Set appearance theme
        ctk.set_appearance_mode("dark")                          # 使用深色模式 / Use dark mode
        ctk.set_default_color_theme("blue")                     # 使用藍色主題 / Use blue theme
        
        # 建立系統托盤圖示
        # Create system tray icon
        self.setup_tray()
        
        # 建立主要框架容器
        # Create main frame container
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # 新增應用程式標題
        # Add application title
        self.title = ctk.CTkLabel(
            self.main_frame, 
            text="AI Diary Assistant",
            font=("Helvetica", 24, "bold")                       # 設定字體：Helvetica, 24px, 粗體 / Set font: Helvetica, 24px, bold
        )
        self.title.pack(pady=20)                                # 加入垂直間距 / Add vertical padding
        
        # 在背景執行緒中啟動 Streamlit 伺服器
        # Start Streamlit server in background thread
        self.streamlit_thread = threading.Thread(
            target=self.run_streamlit,                           # 執行目標函數 / Target function to run
            daemon=True                                          # 設為守護執行緒，主程式結束時自動結束 / Set as daemon thread
        )
        self.streamlit_thread.start()                           # 啟動執行緒 / Start the thread
        
        # 新增開啟日記的按鈕（目前開啟預設瀏覽器）
        # Add button to open diary (currently opens default browser)
        self.start_button = ctk.CTkButton(
            self.main_frame,
            text="Open Diary",                                   # 按鈕文字 / Button text
            command=self.open_diary                              # 點擊時執行的函數 / Function to execute on click
        )
        self.start_button.pack(pady=20)                         # 加入垂直間距 / Add vertical padding
        
        # 新增額外的控制按鈕
        # Add additional control buttons
        self.create_control_buttons()
    
    def create_control_buttons(self):
        """
        建立額外的控制按鈕
        Create additional control buttons.
        """
        # 建立按鈕框架
        # Create button frame
        button_frame = ctk.CTkFrame(self.main_frame)
        button_frame.pack(pady=20, fill="x")
        
        # 最小化到托盤按鈕
        # Minimize to tray button
        self.minimize_button = ctk.CTkButton(
            button_frame,
            text="Minimize to Tray",                             # 最小化到托盤 / Minimize to tray
            command=self.minimize_to_tray
        )
        self.minimize_button.pack(side="left", padx=10)
        
        # 重新載入 Streamlit 按鈕
        # Reload Streamlit button
        self.reload_button = ctk.CTkButton(
            button_frame,
            text="Reload Web App",                               # 重新載入網頁應用程式 / Reload web app
            command=self.reload_streamlit
        )
        self.reload_button.pack(side="left", padx=10)
        
        # 結束應用程式按鈕
        # Quit application button
        self.quit_button = ctk.CTkButton(
            button_frame,
            text="Quit",                                         # 結束 / Quit
            command=self.quit_app,
            fg_color="red",                                      # 紅色背景表示危險操作 / Red background for dangerous action
            hover_color="darkred"                                # 滑鼠懸停時的顏色 / Color when mouse hovers
        )
        self.quit_button.pack(side="right", padx=10)
    
    def run_streamlit(self):
        """
        在背景執行緒中執行 Streamlit 應用程式
        Run Streamlit application in background thread.
        
        使用 Streamlit 的 bootstrap 模組來啟動網頁伺服器，
        讓用戶可以透過瀏覽器與日記應用程式互動。
        
        Uses Streamlit's bootstrap module to start web server,
        allowing users to interact with diary app through browser.
        """
        try:
            # 啟動 Streamlit 伺服器
            # Start Streamlit server
            bootstrap.run(
                file=os.path.join(os.path.dirname(__file__), "app.py"),  # Streamlit 應用程式檔案路徑 / Streamlit app file path
                command_line=[],                                          # 命令列參數 / Command line arguments
                args=[],                                                  # 額外參數 / Additional arguments
                flag_options={},                                          # 旗標選項 / Flag options
            )
        except Exception as e:
            # 處理 Streamlit 啟動錯誤
            # Handle Streamlit startup errors
            print(f"Error starting Streamlit: {e}")
            # 可以在這裡新增錯誤對話框
            # Could add error dialog here
    
    def open_diary(self):
        """
        開啟日記網頁介面
        Open diary web interface.
        
        在預設瀏覽器中開啟本地 Streamlit 伺服器
        Opens local Streamlit server in default browser
        """
        try:
            # 在瀏覽器中開啟 Streamlit 應用程式
            # Open Streamlit app in browser
            webbrowser.open("http://localhost:8501")
        except Exception as e:
            # 處理瀏覽器開啟錯誤
            # Handle browser opening errors
            print(f"Error opening browser: {e}")
    
    def minimize_to_tray(self):
        """
        最小化應用程式到系統托盤
        Minimize application to system tray.
        """
        self.root.withdraw()                                    # 隱藏主視窗 / Hide main window
        print("應用程式已最小化到系統托盤 / Application minimized to system tray")
    
    def reload_streamlit(self):
        """
        重新載入 Streamlit 應用程式
        Reload Streamlit application.
        
        注意：這個功能需要重新啟動整個應用程式才能完全生效
        Note: This feature requires restarting the entire application to take full effect
        """
        print("重新載入 Streamlit... / Reloading Streamlit...")
        # 實際上重新載入 Streamlit 比較複雜，這裡只是示範
        # Actually reloading Streamlit is complex, this is just for demonstration
        webbrowser.open("http://localhost:8501")
    
    def restore_window(self):
        """
        從系統托盤恢復視窗
        Restore window from system tray.
        """
        self.root.deiconify()                                   # 顯示主視窗 / Show main window
        self.root.lift()                                        # 將視窗帶到最前面 / Bring window to front
        self.root.focus_force()                                 # 強制取得焦點 / Force focus
    
    def setup_tray(self):
        """
        設定系統托盤圖示和選單
        Set up system tray icon and menu.
        
        建立系統托盤圖示，讓用戶可以在背景執行應用程式，
        並透過右鍵選單進行基本操作。
        
        Creates system tray icon allowing users to run app in background
        and perform basic operations through right-click menu.
        """
        try:
            # 載入托盤圖示圖片
            # Load tray icon image
            icon_path = "assets/icon.png"
            if os.path.exists(icon_path):
                image = Image.open(icon_path)
            else:
                # 如果找不到圖示檔案，建立一個簡單的預設圖示
                # If icon file not found, create a simple default icon
                image = Image.new('RGB', (64, 64), color='blue')
                print(f"警告：找不到圖示檔案 {icon_path}，使用預設圖示 / Warning: Icon file {icon_path} not found, using default icon")
            
            # 建立托盤選單
            # Create tray menu
            menu = (
                item('Open Diary', self.open_diary),             # 開啟日記 / Open diary
                item('Show Window', self.restore_window),        # 顯示視窗 / Show window
                item('Minimize to Tray', self.minimize_to_tray), # 最小化到托盤 / Minimize to tray
                item('Quit', self.quit_app)                     # 結束程式 / Quit application
            )
            
            # 建立系統托盤圖示
            # Create system tray icon
            self.icon = pystray.Icon(
                "AI Diary",                                      # 圖示名稱 / Icon name
                image,                                           # 圖示圖片 / Icon image
                "AI Diary Assistant",                           # 工具提示文字 / Tooltip text
                menu                                             # 右鍵選單 / Right-click menu
            )
            
            # 在背景執行緒中執行托盤圖示
            # Run tray icon in background thread
            self.tray_thread = threading.Thread(
                target=self.icon.run, 
                daemon=True
            )
            self.tray_thread.start()
            
        except Exception as e:
            # 處理托盤設定錯誤
            # Handle tray setup errors
            print(f"Error setting up system tray: {e}")
            self.icon = None
    
    def on_closing(self):
        """
        處理視窗關閉事件
        Handle window closing event.
        
        當用戶點擊視窗的 X 按鈕時，不直接關閉程式，
        而是最小化到系統托盤。
        
        When user clicks window's X button, don't close program directly,
        but minimize to system tray instead.
        """
        self.minimize_to_tray()
    
    def quit_app(self):
        """
        完全結束應用程式
        Completely quit the application.
        
        停止所有執行緒並關閉程式
        Stop all threads and close program
        """
        print("正在關閉應用程式... / Shutting down application...")
        
        # 停止系統托盤圖示
        # Stop system tray icon
        if hasattr(self, 'icon') and self.icon:
            self.icon.stop()
        
        # 關閉主視窗
        # Close main window
        if self.root:
            self.root.quit()
            self.root.destroy()
        
        # 結束程式
        # Exit program
        sys.exit(0)
    
    def run(self):
        """
        啟動桌面應用程式主迴圈
        Start desktop application main loop.
        
        設定視窗關閉事件處理器並啟動 Tkinter 主迴圈
        Set up window closing event handler and start Tkinter main loop
        """
        # 設定視窗關閉時的處理方式
        # Set up window closing behavior
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 啟動 GUI 主迴圈
        # Start GUI main loop
        try:
            print("啟動 AI 日記助手... / Starting AI Diary Assistant...")
            self.root.mainloop()
        except KeyboardInterrupt:
            # 處理 Ctrl+C 中斷
            # Handle Ctrl+C interrupt
            print("\n收到中斷信號，正在關閉... / Received interrupt signal, shutting down...")
            self.quit_app()
        except Exception as e:
            # 處理其他執行時錯誤
            # Handle other runtime errors
            print(f"應用程式執行錯誤: {e} / Application runtime error: {e}")
            self.quit_app()

# 主程式進入點
# Main program entry point
if __name__ == "__main__":
    """
    應用程式啟動點
    Application startup point.
    
    建立並執行桌面應用程式實例
    Create and run desktop application instance
    """
    try:
        # 建立應用程式實例
        # Create application instance
        app = DiaryDesktopApp()
        
        # 執行應用程式
        # Run application
        app.run()
        
    except Exception as e:
        # 處理啟動錯誤
        # Handle startup errors
        print(f"應用程式啟動失敗: {e} / Application startup failed: {e}")
        sys.exit(1)
