import os
import google.generativeai as genai
from dotenv import load_dotenv
import time
from PIL import Image

class DiaryResponder:
    """Class to handle interactions with Google Gemini API."""
    
    def __init__(self):
        # Load environment variables if not already loaded
        load_dotenv()
        
        # Get API key with better error handling
        self.api_key = os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables. Please check your .env file.")
        
        try:
            # Configure the API
            genai.configure(api_key=self.api_key)
            
            # Set up the model configuration for more natural responses
            self.generation_config = {
                "temperature": 0.85,
                "top_p": 0.95,
                "top_k": 40,
                "max_output_tokens": 1024,
            }
            
            self.safety_settings = [
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            ]
            
            # Initialize the model with validation
            try:
                self.model = genai.GenerativeModel('models/gemini-1.5-flash-latest',
                                                 generation_config=self.generation_config,
                                                 safety_settings=self.safety_settings)
                
                # Initialize rate limiting parameters
                self.last_request_time = 0
                self.min_request_interval = 2  # Minimum seconds between requests
                
                # Validate model initialization with a simple test
                self._make_request_with_rate_limit(lambda: self.model.generate_content("test"))
                    
            except Exception as e:
                raise ValueError(f"Failed to initialize Gemini model: {str(e)}")
            
            # Initialize conversation
            self.conversation = None
            self.reset_conversation()
            
        except Exception as e:
            raise ValueError(f"Failed to configure Gemini API: {str(e)}")

    def _make_request_with_rate_limit(self, request_func, max_retries=3):
        """Helper method to make API requests with rate limiting"""
        retry_delay = self.min_request_interval
        
        for attempt in range(max_retries):
            try:
                # Ensure minimum time between requests
                current_time = time.time()
                time_since_last = current_time - self.last_request_time
                if time_since_last < self.min_request_interval:
                    time.sleep(self.min_request_interval - time_since_last)
                
                response = request_func()
                self.last_request_time = time.time()
                return response
                
            except Exception as e:
                if "429" in str(e) and attempt < max_retries - 1:
                    print(f"Rate limit hit, waiting {retry_delay} seconds...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                raise e
        
        raise Exception("Maximum retries reached")

    def reset_conversation(self):
        """Reset the conversation context with error handling"""
        try:
            if not self.model:
                self.init_model()
            self.conversation = self.model.start_chat(history=[])
            return True
        except Exception as e:
            print(f"Error resetting conversation: {e}")
            self.conversation = None
            return False

    def ensure_conversation_health(self):
        """Ensure the conversation and model are healthy"""
        if not self.model or not self.conversation:
            return self.reset_conversation()
        return True

    def get_response(self, user_input, images=None, input_lang="中文", output_lang="中文"):
        """Generate response based on user input and conversation history"""
        if not user_input.strip():
            return "有什麼想聊的嗎？(◕‿◕)" if output_lang == "中文" else "What would you like to chat about? (◕‿◕)"
            
        try:
            # Ensure conversation health
            if not self.ensure_conversation_health():
                raise Exception("Failed to initialize conversation")
            
            # Add context if it's a new conversation
            if not self.conversation.history:
                context = self.get_context(output_lang)
                try:
                    self._make_request_with_rate_limit(
                        lambda: self.conversation.send_message(f"Context: {context}")
                    )
                except Exception as e:
                    print(f"Error sending context: {e}")
                    if not self.reset_conversation():
                        raise Exception("Failed to reset conversation")
                    self._make_request_with_rate_limit(
                        lambda: self.conversation.send_message(f"Context: {context}")
                    )
            
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
                response = self._make_request_with_rate_limit(
                    lambda: self.conversation.send_message(base_prompt)
                )
            
            if response and response.text and len(response.text.strip()) > 0:
                return response.text
            else:
                raise Exception("Empty or invalid response")
                
        except Exception as e:
            print(f"Error in get_response: {e}")
            return "需要休息一下，等等再聊吧 (´･_･`)" if output_lang == "中文" else "Need a little break, let's chat later (´･_･`)"

    def get_context(self, lang="中文"):
        """Get the appropriate context based on language"""
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
        """Analyze the emotional content of user's message"""
        if not text.strip():
            return None
            
        try:
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

            response = self._make_request_with_rate_limit(
                lambda: self.model.generate_content(prompt)
            )
            return response.text if response and response.text else None
        except Exception as e:
            print(f"Error in analyze_emotion: {e}")
            return None
    
    def suggest_followup_questions(self, conversation_history, lang="zh"):
        """Generate relevant follow-up questions based on conversation history"""
        if not conversation_history:
            return []
            
        try:
            # Extract text from conversation history
            history_text = ""
            for msg in conversation_history[-3:]:  # Only use last 3 messages for better focus
                if hasattr(msg, 'parts') and msg.parts:
                    history_text += msg.parts[0].text + "\n"
            
            if not history_text.strip():
                return []
                
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

            response = self._make_request_with_rate_limit(
                lambda: self.model.generate_content(prompt)
            )
            if response and response.text:
                questions = [q.strip() for q in response.text.split("\n") if q.strip() and "?" in q]
                return questions[:2]  # Return at most 2 questions
            return []
        except Exception as e:
            print(f"Error in suggest_followup_questions: {e}")
            return [] 