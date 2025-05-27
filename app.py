import streamlit as st
import os
from PIL import Image
from dotenv import load_dotenv
from diary_responder import DiaryResponder

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

    /* Custom button styles */
    .language-button {
        padding: 5px 10px;
        margin: 0 5px;
        border-radius: 15px;
        border: 2px solid #4C84FF;
        background: white;
        color: #4C84FF;
        cursor: pointer;
        transition: all 0.3s;
    }

    .language-button.active {
        background: #4C84FF;
        color: white;
    }

    /* Hide Streamlit's default button */
    .stButton {
        display: none;
    }

    /* Hide default submit button */
    [data-testid="stForm"] [data-testid="baseButton-secondary"] {
        display: none;
    }
</style>

<script>
    // JavaScript to handle Enter key press
    document.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            document.querySelector('button[kind="primary"]').click();
        }
    });
</script>
""", unsafe_allow_html=True)

# Initialize AI responder
@st.cache_resource(show_spinner=False)
def init_responder():
    """Initialize AI responder with caching for better performance"""
    try:
        # Check for API key before initializing responder
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            st.error("🔑 Google API key not found. Please set GOOGLE_API_KEY in your .env file.")
            return None
            
        # Initialize responder
        try:
            responder = DiaryResponder()
            return responder
        except Exception as e:
            st.error(f"❌ Failed to initialize AI responder: {str(e)}")
            return None
            
    except Exception as e:
        st.error(f"❌ Failed to initialize components: {str(e)}")
        return None

# Load environment variables
load_dotenv()

# Initialize responder
responder = init_responder()

if not responder:
    st.error("""
    ⚠️ Application initialization failed. Please check:
    1. Your .env file exists and contains GOOGLE_API_KEY
    2. Your internet connection is stable
    3. Your API key is valid
    
    Try restarting the application after fixing these issues.
    """)
    st.stop()

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

# Language selection buttons in sidebar
st.sidebar.title("語言設定 Language")

input_lang = st.sidebar.radio(
    "輸入語言 Input Language",
    ["中文", "English"],
    index=1,
    key="input_lang_radio",
    horizontal=True,
    format_func=lambda x: "🇹🇼 " + x if x == "中文" else "🇺🇸 " + x
)

output_lang = st.sidebar.radio(
    "回應語言 Response Language",
    ["中文", "English"],
    index=1,
    key="output_lang_radio",
    horizontal=True,
    format_func=lambda x: "🇹🇼 " + x if x == "中文" else "🇺🇸 " + x
)

# Main chat interface
st.title("AI 日記助手 📝" if input_lang == "中文" else "AI Diary Assistant 📝")

# File upload
uploaded_files = st.file_uploader(
    "上傳照片（可多選）" if input_lang == "中文" else "Upload Photos (Optional)",
    type=['png', 'jpg', 'jpeg'],
    accept_multiple_files=True
)

# Display uploaded images
if uploaded_files:
    cols = st.columns(4)
    for idx, file in enumerate(uploaded_files):
        with cols[idx % 4]:
            st.image(file, use_column_width=True)

# Display chat history
for message in st.session_state.chat_history:
    if message["role"] == "user":
        st.markdown(f'<div class="user-message">{message["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="assistant-message">{message["content"]}</div>', unsafe_allow_html=True)

# Chat input with form
with st.form(key="chat_form", clear_on_submit=True):
    placeholder = "今天發生了什麼事？有什麼感受？" if input_lang == "中文" else "What happened today? How do you feel?"
    user_input = st.text_area(
        "分享你的心情..." if input_lang == "中文" else "Share your thoughts...",
        height=100,
        placeholder=placeholder,
        key="chat_input"
    )
    
    # Hidden submit button (will be triggered by Enter key)
    submit = st.form_submit_button("Send", type="primary")

# Process form submission
if submit and user_input.strip():
    # Add user message to chat history
    st.session_state.chat_history.append({
        "role": "user",
        "content": user_input
    })
    
    # Process images if any
    image_paths = []
    if uploaded_files:
        for file in uploaded_files:
            image = Image.open(file)
            image_paths.append(image)
    
    # Get AI response
    with st.spinner("AI助手正在思考回覆..." if output_lang == "中文" else "AI is thinking..."):
        response = responder.get_response(
            user_input,
            images=image_paths,
            input_lang=input_lang,
            output_lang=output_lang
        )
    
    # Add AI response to chat history
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": response
    })
    
    # Rerun to update the display
    st.rerun()

# Clear chat button
if st.button("清除對話" if input_lang == "中文" else "Clear Chat"):
    st.session_state.chat_history = []
    st.rerun()

# Add JavaScript for Enter key handling
st.markdown("""
<script>
document.addEventListener('keydown', function(e) {
    if (e.key === 'Enter' && !e.shiftKey && !e.ctrlKey && !e.altKey) {
        e.preventDefault();
        const textarea = document.querySelector('textarea');
        if (textarea && textarea.value.trim()) {
            const submitButton = document.querySelector('button[kind="primary"]');
            if (submitButton) {
                submitButton.click();
            }
        }
    }
});
</script>
""", unsafe_allow_html=True) 