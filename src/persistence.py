"""
Persistence layer for tracking processed emails.
Uses S3 when S3_BUCKET env var is set, otherwise local JSON file.
"""
import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional

_S3_BUCKET = os.environ.get("S3_BUCKET")
_S3_KEY = os.environ.get("PROCESSED_EMAILS_S3_KEY", "processed_emails.json")

_EMPTY_DB = {
    "processed_emails": [],
    "last_sync": None,
    "last_run": None,
    "total_processed": 0,
}


class EmailPersistence:
    """Manages persistent storage of processed email metadata (S3 or local file)."""

    def __init__(self, db_path: str = "./data/processed_emails.json"):
        if _S3_BUCKET:
            import boto3
            self._s3 = boto3.client("s3")
            self._bucket = _S3_BUCKET
            self._key = _S3_KEY
            self.db_path = None
        else:
            self._s3 = None
            self.db_path = Path(db_path)
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self._ensure_db_exists()

    def _ensure_db_exists(self):
        if self.db_path and not self.db_path.exists():
            self.db_path.write_text(json.dumps(_EMPTY_DB, indent=2))

    def _load_db(self) -> Dict:
        if self._s3:
            try:
                obj = self._s3.get_object(Bucket=self._bucket, Key=self._key)
                return json.loads(obj["Body"].read())
            except self._s3.exceptions.NoSuchKey:
                return dict(_EMPTY_DB)
        with open(self.db_path, "r") as f:
            return json.load(f)

    def _save_db(self, data: Dict):
        if self._s3:
            self._s3.put_object(
                Bucket=self._bucket,
                Key=self._key,
                Body=json.dumps(data, indent=2),
                ContentType="application/json",
            )
        else:
            with open(self.db_path, "w") as f:
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
