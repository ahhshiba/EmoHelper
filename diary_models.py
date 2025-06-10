import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class DiaryEntry:
    """
    表示單一日記條目的類別
    Class representing a single diary entry.
    """
    timestamp: datetime                    # 時間戳記 / Timestamp of the entry
    content: str                          # 日記內容 / Diary content
    claude_response: str                  # Claude AI 的回應 / Claude AI's response
    image_path: Optional[str] = None      # 圖片路徑（多個圖片用逗號分隔）/ Image paths (comma-separated for multiple images)
    file_path: Optional[str] = None       # 檔案路徑（多個檔案用逗號分隔）/ File paths (comma-separated for multiple files)
    entry_id: Optional[str] = None        # 條目唯一識別碼 / Unique entry identifier
    
    def to_dict(self) -> dict:
        """
        將條目轉換為字典格式以供儲存
        Convert entry to dictionary for storage.
        
        Returns:
            dict: 包含所有條目資料的字典 / Dictionary containing all entry data
        """
        return {
            'entry_id': self.entry_id or str(int(self.timestamp.timestamp())),  # 使用時間戳記作為預設 ID / Use timestamp as default ID
            'timestamp': self.timestamp.isoformat(),                             # ISO 格式的時間字串 / ISO format timestamp string
            'content': self.content,                                             # 日記文字內容 / Diary text content
            'claude_response': self.claude_response,                             # AI 回應內容 / AI response content
            'image_path': self.image_path,                                       # 圖片檔案路徑 / Image file paths
            'file_path': self.file_path                                          # 其他檔案路徑 / Other file paths
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'DiaryEntry':
        """
        從字典資料建立 DiaryEntry 實例
        Create DiaryEntry instance from dictionary.
        
        Args:
            data (dict): 包含條目資料的字典 / Dictionary containing entry data
            
        Returns:
            DiaryEntry: 新建立的日記條目實例 / Newly created diary entry instance
        """
        return cls(
            timestamp=datetime.fromisoformat(data['timestamp']),    # 將 ISO 字串轉換回 datetime / Convert ISO string back to datetime
            content=data['content'],                                # 載入日記內容 / Load diary content
            claude_response=data['claude_response'],                # 載入 AI 回應 / Load AI response
            image_path=data.get('image_path'),                      # 可選的圖片路徑 / Optional image paths
            file_path=data.get('file_path'),                        # 可選的檔案路徑 / Optional file paths
            entry_id=data.get('entry_id')                           # 可選的條目 ID / Optional entry ID
        )

class DiaryManager:
    """
    管理日記條目儲存和檢索的類別
    Class to manage diary entries storage and retrieval.
    """
    
    def __init__(self, storage_file: str = "diary_data.json"):
        """
        初始化日記管理器
        Initialize diary manager.
        
        Args:
            storage_file (str): 儲存檔案的路徑，預設為 "diary_data.json" 
                               / Storage file path, defaults to "diary_data.json"
        """
        self.storage_file = storage_file                            # 儲存檔案路徑 / Storage file path
        self.entries: Dict[str, DiaryEntry] = {}                   # 日記條目字典，以 ID 為鍵 / Dictionary of diary entries with ID as key
        self._load_entries()                                        # 載入現有的日記條目 / Load existing diary entries
    
    def _load_entries(self):
        """
        從儲存檔案載入日記條目
        Load entries from storage file.
        """
        # 檢查儲存檔案是否存在
        # Check if storage file exists
        if os.path.exists(self.storage_file):
            try:
                # 以 UTF-8 編碼開啟檔案並讀取 JSON 資料
                # Open file with UTF-8 encoding and read JSON data
                with open(self.storage_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # 將字典資料轉換為 DiaryEntry 物件
                    # Convert dictionary data to DiaryEntry objects
                    self.entries = {
                        entry_id: DiaryEntry.from_dict(entry_data)
                        for entry_id, entry_data in data.items()
                    }
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                # 處理檔案讀取或解析錯誤
                # Handle file reading or parsing errors
                print(f"Error loading diary entries: {e}")
                self.entries = {}
    
    def _save_entries(self):
        """
        將日記條目儲存到檔案
        Save entries to storage file.
        """
        try:
            # 將所有 DiaryEntry 物件轉換為字典格式
            # Convert all DiaryEntry objects to dictionary format
            data = {
                entry_id: entry.to_dict()
                for entry_id, entry in self.entries.items()
            }
            
            # 以 UTF-8 編碼寫入 JSON 檔案
            # Write JSON file with UTF-8 encoding
            with open(self.storage_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            # 處理檔案寫入錯誤
            # Handle file writing errors
            print(f"Error saving diary entries: {e}")
    
    def add_entry(self, entry: DiaryEntry) -> str:
        """
        新增一個日記條目
        Add a new diary entry.
        
        Args:
            entry (DiaryEntry): 要新增的日記條目 / Diary entry to add
            
        Returns:
            str: 新增條目的唯一識別碼 / Unique identifier of the added entry
        """
        # 生成基於時間戳記的唯一 ID
        # Generate unique ID based on timestamp
        entry_id = str(int(entry.timestamp.timestamp()))
        
        # 將條目加入記憶體中的字典
        # Add entry to in-memory dictionary
        self.entries[entry_id] = entry
        
        # 立即儲存到檔案
        # Immediately save to file
        self._save_entries()
        
        return entry_id
    
    def get_entries_by_date_range(self, start_date: datetime, end_date: datetime) -> List[DiaryEntry]:
        """
        取得指定日期範圍內的日記條目
        Get entries within a date range.
        
        Args:
            start_date (datetime): 開始日期 / Start date
            end_date (datetime): 結束日期 / End date
            
        Returns:
            List[DiaryEntry]: 符合日期範圍的日記條目列表 / List of diary entries within date range
        """
        return [
            entry for entry in self.entries.values()
            if start_date <= entry.timestamp <= end_date
        ]
    
    def get_daily_entries(self, date: datetime) -> List[DiaryEntry]:
        """
        取得指定日期的所有日記條目
        Get entries for a specific day.
        
        Args:
            date (datetime): 指定的日期 / Specified date
            
        Returns:
            List[DiaryEntry]: 該日的所有日記條目 / All diary entries for that day
        """
        # 設定當日的開始時間（00:00:00）
        # Set start time of the day (00:00:00)
        start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 設定次日的開始時間作為結束時間
        # Set start time of next day as end time
        end = start + timedelta(days=1)
        
        return self.get_entries_by_date_range(start, end)
    
    def get_weekly_entries(self, date: datetime) -> List[DiaryEntry]:
        """
        取得包含指定日期的那一週的所有日記條目
        Get entries for the week containing the specified date.
        
        Args:
            date (datetime): 指定的日期 / Specified date
            
        Returns:
            List[DiaryEntry]: 該週的所有日記條目 / All diary entries for that week
        """
        # 計算該週的週一（weekday() 回傳 0-6，週一為 0）
        # Calculate Monday of that week (weekday() returns 0-6, Monday is 0)
        start = date - timedelta(days=date.weekday())
        
        # 設定週一的開始時間（00:00:00）
        # Set start time of Monday (00:00:00)
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # 設定下週一的開始時間作為結束時間
        # Set start time of next Monday as end time
        end = start + timedelta(days=7)
        
        return self.get_entries_by_date_range(start, end)
    
    def get_monthly_entries(self, date: datetime) -> List[DiaryEntry]:
        """
        取得包含指定日期的那個月的所有日記條目
        Get entries for the month containing the specified date.
        
        Args:
            date (datetime): 指定的日期 / Specified date
            
        Returns:
            List[DiaryEntry]: 該月的所有日記條目 / All diary entries for that month
        """
        # 設定該月的第一天（00:00:00）
        # Set first day of the month (00:00:00)
        start = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # 計算下個月的第一天作為結束時間
        # Calculate first day of next month as end time
        if date.month == 12:
            # 如果是 12 月，下個月是明年 1 月
            # If December, next month is January of next year
            end = date.replace(year=date.year + 1, month=1, day=1)
        else:
            # 其他月份，月份加 1
            # For other months, increment month by 1
            end = date.replace(month=date.month + 1, day=1)
        
        return self.get_entries_by_date_range(start, end)
    
    def delete_entry(self, entry_id: str) -> bool:
        """
        刪除指定的日記條目
        Delete a specific diary entry.
        
        Args:
            entry_id (str): 要刪除的條目 ID / Entry ID to delete
            
        Returns:
            bool: 刪除是否成功 / Whether deletion was successful
        """
        if entry_id in self.entries:
            del self.entries[entry_id]
            self._save_entries()
            return True
        return False
    
    def update_entry(self, entry_id: str, updated_entry: DiaryEntry) -> bool:
        """
        更新指定的日記條目
        Update a specific diary entry.
        
        Args:
            entry_id (str): 要更新的條目 ID / Entry ID to update
            updated_entry (DiaryEntry): 更新後的條目資料 / Updated entry data
            
        Returns:
            bool: 更新是否成功 / Whether update was successful
        """
        if entry_id in self.entries:
            self.entries[entry_id] = updated_entry
            self._save_entries()
            return True
        return False
    
    def get_all_entries(self) -> List[DiaryEntry]:
        """
        取得所有日記條目，按時間排序
        Get all diary entries, sorted by time.
        
        Returns:
            List[DiaryEntry]: 所有日記條目的列表 / List of all diary entries
        """
        return sorted(self.entries.values(), key=lambda x: x.timestamp)
    
    def search_entries(self, keyword: str) -> List[DiaryEntry]:
        """
        搜尋包含關鍵字的日記條目
        Search diary entries containing a keyword.
        
        Args:
            keyword (str): 搜尋關鍵字 / Search keyword
            
        Returns:
            List[DiaryEntry]: 包含關鍵字的日記條目列表 / List of diary entries containing the keyword
        """
        keyword_lower = keyword.lower()
        return [
            entry for entry in self.entries.values()
            if (keyword_lower in entry.content.lower() or 
                keyword_lower in entry.claude_response.lower())
        ]
