import streamlit as st
import os
from datetime import datetime
from PIL import Image
from dotenv import load_dotenv
import glob
import time

from diary_models import DiaryEntry, DiaryManager
from diary_responder import DiaryResponder
from environment import EnvironmentManager

# Set page config must be the first Streamlit command
st.set_page_config(
    page_title="AI Diary Assistant",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better UI
st.markdown("""
<style>
    /* Main container and background */
    .main > div {
        max-width: 1000px;
        padding-top: 0.5rem;
    }
    
    .stApp {
        background: linear-gradient(135deg, #f5f7fa 0%, #e3eeff 100%);
        background-attachment: fixed;
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Chat messages */
    .user-message, .assistant-message {
        color: white;
        padding: 15px;
        margin: 10px 0;
        max-width: 75%;
        clear: both;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        font-size: 16px;
        line-height: 1.5;
    }
    
    .user-message {
        background: linear-gradient(135deg, #4C84FF 0%, #3366FF 100%);
        border-radius: 20px 20px 0 20px;
        float: right;
    }
    
    .assistant-message {
        background: linear-gradient(135deg, #FF6B6B 0%, #FF4F4F 100%);
        border-radius: 20px 20px 20px 0;
        float: left;
    }
    
    /* Message metadata */
    .message-timestamp {
        font-size: 0.8em;
        opacity: 0.8;
        margin-bottom: 5px;
    }
    
    /* Input and buttons */
    .stTextInput > div > div > input {
        border-radius: 25px !important;
        padding: 12px 20px !important;
        font-size: 16px !important;
        border: 2px solid #4C84FF !important;
        background: white !important;
    }
    
    .stButton > button {
        border-radius: 25px !important;
        padding: 10px 25px !important;
        background: linear-gradient(135deg, #4C84FF 0%, #6B9FFF 100%) !important;
        color: white !important;
        border: none !important;
        transition: transform 0.2s !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
    }
    
    /* Content cards */
    .content-card {
        background: white;
        border-radius: 15px;
        padding: 1rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* Headers */
    h1 {
        background: linear-gradient(135deg, #4C84FF 0%, #FF6B6B 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.2rem !important;
        margin-bottom: 1.5rem !important;
    }
    
    /* Expander and date input */
    .streamlit-expanderHeader {
        background: white !important;
        border-radius: 10px !important;
    }
    
    .stDateInput > div > div > input {
        border-radius: 10px !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize components with better error handling
@st.cache_resource(show_spinner=False)
def init_components():
    """Initialize diary components with caching for better performance"""
    try:
        # First initialize diary manager
        diary_manager = DiaryManager()
        
        # Check for API key before initializing responder
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            st.error("🔑 Google API key not found. Please set GOOGLE_API_KEY in your .env file.")
            return None, None
            
        # Initialize responder with gentler validation
        try:
            responder = DiaryResponder()
            return diary_manager, responder
        except Exception as e:
            st.error(f"❌ Failed to initialize AI responder: {str(e)}")
            print(f"Responder initialization error: {e}")
            return None, None
            
    except Exception as e:
        st.error(f"❌ Failed to initialize components: {str(e)}")
        print(f"Component initialization error: {e}")
        return None, None

# Load environment variables first
load_dotenv()

# Initialize components with better error messages
diary_manager, claude_responder = init_components()

if not diary_manager or not claude_responder:
    st.error("""
    ⚠️ Application initialization failed. Please check:
    1. Your .env file exists and contains GOOGLE_API_KEY
    2. Your internet connection is stable
    3. Your API key is valid
    
    Try restarting the application after fixing these issues.
    """)
    st.stop()

# Initialize session state with better organization
def init_session_state(lang):
    """Initialize session state variables if they don't exist"""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "user_input" not in st.session_state:
        st.session_state.user_input = ""
    if "ai_name" not in st.session_state:
        st.session_state.ai_name = "AI助手" if lang == "中文" else "AI Assistant"

# Language settings
LANGUAGES = {
    "中文": {
        "title": "AI 日記助手",
        "new_entry": "✏️ 聊天模式",
        "browse": "📖 瀏覽日記",
        "how_feel": "今天心情如何？",
        "share_feeling": "分享你的心情...",
        "what_happened": "今天發生了什麼事？有什麼感受？",
        "upload_photos": "上傳照片（可多選）",
        "upload_files": "上傳檔案（可多選）",
        "submit": "送出",
        "thinking": "AI助手正在思考回覆...",
        "saved": "對話已儲存！",
        "ai_response": "AI助手",
        "please_input": "請輸入一些內容！",
        "diary_review": "日記回顧",
        "start_date": "開始日期",
        "end_date": "結束日期",
        "original": "原始內容",
        "attached_photos": "附加圖片",
        "no_entries": "在選擇的日期範圍內沒有找到日記。",
        "clear_chat": "清除對話",
        "save_chat": "儲存對話",
        "customize_ai": "自訂AI助手名稱",
        "current_ai_name": "目前AI助手名稱",
        "enter_ai_name": "輸入新的AI助手名稱"
    },
    "English": {
        "title": "AI Diary Assistant",
        "new_entry": "💭 Chat Mode",
        "browse": "📖 Browse Entries",
        "how_feel": "How are you feeling today? ✨",
        "share_feeling": "Share your thoughts and feelings...",
        "what_happened": "Tell me about your day... I'm here to listen 💫",
        "upload_photos": "📸 Add Photos (Multiple)",
        "upload_files": "📎 Add Files (Multiple)",
        "submit": "Send",
        "thinking": "✨ AI Assistant is thinking...",
        "saved": "✅ Chat saved successfully!",
        "ai_response": "AI Friend",
        "please_input": "Please share your thoughts...",
        "diary_review": "📖 Your Diary Entries",
        "start_date": "From Date",
        "end_date": "To Date",
        "original": "Your Entry",
        "attached_photos": "Your Photos",
        "no_entries": "No diary entries found in this date range. Start writing! ✨",
        "clear_chat": "New Chat",
        "save_chat": "Save Entry",
        "customize_ai": "✨ Customize AI Friend's Name",
        "current_ai_name": "Current Name",
        "enter_ai_name": "Choose a new name for your AI friend"
    }
}

# Language selection in sidebar
lang = st.sidebar.selectbox("Language / 語言", list(LANGUAGES.keys()))
txt = LANGUAGES[lang]

# Initialize session state after language selection
init_session_state(lang)

def submit_message():
    if st.session_state.user_input.strip():
        try:
            # Process images
            image_paths = []
            if st.session_state.get("chat_images"):
                save_dir = "uploaded_images"
                os.makedirs(save_dir, exist_ok=True)
                
                for img in st.session_state.chat_images:
                    image_path = os.path.join(save_dir, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{img.name}")
                    with open(image_path, "wb") as f:
                        f.write(img.getbuffer())
                    image_paths.append(image_path)
            
            # Add user message to chat history
            st.session_state.chat_history.append({
                "role": "user",
                "content": st.session_state.user_input,
                "images": image_paths if image_paths else None,
                "timestamp": datetime.now()
            })
            
            # Get the current language
            current_lang = "en" if lang == "English" else "zh"
            
            # Get AI response
            with st.spinner(txt["thinking"]):
                # Try to get main response
                retry_count = 0
                max_retries = 2
                success = False
                
                while retry_count < max_retries and not success:
                    try:
                        # Get main response
                        claude_response = claude_responder.get_response(st.session_state.user_input, current_lang)
                        
                        if claude_response and "issues" not in claude_response.lower():
                            # Try to get follow-up questions if we have a valid response
                            try:
                                if len(st.session_state.chat_history) >= 2:
                                    followup_questions = claude_responder.suggest_followup_questions(
                                        claude_responder.conversation.history,
                                        current_lang
                                    )
                                    
                                    # Add follow-up questions if available
                                    if followup_questions:
                                        questions_text = "\n\n" + "\n".join([f"• {q}" for q in followup_questions])
                                        claude_response += questions_text
                            except Exception as e:
                                print(f"Error getting follow-up questions: {e}")
                            
                            # Add AI response to chat history
                            st.session_state.chat_history.append({
                                "role": "assistant",
                                "content": claude_response,
                                "timestamp": datetime.now()
                            })
                            success = True
                        else:
                            retry_count += 1
                            if retry_count < max_retries:
                                time.sleep(1)  # Short pause before retry
                    except Exception as e:
                        print(f"Error in response attempt {retry_count + 1}: {e}")
                        retry_count += 1
                        if retry_count < max_retries:
                            time.sleep(1)
                
                if not success:
                    error_msg = "AI助手暂时需要休息，请稍后再试。" if current_lang == "zh" else "The AI assistant needs a brief rest. Please try again shortly."
                    st.error(error_msg)
            
            # Clear the input
            st.session_state.user_input = ""
            
        except Exception as e:
            print(f"Error in submit_message: {e}")
            error_msg = "发生错误，请重试。" if lang == "中文" else "An error occurred. Please try again."
            st.error(error_msg)

# Add restart button
if st.sidebar.button("🔄 重新啟動 / Restart"):
    st.rerun()

# Add AI Assistant name customization in sidebar
with st.sidebar.expander(txt["customize_ai"]):
    st.text(f"{txt['current_ai_name']}: {st.session_state.ai_name}")
    new_ai_name = st.text_input(txt["enter_ai_name"])
    if new_ai_name:
        st.session_state.ai_name = new_ai_name
        st.rerun()

# Sidebar for navigation
page = st.sidebar.radio(txt["title"], [txt["new_entry"], txt["browse"]])

if page == txt["new_entry"]:
    st.title(txt["how_feel"])
    
    # Chat container with optimized layout
    with st.container():
        # Display chat history
        if st.session_state.chat_history:
            st.markdown('<div class="content-card" style="background: rgba(255,255,255,0.8);">', unsafe_allow_html=True)
            for message in st.session_state.chat_history:
                message_time = datetime.now().strftime("%H:%M")
                
                if message["role"] == "user":
                    st.markdown(f"""
                    <div class="user-message">
                        <div class="message-timestamp">{message_time}</div>
                        <div style="margin-bottom: 5px;"><strong>You</strong> ✨</div>
                        {message['content']}
                    </div>
                    <div style="clear: both;"></div>
                    """, unsafe_allow_html=True)
                    
                    if message.get("images"):
                        cols = st.columns(min(3, len(message["images"])))
                        for idx, img_path in enumerate(message["images"]):
                            if os.path.exists(img_path):
                                with cols[idx % 3]:
                                    st.image(img_path, use_column_width=True)
                else:
                    st.markdown(f"""
                    <div class="assistant-message">
                        <div class="message-timestamp">{message_time}</div>
                        <div style="margin-bottom: 5px;"><strong>{st.session_state.ai_name}</strong> 🌟</div>
                        {message['content']}
                    </div>
                    <div style="clear: both;"></div>
                    """, unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Compact input area
        with st.container():
            st.markdown('<div class="content-card" style="background: white; margin-top: 0.5rem;">', unsafe_allow_html=True)
            
            # File uploader in compact expander
            with st.expander("📎 " + txt["upload_photos"], expanded=False):
                st.file_uploader(
                    txt["upload_photos"],
                    type=["jpg", "jpeg", "png"],
                    accept_multiple_files=True,
                    key="chat_images",
                    label_visibility="collapsed"
                )
            
            # Input and send button
            col1, col2 = st.columns([4.8,1.2])
            with col1:
                st.text_input(
                    txt["share_feeling"],
                    key="user_input",
                    placeholder=txt["what_happened"],
                    on_change=submit_message,
                    label_visibility="collapsed"
                )
            with col2:
                st.button(
                    "✨ " + txt["submit"],
                    on_click=submit_message,
                    type="primary",
                    use_container_width=True
                )
            
            # Action buttons
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ " + txt["clear_chat"], type="secondary", use_container_width=True):
                    st.session_state.chat_history = []
                    st.rerun()
            with col2:
                if st.button("💫 " + txt["save_chat"], type="primary", use_container_width=True) and st.session_state.chat_history:
                    # Save entire chat as one diary entry
                    full_content = "\n\n".join([
                        f"{'You' if msg['role'] == 'user' else st.session_state.ai_name}: {msg['content']}"
                        for msg in st.session_state.chat_history
                    ])
                    
                    # Get the last AI response
                    last_ai_response = next(
                        (msg["content"] for msg in reversed(st.session_state.chat_history)
                         if msg["role"] == "assistant"),
                        ""
                    )
                    
                    # Get all image paths from the chat
                    all_images = []
                    for msg in st.session_state.chat_history:
                        if msg.get("images"):
                            all_images.extend(msg["images"])
                    
                    # Create and save diary entry
                    entry = DiaryEntry(
                        timestamp=datetime.now(),
                        content=full_content,
                        claude_response=last_ai_response,
                        image_path=",".join(all_images) if all_images else None
                    )
                    diary_manager.add_entry(entry)
                    st.success(txt["saved"])
            st.markdown('</div>', unsafe_allow_html=True)

else:  # Browse page
    st.title(txt["diary_review"])
    
    # Date range selection
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(txt["start_date"])
    with col2:
        end_date = st.date_input(txt["end_date"])
    
    if start_date and end_date:
        # Convert to datetime
        start_dt = datetime.combine(start_date, datetime.min.time())
        end_dt = datetime.combine(end_date, datetime.max.time())
        
        # Get entries
        entries = diary_manager.get_entries_by_date_range(start_dt, end_dt)
        
        if entries:
            for entry in sorted(entries, key=lambda x: x.timestamp, reverse=True):
                with st.expander(f"📝 {entry.timestamp.strftime('%Y-%m-%d %H:%M')}"):
                    st.write(f"### {txt['original']}")
                    st.write(entry.content)
                    
                    # Display images if any
                    if entry.image_path:
                        st.write(f"### {txt['attached_photos']}")
                        image_paths = entry.image_path.split(",")
                        for img_path in image_paths:
                            if os.path.exists(img_path):
                                st.image(img_path, caption=os.path.basename(img_path), use_column_width=True)
        else:
            st.info(txt["no_entries"]) 