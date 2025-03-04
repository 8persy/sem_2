import os
from flask import Flask, request, render_template, redirect, url_for, session, flash
import sqlite3
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.urandom(24)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


# functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_db_connection():
    conn = sqlite3.connect('blog.db')
    # Возвращаем строки как "словари"
    conn.row_factory = sqlite3.Row
    return conn


def get_all_tags():
    conn = get_db_connection()
    tags = conn.execute('select name from tags').fetchall()

    return tags


# auth and registration
@app.route('/authorization', methods=['GET', 'POST'])
def auth():
    if request.method == 'POST':
        login = request.form.get('Login')
        password = request.form.get('Password')

        db_lp = sqlite3.connect('blog.db')
        cursor_db = db_lp.cursor()
        cursor_db.execute('''SELECT password FROM passwords WHERE login = ?;''',
                          (login, ))

        pas = cursor_db.fetchone()

        if not pas:
            return render_template('navbar/authorization.html', error='Несуществующий клиент')

        if pas[0] != password:
            return render_template('navbar/authorization.html', error='Неправильный пароль')

        cursor_db.execute('SELECT role FROM user_profile WHERE login = ?', (login,))
        role = cursor_db.fetchone()[0]

        cursor_db.execute('SELECT user_id FROM user_profile WHERE login = ?', (login,))
        user_id = cursor_db.fetchone()[0]

        session['username'] = login
        session['role'] = role
        session['user_id'] = user_id
        session.permanent = True

        db_lp.close()

        return redirect(url_for('index'))

    return render_template('navbar/authorization.html')


@app.route('/registration', methods=['GET', 'POST'])
def form_registration():
    if request.method == 'POST':
        login = request.form.get('Login')
        password = request.form.get('Password')

        conn = sqlite3.connect('blog.db')
        cursor_db = conn.cursor()

        try:
            cursor_db.execute('INSERT INTO passwords (login, password) VALUES (?, ?)', (login, password))
            cursor_db.execute('INSERT INTO user_profile (login) VALUES (?)', (login,))
        except Exception as e:
            print(e)
            return render_template('navbar/registration.html', error='Такой пользователь уже существует')

        cursor_db.execute('SELECT role FROM user_profile WHERE login = ?', (login,))
        role = cursor_db.fetchone()[0]

        cursor_db.execute('SELECT user_id FROM user_profile WHERE login = ?', (login,))
        user_id = cursor_db.fetchone()[0]

        session['username'] = login
        session['role'] = role
        session['user_id'] = user_id
        session.permanent = True

        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('navbar/registration.html')


# navbar
@app.route("/about")
def about():
    return render_template("navbar/about.html")


@app.route("/contact")
def contact():
    return render_template("navbar/contact.html")


@app.route('/')
def index():
    conn = get_db_connection()

    posts_data = conn.execute('''
                SELECT
                    posts.post_id,
                    posts.title,
                    posts.content,
                    posts.image_path,
                    user_profile.login,
                    posts.user_id,
                    GROUP_CONCAT(tags.name, ', ') AS tags -- Группируем теги через запятую
                FROM posts
                INNER JOIN user_profile ON posts.user_id = user_profile.user_id
                LEFT JOIN post_tags ON posts.post_id = post_tags.post_id
                LEFT JOIN tags ON post_tags.tag_id = tags.id
                GROUP BY posts.post_id -- Группируем данные по ID поста
            ''').fetchall()

    conn.close()
    return render_template('main/index.html', posts=posts_data)


# account
@app.route('/account', methods=('GET', 'POST'))
def account():
    conn = get_db_connection()
    login = session['username']
    user = conn.execute('SELECT * FROM user_profile WHERE login = ?', (login,)).fetchone()

    name = user['name']
    email = user['email']

    if not name:
        name = 'Введите имя'
    if not email:
        email = 'Введите email'

    if request.method == 'POST':
        new_email = request.form.get('email')
        new_name = request.form.get('name')

        conn.execute('update user_profile set email = ?, name = ? where login = ?',
                     (new_email, new_name, login))

        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('account/account.html', name=name, email=email)


