# AI Diary Assistant

A cross-platform AI-powered diary assistant that helps you reflect on your thoughts and experiences.

## 🚀 Quick Start (一鍵安裝)

### Windows 使用者
1. 下載並安裝 [Python 3.8+](https://www.python.org/downloads/) (安裝時請勾選 "Add Python to PATH")
2. 下載此專案:
```bash
git clone https://github.com/yourusername/ai-diary-assistant.git
cd ai-diary-assistant
```
3. 雙擊執行 `start_diary.bat`

### Mac/Linux Users
1. Install Python 3.8+ if not installed
2. Run these commands:
```bash
git clone https://github.com/yourusername/ai-diary-assistant.git
cd ai-diary-assistant
chmod +x start_diary.sh  # Make script executable
./start_diary.sh
```

### 🔑 API Key Setup (API 金鑰設置)

#### 取得 API 金鑰 / Get API Key
1. 前往 [Google AI Studio](https://makersuite.google.com/app/apikey)
2. 登入 Google 帳號
3. 點擊 "Create API key" 按鈕
4. 複製生成的 API 金鑰

#### 設置 API 金鑰 / Setup API Key
1. 在專案資料夾中建立 `.env` 檔案
2. 將以下內容加入 `.env` 檔案（替換為您的 API 金鑰）:
```
GOOGLE_API_KEY=your_api_key_here
```

注意：
- API 金鑰請保密，不要分享給他人
- 首次使用時需要設定 API 金鑰
- 設定完成後程式會自動記住，不需要重複設定

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