from flask import Flask, render_template, request
import markdown2
import sqlite3

app = Flask(__name__)


def get_db_connection():
    try:
        conn = sqlite3.connect("blog.db")
        return conn
    except sqlite3.Error as e:
        print(e)
        return None


def create_database():
    conn = get_db_connection()
    if conn is not None:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                image TEXT,
                type TEXT NOT NULL,
                tags TEXT
            )
        """
        )
        conn.commit()
        conn.close()


create_database()


@app.context_processor
def inject_markdown2():
    return {"markdown2": markdown2}


@app.route("/")
def index():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM articles WHERE type='article' ORDER BY id DESC LIMIT 5"
            )
            latest_articles = cursor.fetchall()
            cursor.execute(
                "SELECT * FROM articles WHERE type='tutorial' ORDER BY id DESC LIMIT 5"
            )
            latest_tutorials = cursor.fetchall()
            cursor.close()
            conn.close()

            if len(latest_articles) == 0 and len(latest_tutorials) == 0:
                message = "No hay artículos publicados aún"
            else:
                message = ""
            return render_template(
                "index.html",
                articles=latest_articles,
                tutorials=latest_tutorials,
                message=message,
            )
        except sqlite3.Error as e:
            print(e)
            return "Error en la conexión a la base de datos"
    else:
        return "Error en la conexión a la base de datos"


@app.route("/articles")
def view_all_articles():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM articles WHERE type='article' ORDER BY id DESC"
            )
            all_articles = cursor.fetchall()
            cursor.close()
            conn.close()
            return render_template("all_articles.html", articles=all_articles)
        except sqlite3.Error as e:
            print(e)
            return "Error en la conexión a la base de datos"
    else:
        return "Error en la conexión a la base de datos"


@app.route("/tutoriales")
def view_all_tutorials():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM articles WHERE type='tutorial' ORDER BY id DESC"
            )
            all_tutorials = cursor.fetchall()
            cursor.close()
            conn.close()
            return render_template("all_tutorials.html", tutorials=all_tutorials)
        except sqlite3.Error as e:
            print(e)
            return "Error en la conexión a la base de datos"
    else:
        return "Error en la conexión a la base de datos"


@app.route("/article/<int:article_id>")
def view_article(article_id):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM articles WHERE id = ?", (article_id,))
            article = cursor.fetchone()
            cursor.close()
            conn.close()
            return render_template("article.html", article=article)
        except sqlite3.Error as e:
            print(e)
            return "Error en la conexión a la base de datos"
    else:
        return "Error en la conexión a la base de datos"


@app.route("/search")
def search():
    keyword = request.args.get("keyword", "")

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM articles WHERE title LIKE ?", ("%" + keyword + "%",)
            )
            articles = cursor.fetchall()
            cursor.close()
            conn.close()
            return render_template("search.html", articles=articles)
        except sqlite3.Error as e:
            print(e)
            return "Error en la conexión a la base de datos"
    else:
        return "Error en la conexión a la base de datos"


@app.route("/create_article_yoezequiel_011358", methods=["GET", "POST"])
def create_article():
    if request.method == "POST":
        try:
            title = request.form["title"]
            content = request.form["content"]
            article_type = request.form["type"]
            tags = request.form["tags"]
            image = request.files.get("image")
            if image:
                image.save("static/images/" + image.filename)
            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()
                    cursor.execute(
                        "INSERT INTO articles (title, content, image, type, tags) VALUES (?, ?, ?, ?, ?)",
                        (
                            title,
                            content,
                            image.filename if image else None,
                            article_type,
                            tags,
                        ),
                    )
                    conn.commit()
                    cursor.close()
                    conn.close()
                    return "Artículo creado exitosamente"
                except sqlite3.Error as e:
                    print(e)
                    return "Error en la conexión a la base de datos"
            else:
                return "Error en la conexión a la base de datos"

        except sqlite3.Error as e:
            print(e)
            return "Error en la conexión a la base de datos"

    return render_template("create_article.html")


@app.errorhandler(404)
def page_not_found(error):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
