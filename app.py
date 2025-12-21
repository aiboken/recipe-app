from flask import Flask, render_template, abort, request, redirect, url_for
from PIL import Image
import sqlite3
import os
import pytesseract

app = Flask(__name__)

UPLOAD_FOLDER = "static/images"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def get_db_connection():
    conn = sqlite3.connect("recipes.db")
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    ingredient = request.args.get("ingredient")
    category_id = request.args.get("category_id")
    show_fav = request.args.get("fav")

    conn = get_db_connection()

    # 分類一覧（検索フォーム用）
    categories = conn.execute(
        "SELECT * FROM categories ORDER BY name"
    ).fetchall()

    query = """
        SELECT r.id, r.name, r.image, r.favorite, c.name AS category
        FROM recipes r
        LEFT JOIN categories c ON r.category_id = c.id
        WHERE 1=1
    """
    params = []

    if ingredient:
        query += " AND r.ingredients LIKE ?"
        params.append(f"%{ingredient}%")

    if category_id:
        query += " AND r.category_id = ?"
        params.append(category_id)

    if show_fav:
        query += " AND r.favorite = 1"

    recipes = conn.execute(query, params).fetchall()
    conn.close()

    return render_template(
        "index.html",
        recipes=recipes,
        categories=categories,
        show_fav=show_fav
    )

@app.route("/recipe/<int:recipe_id>")
def recipe_detail(recipe_id):
    conn = get_db_connection()
    recipe = conn.execute(
        "SELECT * FROM recipes WHERE id = ?",
        (recipe_id,)
    ).fetchone()
    conn.close()

    if recipe is None:
        abort(404)

    return render_template("detail.html", recipe=recipe)

# ★ 新規登録画面
@app.route("/add", methods=["GET", "POST"])
def add_recipe():
    conn = get_db_connection()

    if request.method == "POST":
        name = request.form["name"]
        ingredients = request.form["ingredients"]
        steps = request.form["steps"]
        memo = request.form["memo"]
        category_id = request.form["category_id"] or None

        image_file = request.files["image"]
        image_name = image_file.filename

        if image_name:
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], image_name)
            image_file.save(save_path)

        conn.execute(
            """
            INSERT INTO recipes (name, image, ingredients, steps, memo, category_id)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (name, image_name, ingredients, steps, memo, category_id)
        )
        conn.commit()
        conn.close()

        return redirect(url_for("index"))

    categories = conn.execute(
        "SELECT * FROM categories ORDER BY name"
    ).fetchall()
    conn.close()

    return render_template("add.html", categories=categories)

@app.route("/categories", methods=["GET", "POST"])
def categories():
    conn = get_db_connection()

    if request.method == "POST":
        name = request.form["name"]
        try:
            conn.execute(
                "INSERT INTO categories (name) VALUES (?)",
                (name,)
            )
            conn.commit()
        except sqlite3.IntegrityError:
            pass  # 同名カテゴリは無視

    categories = conn.execute(
        "SELECT * FROM categories ORDER BY name"
    ).fetchall()
    conn.close()

    return render_template("categories.html", categories=categories)

@app.route("/favorite/<int:recipe_id>")
def toggle_favorite(recipe_id):
    conn = get_db_connection()

    conn.execute("""
        UPDATE recipes
        SET favorite = CASE
            WHEN favorite = 1 THEN 0
            ELSE 1
        END
        WHERE id = ?
    """, (recipe_id,))

    conn.commit()
    conn.close()

    return redirect(url_for("index"))

@app.route("/ocr", methods=["POST"])
def ocr_image():
    image_file = request.files["image"]

    img = Image.open(image_file)

    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )

    text = pytesseract.image_to_string(img, lang="jpn")

    return text

#再編集用ルート
@app.route("/edit/<int:recipe_id>", methods=["GET", "POST"])
def edit_recipe(recipe_id):
    conn = get_db_connection()

    recipe = conn.execute(
        "SELECT * FROM recipes WHERE id = ?",
        (recipe_id,)
    ).fetchone()

    if recipe is None:
        conn.close()
        abort(404)

    categories = conn.execute(
        "SELECT * FROM categories ORDER BY name"
    ).fetchall()

    if request.method == "POST":
        name = request.form["name"]
        ingredients = request.form["ingredients"]
        steps = request.form["steps"]
        memo = request.form["memo"]
        category_id = request.form["category_id"] or None

        image_file = request.files["image"]
        image_name = recipe["image"]  # デフォルトは既存画像

        if image_file and image_file.filename:
            image_name = image_file.filename
            save_path = os.path.join(app.config["UPLOAD_FOLDER"], image_name)
            image_file.save(save_path)

        conn.execute("""
            UPDATE recipes
            SET name=?, image=?, ingredients=?, steps=?, memo=?, category_id=?
            WHERE id=?
        """, (name, image_name, ingredients, steps, memo, category_id, recipe_id))

        conn.commit()
        conn.close()

        return redirect(url_for("recipe_detail", recipe_id=recipe_id))

    conn.close()
    return render_template(
        "edit.html",
        recipe=recipe,
        categories=categories
    )

#削除用ルート
@app.route("/delete/<int:recipe_id>", methods=["POST"])
def delete_recipe(recipe_id):
    conn = get_db_connection()

    # 画像ファイル名を取得
    recipe = conn.execute(
        "SELECT image FROM recipes WHERE id = ?",
        (recipe_id,)
    ).fetchone()

    if recipe is None:
        conn.close()
        abort(404)

    # DBから削除
    conn.execute(
        "DELETE FROM recipes WHERE id = ?",
        (recipe_id,)
    )
    conn.commit()
    conn.close()

    # 画像ファイルも削除（存在すれば）
    if recipe["image"]:
        image_path = os.path.join(app.config["UPLOAD_FOLDER"], recipe["image"])
        if os.path.exists(image_path):
            os.remove(image_path)

    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
