# AI Diary Assistant

一個智能日記助手，幫助你記錄生活，分析情緒，提供建議。

## 安裝說明

### 系統需求
- Windows 7/10/11
- Python 3.8 或更新版本
- 網路連接
- Google API 金鑰（用於 AI 功能）

### 安裝步驟

1. **安裝 Python**
   - 從 [Python 官網](https://www.python.org/downloads/) 下載並安裝 Python 3.8 或更新版本
   - 安裝時請務必勾選 "Add Python to PATH" 選項
   - 安裝完成後，可以在命令提示字元中輸入 `python --version` 確認安裝成功

2. **下載專案**
   - 點擊 GitHub 頁面上的 "Code" 按鈕
   - 選擇 "Download ZIP"
   - 解壓縮下載的檔案到你想要的位置

3. **設定 API 金鑰**
   - 在專案根目錄建立 `.env` 文件
   - 在檔案中添加你的 Google API 金鑰：
     ```
     GOOGLE_API_KEY=your_api_key_here
     ```
   - 將 `your_api_key_here` 替換為你的實際 API 金鑰

4. **啟動應用程式**
   - 雙擊 `start_diary.bat`
   - 首次啟動時會自動設置 Python 環境並安裝必要套件
   - 等待安裝完成後，應用程式會自動在瀏覽器中開啟

### 常見問題

1. **找不到 Python**
   - 確認 Python 已正確安裝
   - 確認安裝時有勾選 "Add Python to PATH"
   - 重新啟動電腦後再試一次

2. **無法安裝套件**
   - 確認網路連接正常
   - 嘗試使用系統管理員權限執行
   - 檢查防火牆設定

3. **應用程式無法啟動**
   - 確認 `.env` 檔案存在且包含正確的 API 金鑰
   - 檢查錯誤訊息
   - 確認所有必要套件都已正確安裝

### 聯絡支援

如果遇到任何問題，請：
1. 檢查上述常見問題解答
2. 在 GitHub Issues 頁面回報問題
3. 提供詳細的錯誤訊息和系統資訊

## 使用說明

## Features

- AI-powered diary responses using Google's Gemini API
- Bilingual support (English/Chinese)
- Multi-platform support (Desktop & Mobile)
- Image upload and analysis
- Chat-like interface
- Secure local storage of entries

## Desktop App (Windows & macOS)

### Requirements

- Python 3.8 or higher
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-diary-assistant.git
cd ai-diary-assistant
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up your environment variables:
Create a `.env` file in the project root and add:
```
GOOGLE_API_KEY=your_api_key_here
```

### Running the Desktop App

Run the desktop application:
```bash
python desktop_app.py
```

### Building Desktop Executables

To create standalone executables:
```bash
python build.py
```

The built application will be in the `dist` directory.

## Mobile App (iOS & Android)

### Requirements

- Flutter SDK
- Android Studio / Xcode
- Flutter development environment setup

### Building the Mobile App

1. Navigate to the mobile app directory:
```bash
cd mobile_app
```

2. Get Flutter dependencies:
```bash
flutter pub get
```

3. Build for your platform:

For Android:
```bash
flutter build apk
```

For iOS:
```bash
flutter build ios
```

## Development

### Project Structure

```
ai-diary-assistant/
├── app.py                 # Main Streamlit application
├── desktop_app.py         # Desktop application wrapper
├── diary_entry.py         # Diary entry class
├── diary_manager.py       # Diary management system
├── diary_responder.py     # AI response handler
├── requirements.txt       # Python dependencies
├── assets/               # Application assets
└── mobile_app/          # Flutter mobile application
```

### Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Built with Streamlit
- Powered by Google Gemini API
- Cross-platform support with CustomTkinter and Flutter 