@app.route('/logout')
def logout():
    session.pop('username', None)
    session.clear()
    return redirect(url_for('index'))


# users
@app.route("/users")
def get_users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM passwords').fetchall()
    conn.close()
    return render_template('users/users.html', users=users)


@app.route('/create', methods=('GET', 'POST'))
def create_user():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')
        role = request.form.get('role')

        if not role:
            role = "user"

        conn = get_db_connection()
        conn.execute('INSERT INTO passwords (password, login) VALUES (?, ?)', (password, login))
        conn.execute('INSERT INTO user_profile (login, role) VALUES (?, ?)', (login, role))
        conn.commit()
        conn.close()

        return redirect(url_for('get_users'))

    return render_template('users/create.html')


@app.route('/users/<string:login>/edit_user', methods=('GET', 'POST'))
def edit_user(login):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM passwords WHERE login = ?', (login,)).fetchone()
    role = conn.execute('SELECT role FROM user_profile WHERE login = ?', (login,)).fetchone()

    if request.method == 'POST':
        new_login = request.form.get('login')
        new_password = request.form.get('password')
        new_role = request.form.get('role')

        conn.execute('UPDATE passwords SET login = ?, password = ? WHERE login = ?',
                     (new_login, new_password, login))

        conn.execute('update user_profile SET login = ?, role = ? WHERE login =?',
                     (new_login, new_role, login))
        conn.commit()
        conn.close()
        return redirect(url_for('get_users'))

    return render_template('users/edit.html', user=user, role=role)


@app.route('/user/<string:login>/delete_user', methods=('POST',))
def delete_user(login):
    conn = get_db_connection()
    conn.execute('DELETE FROM passwords WHERE login = ?', (login,))
    conn.execute('DELETE FROM user_profile WHERE login = ?', (login,))
    conn.commit()
    conn.close()
    return redirect(url_for('get_users'))


# user's posts
@app.route('/user_posts')
def get_user_posts():
    conn = get_db_connection()

    posts_data = conn.execute('''
              SELECT
                  posts.post_id,
                  posts.title,
                  posts.content,
                  posts.image_path,
                  user_profile.login,
                  GROUP_CONCAT(tags.name, ', ') AS tags
              FROM posts
              INNER JOIN user_profile ON posts.user_id = user_profile.user_id
              LEFT JOIN post_tags ON posts.post_id = post_tags.post_id
              LEFT JOIN tags ON post_tags.tag_id = tags.id
              WHERE user_profile.login = ?
              GROUP BY posts.post_id, user_profile.login
          ''', (session['username'],)).fetchall()

    conn.close()
    return render_template('user_posts/user_posts.html', posts=posts_data)


@app.route('/create_user_post', methods=('GET', 'POST'))
def create_user_post():
    if request.method == 'POST':
        # Получение данных из формы
        title = request.form.get('title')
        content = request.form.get('content')
        # ID тега из выпадающего списка
        selected_tags = request.form.getlist('tags')  # Получаем список выбраных тегов
        user_id = session['user_id']
        file = request.files.get('image')  # Получение загружаемого файла

        image_path = None
        if file and allowed_file(file.filename):
            safe_filename = secure_filename(file.filename)

            upload_path = f'static/uploads/{safe_filename}'

            file.save(upload_path)

            image_path = upload_path

        try:
            conn = sqlite3.connect('blog.db')
            cursor = conn.cursor()

            cursor.execute('''
                    INSERT INTO posts (user_id, title, content, image_path)
                    VALUES (?, ?, ?, ?)''',
                           (user_id, title, content, image_path))

            post_id = cursor.lastrowid  # Получаем ID созданного поста

            # Добавляем теги для поста в таблицу post_tags
            for tag_id in selected_tags:
                cursor.execute('''
                                            INSERT INTO post_tags (post_id, tag_id)
                                            VALUES (?, ?)
                                        ''', (post_id, tag_id))

            conn.commit()
            conn.close()

            return redirect(url_for('get_user_posts'))
        except Exception as e:
            flash(f'Ошибка при добавлении поста: {str(e)}', 'danger')

    conn = get_db_connection()
    tags = conn.execute('SELECT id, name FROM tags').fetchall()
    conn.close()

    return render_template('user_posts/create_user_post.html', tags=tags)


