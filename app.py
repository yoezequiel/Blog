from flask import Flask, render_template, request
from flaskext.markdown import Markdown
import sqlite3
from config import SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY  # Clave secreta para la sesión
Markdown(app)

# Función para obtener la conexión a la base de datos
def get_db_connection():
    try:
        conn = sqlite3.connect('blog.db')
        return conn
    except sqlite3.Error as e:
        print(e)
        return None

def create_database():
    conn = get_db_connection()
    if conn is not None:
        conn.close()

# Llamada a la función create_database() para crear la base de datos si no existe
create_database()

# Rutas
@app.route('/')
def index():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()

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

            cursor.close()
            conn.close()

            if len(latest_articles) == 0:
                message = "No hay artículos publicados aún"
            else:
                message = ""

            return render_template('index.html', articles=latest_articles, message=message)

        except sqlite3.Error as e:
            print(e)
            return "Error en la conexión a la base de datos"
    else:
        return "Error en la conexión a la base de datos"

@app.route('/articles')
def view_all_articles():
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM articles ORDER BY id DESC")
            all_articles = cursor.fetchall()

            cursor.close()
            conn.close()

            return render_template('all_articles.html', articles=all_articles)

        except sqlite3.Error as e:
            print(e)
            return "Error en la conexión a la base de datos"
    else:
        return "Error en la conexión a la base de datos"

@app.route('/article/<int:article_id>')
def view_article(article_id):
    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM articles WHERE id = ?", (article_id,))
            article = cursor.fetchone()

            cursor.close()
            conn.close()

            return render_template('article.html', article=article)

        except sqlite3.Error as e:
            print(e)
            return "Error en la conexión a la base de datos"
    else:
        return "Error en la conexión a la base de datos"

@app.route('/search')
def search():
    keyword = request.args.get('keyword', '')

    conn = get_db_connection()
    if conn:
        try:
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM articles WHERE title LIKE ?", ('%' + keyword + '%',))
            articles = cursor.fetchall()

            cursor.close()
            conn.close()

            return render_template('search.html', articles=articles)

        except sqlite3.Error as e:
            print(e)
            return "Error en la conexión a la base de datos"
    else:
        return "Error en la conexión a la base de datos"

@app.route('/create_article_yoezequiel_011358', methods=['GET', 'POST'])
def create_article():
    if request.method == 'POST':
        try:
            title = request.form['title']
            content = request.form['content']
            image = request.files.get('image')  # Usamos get() en lugar de ['image'] para obtener el archivo opcionalmente

            if image:
                # Guardar la imagen en tu sistema de archivos
                image.save('static/images/' + image.filename)

            conn = get_db_connection()
            if conn:
                try:
                    cursor = conn.cursor()

                    # Insertar el artículo en la base de datos
                    cursor.execute("INSERT INTO articles (title, content, image) VALUES (?, ?, ?)",
                                (title, content, image.filename if image else None))
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

    return render_template('create_article.html')

@app.route('/cursos')
def cursos():
    return render_template('cursos.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run()
