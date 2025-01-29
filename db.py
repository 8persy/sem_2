import sqlite3

conn = sqlite3.connect('blog.db')
cursor = conn.cursor()
# sql_create = '''CREATE TABLE passwords(
# login TEXT PRIMARY KEY,
# password TEXT NOT NULL);'''
# cursor.execute(sql_create)

# cursor.execute('''drop table user_profile''')
# cursor.execute('''drop table passwords''')
# cursor.execute('''drop table tag''')


# добавление столбца
# Убирая NOT NULL, вы позволяете столбцу role принимать значения NULL, что означает, что значение может быть "пустым" (неопределенным).
# cursor.execute('''ALTER TABLE passwords ADD COLUMN role TEXT''')

# sql_create = '''CREATE TABLE tag(
# name TEXT PRIMARY KEY,
# description TEXT not null
# );'''
# cursor.execute(sql_create)
#
# cursor.execute('''
#                 CREATE TABLE IF NOT EXISTS passwords(
#                 login TEXT PRIMARY KEY,
#                 password TEXT NOT NULL)
# ''')
# cursor.execute('drop table passwords')
# удаление столбца
# cursor.execute('''ALTER TABLE passwords DROP COLUMN role''')


# FOREIGN KEY (user_id)
# Эта часть указывает, что поле user_id в текущей таблице (таблице, где применяется это ограничение) является внешним ключом.
# Внешний ключ определяет, что значения в колонке user_id должны ссылаться на существующие значения в другой таблице.
# REFERENCES users (login)
# Это значит, что внешнее ключевое поле user_id указывает на поле login в таблице users. Таким образом, оно устанавливает
# связь между текущей таблицей и таблицей users. Значение в колонке user_id должно соответствовать значению, существующему
# в колонке login в таблице users.
# ON DELETE CASCADE
# Это поведение, задающее, что произойдет с записями в текущей таблице, если запись, на которую они ссылаются, будет удалена
# в таблице users.
# В данном случае, ON DELETE CASCADE означает, что если запись в таблице users с указанным значением login будет удалена,
# то все записи в текущей таблице, которые ссылаются на нее через внешние ключи (т. е. через поле user_id), также будут
# автоматически удалены. Таким образом, это помогает поддерживать целостность данных: система автоматически удаляет связанные
# записи, чтобы не осталось "висячих" ссылок.

# cursor.execute('''
#             CREATE TABLE IF NOT EXISTS posts (
#                 id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 user_id INTEGER,
#                 title TEXT NOT NULL,
#                 body TEXT NOT NULL,
#                 FOREIGN KEY (user_id) REFERENCES users (login) ON DELETE CASCADE
#             )
#         ''')

# cursor.execute('''
#             CREATE TABLE user_profile (
#                 user_id INTEGER PRIMARY KEY AUTOINCREMENT, -- Уникальный ID пользователя
#                 name TEXT, -- Имя пользователя
#                 email TEXT, -- Email пользователя
#                 login TEXT, -- Логин, связанный с таблицей passwords
#                 FOREIGN KEY (login) REFERENCES passwords(login) ON DELETE CASCADE ON UPDATE CASCADE
# )
# ''')
# cursor.execute('''ALTER TABLE user_profile add COLUMN role text default 'user' ''')

cursor.execute('''
            CREATE TABLE IF NOT EXISTS post_tags (
                post_id INTEGER NOT NULL,
                tag_id INTEGER NOT NULL,
                FOREIGN KEY (post_id) REFERENCES posts (post_id) ON DELETE CASCADE,
                FOREIGN KEY (tag_id) REFERENCES tags (id) ON DELETE CASCADE,
                PRIMARY KEY (post_id, tag_id)
            )
''')
# cursor.execute('''
#                     CREATE TABLE IF NOT EXISTS posts (
#                     post_id INTEGER PRIMARY key AUTOINCREMENT,
#                     user_id INTEGER,
#                     title text not null,
#                     content text not null,
#                     image_path text,
#                     tags text,
#                     foreign key (user_id) references user_profile (user_id) on delete cascade)
# ''')

conn.commit()
conn.close()
