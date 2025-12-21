import sqlite3

conn = sqlite3.connect("recipes.db")
conn.execute(
    "ALTER TABLE recipes ADD COLUMN favorite INTEGER DEFAULT 0"
)
conn.commit()
conn.close()

print("favoriteカラムを追加しました")
