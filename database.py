import sqlite3

DB_FILE = "converter.db"

class DatabaseManager:
    def __init__(self):
        self.conn = None

    def init_db(self):
        self.conn = sqlite3.connect(DB_FILE)
        self.conn.row_factory = sqlite3.Row
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                from_unit TEXT,
                value REAL,
                to_unit TEXT,
                result REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def insert_record(self, from_unit, value, to_unit, result):
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO history (from_unit, value, to_unit, result) VALUES (?, ?, ?, ?)",
            (from_unit, value, to_unit, result)
        )
        self.conn.commit()

    def get_all(self):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM history ORDER BY timestamp DESC")
        return cur.fetchall()

    def close(self):
        if self.conn:
            self.conn.close()