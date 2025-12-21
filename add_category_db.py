import sqlite3

conn = sqlite3.connect("recipes.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE
)
""")

# 既存 recipes に category_id 列を追加（なければ）
try:
    cur.execute("ALTER TABLE recipes ADD COLUMN category_id INTEGER")
except sqlite3.OperationalError:
    pass  # 既にある場合

conn.commit()
conn.close()

print("カテゴリDB準備完了")
