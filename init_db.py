import sqlite3

conn = sqlite3.connect("recipes.db")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    image TEXT,
    ingredients TEXT,
    steps TEXT,
    memo TEXT
)
""")

# 初期データ（最初だけ）
cur.execute("""
INSERT INTO recipes (name, image, ingredients, steps, memo)
VALUES (?, ?, ?, ?, ?)
""", (
    "カレーライス",
    "curry.jpg",
    "・カレールウ\n・玉ねぎ\n・肉",
    "1. 切る\n2. 煮る\n3. ルウを入れる",
    "2日目が美味しい"
))

cur.execute("""
INSERT INTO recipes (name, image, ingredients, steps, memo)
VALUES (?, ?, ?, ?, ?)
""", (
    "オムレツ",
    "omelette.jpg",
    "・卵\n・牛乳\n・塩",
    "1. 混ぜる\n2. 焼く",
    ""
))

conn.commit()
conn.close()

print("DB初期化完了")
