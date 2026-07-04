import sqlite3
import logging

logger = logging.getLogger(__name__)

DB_FILE = "converter.db"

class DatabaseManager:
    def __init__(self):
        self.conn = None

    def init_db(self):
        self.conn = sqlite3.connect(DB_FILE)
        self.conn.row_factory = sqlite3.Row
        cur = self.conn.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_unit TEXT,
            value REAL,
            to_unit TEXT,
            result REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )""")
        self.conn.commit()
        logger.info("База данных инициализирована")

    def insert_record(self, from_unit, value, to_unit, result):
        try:
            cur = self.conn.cursor()
            cur.execute(
                "INSERT INTO history (from_unit, value, to_unit, result) VALUES (?, ?, ?, ?)",
                (from_unit, value, to_unit, result)
            )
            self.conn.commit()
            logger.info(f"Добавлена запись: {value} {from_unit} → {result:.4f} {to_unit}")
        except Exception as e:
            logger.error(f"Ошибка вставки в БД: {e}")
            raise

    def get_all(self):
        try:
            cur = self.conn.cursor()
            cur.execute("SELECT * FROM history ORDER BY timestamp DESC")
            records = cur.fetchall()
            logger.debug(f"Загружено {len(records)} записей")
            return records
        except Exception as e:
            logger.error(f"Ошибка чтения из БД: {e}")
            return []

    def delete_record(self, item_id):
        try:
            cur = self.conn.cursor()
            cur.execute("DELETE FROM history WHERE id=?", (item_id,))
            self.conn.commit()
            logger.info(f"Удалена запись ID: {item_id}")
        except Exception as e:
            logger.error(f"Ошибка удаления из БД: {e}")
            raise

    def close(self):
        if self.conn:
            self.conn.close()
            logger.info("Соединение с БД закрыто")