@app.route('/user_posts/<string:post_id>/edit_post', methods=('GET', 'POST'))
def edit_post(post_id):
    conn = get_db_connection()
    post = conn.execute('select * FROM posts WHERE post_id = ?',
                        (post_id,)).fetchone()

    if request.method == 'POST':
        new_title = request.form.get('title')
        new_content = request.form.get('content')
        new_image_path = request.files.get('img')

        if new_image_path and allowed_file(new_image_path.filename):
            safe_filename = secure_filename(new_image_path.filename)

            upload_path = f'static/uploads/{safe_filename}'

            new_image_path = upload_path
        else:
            new_image_path = post['image_path']

        conn.execute('UPDATE posts SET title = ?, content = ?, image_path = ? WHERE post_id = ?',
                     (new_title, new_content, new_image_path, post_id))
        conn.commit()
        conn.close()

        return redirect(url_for('get_user_posts'))

    return render_template('user_posts/edit_user_post.html', post=post)


@app.route('/user_posts/<string:post_id>/<string:place>/delete_post', methods=('POST', ))
def delete_post(post_id, place):
    print(post_id, '\n', place)
    conn = get_db_connection()
    conn.execute('delete from posts WHERE post_id = ?',
                 (post_id, ))
    conn.commit()
    conn.close()

    if place == 'posts':
        return redirect(url_for('get_user_posts'))
    else:
        return redirect(url_for('index'))


# tags
@app.route('/tag')
def tag():
    conn = get_db_connection()
    tags = conn.execute('select * from tags').fetchall()
    conn.close()
    return render_template('tag/tag.html', tags=tags)


@app.route('/tag/<string:name>/edit_tag', methods=('GET', 'POST'))
def edit_tag(name):
    conn = get_db_connection()
    tag = conn.execute('SELECT * FROM tags WHERE name = ?', (name,)).fetchone()

    if request.method == 'POST':
        new_name = request.form.get('name')
        # new_description = request.form.get('description')

        conn.execute('UPDATE tags SET name = ? WHERE name = ?',
                     (new_name, name))
        conn.commit()
        conn.close()
        return redirect(url_for('tag'))

    return render_template('tag/edit.html', tag=tag)


@app.route('/create_tag', methods=('GET', 'POST'))
def create_tag():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')

        conn = get_db_connection()
        conn.execute('INSERT INTO tags (name) VALUES (?)', (name,))
        conn.commit()
        conn.close()

        return redirect(url_for('tag'))

    return render_template('tag/create.html')


@app.route('/tag/<string:name>/delete_tag', methods=('POST',))
def delete_tag(name):
    conn = get_db_connection()
    conn.execute('DELETE FROM tags WHERE name = ?', (name,))
    conn.commit()
    conn.close()
    return redirect(url_for('tag'))


@app.route('/comments/<post_id>/<user_id>', methods=('GET', 'POST'))
def comments(post_id, user_id):
    conn = get_db_connection()

    if request.method == 'POST':
        author = session.get('username')
        text = request.form.get('comment')

        if not author:
            author = 'Anonymous'

        conn.execute('INSERT INTO comments (author, text, post_id, user_id) VALUES (?, ?, ?, ?)',
                     (author, text, post_id, user_id))

        conn.commit()

    comments = conn.execute('select * from comments where post_id = ?',
                            (post_id,)).fetchall()

    return render_template('comments/comments.html', comments=comments)


@app.route('/comments/<id>', methods=('POST', ))
def delete_comment(id):
    conn = get_db_connection()
    conn.execute('delete from comments where id = ?', (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
