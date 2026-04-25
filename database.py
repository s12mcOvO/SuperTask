import json
import sqlite3
import os
from datetime import datetime

class AssignmentDB:
    def __init__(self, db_path="assignments.db"):
        self.db_path = db_path
        self.json_backup_path = "assignments_backup.json"
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        self._init_db()
    
    def _init_db(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS assignments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                sender TEXT DEFAULT '教师',
                date TEXT NOT NULL,
                completed BOOLEAN DEFAULT 0,
                status TEXT DEFAULT 'pending'
            )
        """)
        self.conn.commit()
    
    def add_assignment(self, title, content, sender="教师", metadata=None):
        date = datetime.now().strftime("%Y-%m-%d %H:%M")
        self.cursor.execute("""
            INSERT INTO assignments (title, content, sender, date)
            VALUES (?, ?, ?, ?)
        """, (title, content, sender, date))
        self.conn.commit()
        aid = self.cursor.lastrowid
        self._backup_to_json()
        return {"id": aid, "title": title, "content": content,
                "sender": sender, "date": date, "completed": False, "status": "pending"}
    
    def toggle_complete(self, aid):
        self.cursor.execute("SELECT completed FROM assignments WHERE id = ?", (aid,))
        r = self.cursor.fetchone()
        if not r:
            return None
        new = not r[0]
        self.cursor.execute("UPDATE assignments SET completed = ?, status = ? WHERE id = ?",
                          (new, "completed" if new else "pending", aid))
        self.conn.commit()
        self._backup_to_json()
        return self.get_assignment(aid)
    
    def get_assignment(self, aid):
        self.cursor.execute("SELECT id, title, content, sender, date, completed, status FROM assignments WHERE id = ?", (aid,))
        r = self.cursor.fetchone()
        if r:
            return {"id": r[0], "title": r[1], "content": r[2],
                    "sender": r[3], "date": r[4], "completed": bool(r[5]), "status": r[6]}
        return None
    
    def get_all(self):
        self.cursor.execute("SELECT id, title, content, sender, date, completed, status FROM assignments ORDER BY date DESC, id DESC")
        return [{"id": r[0], "title": r[1], "content": r[2],
                "sender": r[3], "date": r[4], "completed": bool(r[5]), "status": r[6]}
                for r in self.cursor.fetchall()]
    
    def get_pending(self):
        self.cursor.execute("SELECT id, title, content, sender, date, completed, status FROM assignments WHERE completed = 0 ORDER BY date DESC, id DESC")
        return [{"id": r[0], "title": r[1], "content": r[2],
                "sender": r[3], "date": r[4], "completed": bool(r[5]), "status": r[6]}
                for r in self.cursor.fetchall()]
    
    def get_completed(self):
        self.cursor.execute("SELECT id, title, content, sender, date, completed, status FROM assignments WHERE completed = 1 ORDER BY date DESC, id DESC")
        return [{"id": r[0], "title": r[1], "content": r[2],
                "sender": r[3], "date": r[4], "completed": bool(r[5]), "status": r[6]}
                for r in self.cursor.fetchall()]
    
    def _backup_to_json(self):
        assignments = self.get_all()
        with open(self.json_backup_path, 'w', encoding='utf-8') as f:
            json.dump(assignments, f, ensure_ascii=False, indent=2)
    
    def close(self):
        self.conn.close()

if __name__ == "__main__":
    db = AssignmentDB()
    db.add_assignment("数学", "1. 解方程", "数学老师")
    print(json.dumps(db.get_all(), indent=2, ensure_ascii=False))
    db.close()
