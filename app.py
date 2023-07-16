from flask import Flask, render_template, request
from config import SECRET_KEY
from flaskext.markdown import Markdown
import sqlite3


app = Flask(__name__)
app = Flask(__name__, static_url_path='/static')
app.secret_key = SECRET_KEY  # Clave secreta para la sesión

Markdown(app)

# Rutas
@app.route('/')
def index():
    # Crea una nueva conexión y cursor en la función de la ruta
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()

    # Crear la tabla "articles" si no existe
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            image TEXT
        )
    ''')
    conn.commit()

    cursor.execute("SELECT * FROM articles ORDER BY id DESC LIMIT 5")
    latest_articles = cursor.fetchall()

    # Cierra la conexión y el cursor después de usarlos
    cursor.close()
    conn.close()

    if len(latest_articles) == 0:
        message = "No hay artículos publicados aún"
    else:
        message = ""

    return render_template('index.html', articles=latest_articles, message=message)


@app.route('/articles')
def view_all_articles():
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM articles")
    all_articles = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('all_articles.html', articles=all_articles)


@app.route('/article/<int:article_id>')
def view_article(article_id):
    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM articles WHERE id = ?", (article_id,))
    article = cursor.fetchone()

    cursor.close()
    conn.close()

    return render_template('article.html', article=article)


@app.route('/search')
def search():
    keyword = request.args.get('keyword', '')

    conn = sqlite3.connect('blog.db')
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM articles WHERE title LIKE ?", ('%' + keyword + '%',))
    articles = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('search.html', articles=articles)


@app.route('/create_article', methods=['GET', 'POST'])
def create_article():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        image = request.files.get('image')  # Usamos get() en lugar de ['image'] para obtener el archivo opcionalmente

        if image:
            # Guardar la imagen en tu sistema de archivos
            image.save('static/images/' + image.filename)

        conn = sqlite3.connect('blog.db')
        cursor = conn.cursor()

        # Insertar el artículo en la base de datos
        cursor.execute("INSERT INTO articles (title, content, image) VALUES (?, ?, ?)",
                    (title, content, image.filename if image else None))
        conn.commit()

        cursor.close()
        conn.close()

        return "Artículo creado exitosamente"

    return render_template('create_article.html')


@app.route('/cursos')
def cursos():
    return render_template('cursos.html')


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 40


if __name__ == '__main__':
    app.run(debug=True)
