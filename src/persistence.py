"""
Persistence layer for tracking processed emails
Stores email IDs to prevent duplicate processing
"""
import json
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional


class EmailPersistence:
    """Manages persistent storage of processed email metadata"""
    
    def __init__(self, db_path: str = "./data/processed_emails.json"):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """Create database file if it doesn't exist"""
        if not self.db_path.exists():
            self.db_path.write_text(json.dumps({
                "processed_emails": [],
                "last_sync": None,
                "last_run": None,
                "total_processed": 0
            }, indent=2))
    
    def _load_db(self) -> Dict:
        """Load database from file"""
        with open(self.db_path, 'r') as f:
            return json.load(f)
    
    def _save_db(self, data: Dict):
        """Save database to file"""
        with open(self.db_path, 'w') as f:
            json.dump(data, f, indent=2)
    
    def is_processed(self, email_id: str) -> bool:
        """Check if email has already been processed"""
        db = self._load_db()
        return email_id in db.get("processed_emails", [])
    
    def mark_processed(self, email_id: str, metadata: Optional[Dict] = None):
        """Mark email as processed"""
        db = self._load_db()
        if email_id not in db.get("processed_emails", []):
            db["processed_emails"].append(email_id)
            db["total_processed"] = len(db["processed_emails"])
            db["last_sync"] = datetime.now().isoformat()
            self._save_db(db)
    
    def mark_sent(self, email_id: str):
        """Mark email draft as sent"""
        db = self._load_db()
        db["processed_emails"].append(email_id)
        db["last_sync"] = datetime.now().isoformat()
        self._save_db(db)
    
    def get_processed_count(self) -> int:
        """Get total count of processed emails"""
        db = self._load_db()
        return db.get("total_processed", 0)
    
    def get_last_sync(self) -> Optional[str]:
        """Get timestamp of last sync"""
        db = self._load_db()
        return db.get("last_sync")

    def save_last_run(self):
        """Save the current time as the last run timestamp"""
        db = self._load_db()
        db["last_run"] = datetime.now().isoformat()
        self._save_db(db)

    def get_last_run(self) -> Optional[datetime]:
        """Get the datetime of the last run, or None if never run"""
        db = self._load_db()
        value = db.get("last_run")
        if value:
            return datetime.fromisoformat(value)
        return None
    
    def get_all_processed(self) -> List[str]:
        """Get list of all processed email IDs"""
        db = self._load_db()
        return db.get("processed_emails", [])
    
    def reset(self):
        """Reset the processed emails database"""
        self._ensure_db_exists()
        print("Processed emails database reset")
