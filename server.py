import os
from flask import Flask, request, render_template, redirect, url_for, session, flash
import sqlite3

app = Flask(__name__)
app.secret_key = os.urandom(24)


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
            return render_template('navbar/authorization.html', error='No such client')

        if pas[0] != password:
            return render_template('navbar/authorization.html', error='Wrong password')

        cursor_db.execute('SELECT role FROM user_profile WHERE login = ?', (login,))
        role = cursor_db.fetchone()[0]

        session['username'] = login
        session['role'] = role

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

        cursor_db.execute('INSERT INTO passwords (login, password) VALUES (?, ?)', (login, password))
        cursor_db.execute('INSERT INTO user_profile (login) VALUES (?)', (login,))

        conn.commit()
        conn.close()

        return redirect(url_for('index'))

    return render_template('navbar/registration.html')


@app.route("/about")
def about():
    return render_template("navbar/about.html")


@app.route("/contact")
def contact():
    return render_template("navbar/contact.html")


@app.route('/')
def index():
    return render_template('main/index.html')


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


def get_db_connection():
    conn = sqlite3.connect('blog.db')
    # Возвращаем строки как "словари"
    conn.row_factory = sqlite3.Row
    return conn


@app.route('/logout')
def logout():
    # Удаляем имя пользователя из сессии (выход из аккаунта)
    session.pop('username', None)
    session.clear()  # Очистка всех данных сессии
    return redirect(url_for('index'))


@app.route("/users")
def get_users():
    conn = get_db_connection()
    users = conn.execute('SELECT * FROM passwords').fetchall()
    conn.close()
    return render_template('users/users.html', users=users)


@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')

        conn = get_db_connection()
        conn.execute('INSERT INTO passwords (password, login) VALUES (?, ?)', (password, login))
        conn.execute('INSERT INTO user_profile (login) VALUES (?)', (login,))
        conn.commit()
        conn.close()

        return redirect(url_for('get_users'))

    return render_template('users/create.html')


@app.route('/users/<string:login>/edit_user', methods=('GET', 'POST'))
def edit_user(login):
    conn = get_db_connection()
    user = conn.execute('SELECT * FROM passwords WHERE login = ?', (login,)).fetchone()

    if request.method == 'POST':
        new_login = request.form.get('login')
        new_password = request.form.get('password')

        conn.execute('UPDATE passwords SET login = ?, password = ? WHERE login = ?',
                     (new_login, new_password, login))

        conn.execute('update user_profile SET login = ? WHERE login =?',
                     (new_login, login))
        conn.commit()
        conn.close()
        return redirect(url_for('get_users'))

    return render_template('users/edit.html', user=user)


@app.route('/user/<string:login>/delete_user', methods=('POST',))
def delete_user(login):
    conn = get_db_connection()
    conn.execute('DELETE FROM passwords WHERE login = ?', (login,))
    conn.execute('DELETE FROM user_profile WHERE login = ?', (login,))
    conn.commit()
    conn.close()
    flash('User has been deleted.')
    return redirect(url_for('get_users'))


@app.route('/tag/<string:name>/edit_tag', methods=('GET', 'POST'))
def edit_tag(name):
    conn = get_db_connection()
    tag = conn.execute('SELECT * FROM tag WHERE name = ?', (name,)).fetchone()

    if request.method == 'POST':
        new_name = request.form.get('name')
        new_description = request.form.get('description')

        conn.execute('UPDATE tag SET name = ?, description = ? WHERE name = ?', (new_name, new_description, name))
        conn.commit()
        conn.close()
        return redirect(url_for('tag'))

    return render_template('tag/edit.html', tag=tag)


@app.route('/tag')
def tag():
    conn = get_db_connection()
    tags = conn.execute('select * from tag').fetchall()
    conn.close()
    return render_template('tag/tag.html', tags=tags)


@app.route('/create_tag', methods=('GET', 'POST'))
def create_tag():
    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')

        conn = get_db_connection()
        conn.execute('INSERT INTO tag (name, description) VALUES (?, ?)', (name, description))
        conn.commit()
        conn.close()

        return redirect(url_for('tag'))

    return render_template('tag/create.html')


@app.route('/tag/<string:name>/delete_tag', methods=('POST',))
def delete_tag(name):
    conn = get_db_connection()
    conn.execute('DELETE FROM tag WHERE name = ?', (name,))
    conn.commit()
    conn.close()
    flash('Tag has been deleted.')
    return redirect(url_for('tag'))


if __name__ == "__main__":
    app.run()
