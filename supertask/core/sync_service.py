import json
import os
from datetime import datetime

class SyncService:
    def __init__(self, db, server_url=None):
        self.db = db
        self.server_url = server_url or os.getenv("SERVER_URL", "http://localhost:8000")
        self.running = False
    
    def sync(self):
        try:
            assignments = self.db.get_all()
            return {"code": 0, "message": "模拟同步成功",
                   "data": {"uploaded": len(assignments), "downloaded": 0,
                           "last_sync": datetime.now().isoformat()}}
        except Exception as e:
            return {"code": -1, "message": str(e), "data": {}}

class MockSyncService:
    def __init__(self, db):
        self.db = db
    
    def sync(self):
        assignments = self.db.get_all()
        return {"code": 0, "message": "模拟同步成功",
               "data": {"uploaded": len(assignments), "downloaded": 0,
                       "last_sync": datetime.now().isoformat()}}

if __name__ == "__main__":
    from .database import AssignmentDB
    db = AssignmentDB()
    svc = MockSyncService(db)
    print(json.dumps(svc.sync(), indent=2, ensure_ascii=False))
    db.conn.close()
