import json
import os
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass

@dataclass
class DiaryEntry:
    """Class representing a single diary entry."""
    timestamp: datetime
    content: str
    claude_response: str
    image_path: Optional[str] = None  # Comma-separated paths for multiple images
    file_path: Optional[str] = None   # Comma-separated paths for multiple files
    entry_id: Optional[str] = None

    def to_dict(self) -> dict:
        """Convert entry to dictionary for storage."""
        return {
            'entry_id': self.entry_id or str(int(self.timestamp.timestamp())),
            'timestamp': self.timestamp.isoformat(),
            'content': self.content,
            'claude_response': self.claude_response,
            'image_path': self.image_path,
            'file_path': self.file_path
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'DiaryEntry':
        """Create DiaryEntry instance from dictionary."""
        return cls(
            timestamp=datetime.fromisoformat(data['timestamp']),
            content=data['content'],
            claude_response=data['claude_response'],
            image_path=data.get('image_path'),
            file_path=data.get('file_path'),
            entry_id=data.get('entry_id')
        )

class DiaryManager:
    """Class to manage diary entries storage and retrieval."""
    
    def __init__(self, storage_file: str = "diary_data.json"):
        self.storage_file = storage_file
        self.entries: Dict[str, DiaryEntry] = {}
        self._load_entries()

    def _load_entries(self):
        """Load entries from storage file."""
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.entries = {
                    entry_id: DiaryEntry.from_dict(entry_data)
                    for entry_id, entry_data in data.items()
                }

    def _save_entries(self):
        """Save entries to storage file."""
        data = {
            entry_id: entry.to_dict()
            for entry_id, entry in self.entries.items()
        }
        with open(self.storage_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def add_entry(self, entry: DiaryEntry) -> str:
        """Add a new diary entry."""
        entry_id = str(int(entry.timestamp.timestamp()))
        self.entries[entry_id] = entry
        self._save_entries()
        return entry_id

    def get_entries_by_date_range(self, start_date: datetime, end_date: datetime) -> List[DiaryEntry]:
        """Get entries within a date range."""
        return [
            entry for entry in self.entries.values()
            if start_date <= entry.timestamp <= end_date
        ]

    def get_daily_entries(self, date: datetime) -> List[DiaryEntry]:
        """Get entries for a specific day."""
        start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)
        return self.get_entries_by_date_range(start, end)

    def get_weekly_entries(self, date: datetime) -> List[DiaryEntry]:
        """Get entries for the week containing the specified date."""
        start = date - timedelta(days=date.weekday())
        start = start.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=7)
        return self.get_entries_by_date_range(start, end)

    def get_monthly_entries(self, date: datetime) -> List[DiaryEntry]:
        """Get entries for the month containing the specified date."""
        start = date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        if date.month == 12:
            end = date.replace(year=date.year + 1, month=1, day=1)
        else:
            end = date.replace(month=date.month + 1, day=1)
        return self.get_entries_by_date_range(start, end) 