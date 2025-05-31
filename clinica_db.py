import sqlite3

conn = sqlite3.connect('user_info.db')
c = conn.cursor()

c.execute("""create table if not exists users
 (id integer primary key autoincrement,
  username text not null,
   age integer, 
   date text, 
   time text,
   reason text
)""")

conn.commit()

def add_user(username):
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    existing_user = c.fetchone()
    if existing_user:
        print(f'Пользователь {username} уже существует')
        return False
    else:
        c.execute('INSERT INTO users (username) VALUES(?)', (username,))
        conn.commit()
        return True

def delete_user(username):
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    existing_user = c.fetchone()
    if existing_user:
        c.execute("DELETE FROM users WHERE username = ?", (username,))
        conn.commit()
        print(f'Пользователь {username} удалён')
        return True
    else:
        print(f"Пользователя {username} не существует")

def get_all_users():
    c.execute("SELECT * FROM users")
    print( c.fetchall())

def get_user_by_name(username):
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    c.fetchone()
    print("User {} was selected".format(username))


def update_user_age(username, new_age):
    c.execute("UPDATE users SET age = ? WHERE username = ?", (new_age, username))
    conn.commit()



if __name__ == '__main__':
    add_user('Ivan')

    get_all_users()

    update_user_age('Ayur', 16)

    get_user_by_name('Ivan')

    delete_user("Ayur")


#c.execute("INSERT INTO users (username, age) VALUES (?, ?)", ('john', '18'))
#c.execute("DROP TABLE IF EXISTS USERS")
# users = [('Bob', '30','13.05.2025', '13:00', 'protes'), ('Alex', '17', '15.05.2025', '14:00', 'consul')]
# c.executemany("INSERT INTO users (username, age, date, time, reason) VALUES (?, ?, ?, ?, ?)", users)
# conn.commit()


# c.execute("SELECT * FROM users")
