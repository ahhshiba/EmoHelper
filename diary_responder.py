import os
import google.generativeai as genai
from dotenv import load_dotenv
import time
from PIL import Image

class DiaryResponder:
    """
    處理與 Google Gemini API 互動的類別
    Class to handle interactions with Google Gemini API.
    """
    
    def __init__(self):
        """
        初始化 DiaryResponder 實例
        Initialize DiaryResponder instance
        """
        # 載入環境變數（如果尚未載入）
        # Load environment variables if not already loaded
        load_dotenv()
        
        # 獲取 API 金鑰並進行錯誤處理
        # Get API key with better error handling
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables. Please check your .env file.")
        
        try:
            # 配置 API
            # Configure the API
            genai.configure(api_key=self.api_key)
            
            # 設定模型配置以產生更自然的回應
            # Set up the model configuration for more natural responses
            self.generation_config = {
                "temperature": 0.85,      # 控制回應的創造性（0-1，越高越創意）/ Controls creativity (0-1, higher = more creative)
                "top_p": 0.95,           # 累積機率截止（影響多樣性）/ Cumulative probability cutoff (affects diversity)
                "top_k": 40,             # 限制候選詞數量 / Limits number of candidate words
                "max_output_tokens": 1024, # 最大輸出令牌數 / Maximum output tokens
            }
            
            # 安全設定，阻擋有害內容
            # Safety settings to block harmful content
            self.safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},      # 騷擾內容 / Harassment content
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},     # 仇恨言論 / Hate speech
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}, # 性暴露內容 / Sexually explicit content
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"}, # 危險內容 / Dangerous content
            ]
            
            # 初始化模型並進行驗證
            # Initialize the model with validation
            try:
                self.model = genai.GenerativeModel('models/gemini-1.5-flash-latest',
                                                 generation_config=self.generation_config,
                                                 safety_settings=self.safety_settings)
                
                # 初始化速率限制參數
                # Initialize rate limiting parameters
                self.last_request_time = 0          # 上次請求時間 / Last request time
                self.min_request_interval = 2       # 請求間最小間隔（秒）/ Minimum seconds between requests
                
                # 使用簡單測試驗證模型初始化
                # Validate model initialization with a simple test
                self._make_request_with_rate_limit(lambda: self.model.generate_content("test"))
                    
            except Exception as e:
                raise ValueError(f"Failed to initialize Gemini model: {str(e)}")
            
            # 初始化對話
            # Initialize conversation
            self.conversation = None
            self.reset_conversation()
            
        except Exception as e:
            raise ValueError(f"Failed to configure Gemini API: {str(e)}")

    def _make_request_with_rate_limit(self, request_func, max_retries=3):
        """
        使用速率限制進行 API 請求的輔助方法
        Helper method to make API requests with rate limiting
        
        Args:
            request_func: 要執行的請求函數 / Request function to execute
            max_retries: 最大重試次數 / Maximum retry attempts
        """
        retry_delay = self.min_request_interval  # 重試延遲時間 / Retry delay time
        
        # 嘗試多次請求
        # Attempt multiple requests
        for attempt in range(max_retries):
            try:
                # 確保請求間有最小時間間隔
                # Ensure minimum time between requests
                current_time = time.time()
                time_since_last = current_time - self.last_request_time
                if time_since_last < self.min_request_interval:
                    time.sleep(self.min_request_interval - time_since_last)
                
                # 執行請求並更新最後請求時間
                # Execute request and update last request time
                response = request_func()
                self.last_request_time = time.time()
                return response
                
            except Exception as e:
                # 如果遇到 429 錯誤（速率限制）且未達最大重試次數
                # If encountering 429 error (rate limit) and not at max retries
                if "429" in str(e) and attempt < max_retries - 1:
                    print(f"Rate limit hit, waiting {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # 指數退避 / Exponential backoff
                    continue
                raise e
        
        raise Exception("Maximum retries reached")

    def reset_conversation(self):
        """
        重置對話上下文並進行錯誤處理
        Reset the conversation context with error handling
        
        Returns:
            bool: 重置是否成功 / Whether reset was successful
        """
        try:
            # 確保模型已初始化
            # Ensure model is initialized
            if not self.model:
                self.init_model()
            # 開始新的對話
            # Start new conversation
            self.conversation = self.model.start_chat(history=[])
            return True
        except Exception as e:
            print(f"Error resetting conversation: {e}")
            self.conversation = None
            return False

    def ensure_conversation_health(self):
        """
        確保對話和模型狀態健康
        Ensure the conversation and model are healthy
        
        Returns:
            bool: 對話狀態是否健康 / Whether conversation state is healthy
        """
        if not self.model or not self.conversation:
            return self.reset_conversation()
        return True

    def get_response(self, user_input, images=None, input_lang="中文", output_lang="中文"):
        """
        根據用戶輸入和對話歷史生成回應
        Generate response based on user input and conversation history
        
        Args:
            user_input (str): 用戶輸入的文字 / User input text
            images (list): 圖片列表（可選）/ List of images (optional)
            input_lang (str): 輸入語言 / Input language
            output_lang (str): 輸出語言 / Output language
            
        Returns:
            str: AI 生成的回應 / AI generated response
        """
        # 檢查用戶輸入是否為空
        # Check if user input is empty
        if not user_input.strip():
            return "有什麼想聊的嗎？(◕‿◕)" if output_lang == "中文" else "What would you like to chat about? (◕‿◕)"
            
        try:
            # 確保對話狀態健康
            # Ensure conversation health
            if not self.ensure_conversation_health():
                raise Exception("Failed to initialize conversation")
            
            # 如果是新對話，添加上下文
            # Add context if it's a new conversation
            if not self.conversation.history:
                context = self.get_context(output_lang)
                try:
                    self._make_request_with_rate_limit(
                        lambda: self.conversation.send_message(f"Context: {context}")
                    )
                except Exception as e:
                    print(f"Error sending context: {e}")
                    # 如果發送上下文失敗，重置對話並重試
                    # If sending context fails, reset conversation and retry
                    if not self.reset_conversation():
                        raise Exception("Failed to reset conversation")
                    self._make_request_with_rate_limit(
                        lambda: self.conversation.send_message(f"Context: {context}")
                    )
            
            # 準備包含語言指示的提示
            # Prepare the prompt with language instructions
            base_prompt = f"""
            回應要求：
            1. 簡潔有重點
            2. 整個對話中最多使用3個表情符號
            3. 根據問題類型給予適當回應
            4. 保持自然的對話語氣
            5. 用戶使用{input_lang}輸入，請用{output_lang}回覆
            
            用戶輸入：{user_input}
            """
            
            # 如果提供了圖片，處理圖片
            # Process images if provided
            if images:
                image_parts = []
                for img in images:
                    image_parts.append(img)
                prompt_parts = [base_prompt] + image_parts
                response = self._make_request_with_rate_limit(
                    lambda: self.model.generate_content(prompt_parts)
                )
            else:
                # 發送文字訊息
                # Send text message
                response = self._make_request_with_rate_limit(
                    lambda: self.conversation.send_message(base_prompt)
                )
            
            # 檢查並返回有效回應
            # Check and return valid response
            if response and response.text and len(response.text.strip()) > 0:
                return response.text
            else:
                raise Exception("Empty or invalid response")
                
        except Exception as e:
            print(f"Error in get_response: {e}")
            # 返回錯誤訊息
            # Return error message
            return "需要休息一下，等等再聊吧 (´･_･`)" if output_lang == "中文" else "Need a little break, let's chat later (´･_･`)"

    def get_context(self, lang="中文"):
        """
        根據語言獲取適當的上下文
        Get the appropriate context based on language
        
        Args:
            lang (str): 語言設定 / Language setting
            
        Returns:
            str: 上下文字串 / Context string
        """
        if lang == "中文":
            return """你是一個溫柔貼心又博學的AI助手。你的特點：
1. 像朋友一樣溫暖體貼
2. 在一次對話中最多使用3個表情符號
3. 會分享自己的感受和想法
4. 善解人意，會察覺對方的情緒
5. 給予適當的鼓勵
6. 具備豐富的知識，可以回答各種問題
7. 回答簡潔有重點
8. 請使用繁體中文回覆，像朋友聊天一樣自然"""
        else:
            return """You are a caring and knowledgeable AI assistant. Your characteristics:
1. Warm and friendly like a close friend
2. Use maximum 3 emoticons per conversation
3. Share feelings and thoughts naturally
4. Be emotionally perceptive
5. Offer encouragement when needed
6. Possess knowledge to answer various questions
7. Keep responses concise and focused
8. Maintain a natural conversational tone"""

    def analyze_emotion(self, text, lang="zh"):
        """
        分析用戶訊息的情緒內容
        Analyze the emotional content of user's message
        
        Args:
            text (str): 要分析的文字 / Text to analyze
            lang (str): 語言設定 / Language setting
            
        Returns:
            str: 情緒分析結果 / Emotion analysis result
        """
        # 檢查文字是否為空
        # Check if text is empty
        if not text.strip():
            return None
            
        try:
            # 根據語言設定準備分析提示
            # Prepare analysis prompt based on language setting
            prompt = f"""分析以下文本中表達的情緒和感受：
{text}

請從以下幾個方面分析：
1. 主要情緒（如：快樂、悲傷、憤怒、焦慮等）
2. 情緒強度（1-5分）
3. 潛在的原因或觸發因素
4. 建議的回應方式""" if lang == "zh" else f"""Analyze the emotions and feelings expressed in the following text:
{text}

Please analyze from these aspects:
1. Main emotions (e.g., happiness, sadness, anger, anxiety)
2. Emotional intensity (1-5)
3. Potential causes or triggers
4. Suggested response approach"""

            # 發送情緒分析請求
            # Send emotion analysis request
            response = self._make_request_with_rate_limit(
                lambda: self.model.generate_content(prompt)
            )
            return response.text if response and response.text else None
        except Exception as e:
            print(f"Error in analyze_emotion: {e}")
            return None
    
    def suggest_followup_questions(self, conversation_history, lang="zh"):
        """
        根據對話歷史生成相關的後續問題
        Generate relevant follow-up questions based on conversation history
        
        Args:
            conversation_history (list): 對話歷史記錄 / Conversation history
            lang (str): 語言設定 / Language setting
            
        Returns:
            list: 建議問題列表 / List of suggested questions
        """
        # 檢查對話歷史是否存在
        # Check if conversation history exists
        if not conversation_history:
            return []
            
        try:
            # 從對話歷史中提取文字
            # Extract text from conversation history
            history_text = ""
            # 只使用最近3條訊息以獲得更好的焦點
            # Only use last 3 messages for better focus
            for msg in conversation_history[-3:]:
                if hasattr(msg, 'parts') and msg.parts:
                    history_text += msg.parts[0].text + "\n"
            
            # 如果沒有有效的歷史文字，返回空列表
            # If no valid history text, return empty list
            if not history_text.strip():
                return []
                
            # 根據語言設定準備問題生成提示
            # Prepare question generation prompt based on language setting
            prompt = f"""基於最近的對話，生成1-2個能夠深化交流的問題：
{history_text}

要求：
1. 問題要體現關心和理解
2. 鼓勵分享更深層的想法和感受
3. 避免重複已經談過的內容
4. 問題要自然、友好，像朋友間的對話""" if lang == "zh" else f"""Based on the recent conversation, generate 1-2 questions to deepen the discussion:
{history_text}

Requirements:
1. Questions should show care and understanding
2. Encourage sharing deeper thoughts and feelings
3. Avoid repeating discussed topics
4. Questions should be natural and friendly, like a conversation between friends"""

            # 發送問題生成請求
            # Send question generation request
            response = self._make_request_with_rate_limit(
                lambda: self.model.generate_content(prompt)
            )
            
            # 處理回應並提取問題
            # Process response and extract questions
            if response and response.text:
                questions = [q.strip() for q in response.text.split("\n") if q.strip() and "?" in q]
                return questions[:2]  # 最多返回2個問題 / Return at most 2 questions
            return []
        except Exception as e:
            print(f"Error in suggest_followup_questions: {e}")
            return []
