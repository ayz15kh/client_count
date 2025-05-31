import sqlite3
conn = sqlite3.connect('books.db')
c = conn.cursor()

c.execute("""create table if not exists books (
    id integer primary key autoincrement,
    title text not null unique,
    author text,
    year integer
)""")

conn.commit()

def add_book(title, author, year):
    c.execute('INSERT INTO books (title, author, year) VALUES (?, ?, ?)',(title, author, year))
    conn.commit()
    print(f'Книга "{title}" добавлена')

def get_all_books():
    c.execute('SELECT * FROM books')
    books = c.fetchall()
    return books

def find_book_by_title(title):
    c.execute('SELECT * FROM books WHERE title = ?', (title,))
    book = c.fetchone()
    return book

def delete_book(title):
    c.execute("DELETE FROM books WHERE title = ?", (title,))
    conn.commit()
    print(f'Книга "{title}" удалена')

if __name__ == "__main__":
    # add_book('Мастер и Маргарита', 'Михаил Булгаков', 1940)
    # add_book('Вишневый сад', 'Антон Чехов', 1941)
    # add_book('Евгений Онегин', 'Александр Пушкин', 1042)
    #add_book('Война и мир', 'Лев Толстой', 1023)

    # print("Список всех книг:")
    # books = get_all_books()
    # for i in books:
    #     print(i)

    delete_book('Мастер и Маргарита')
    delete_book('Вишневый сад')

    print("Список книг после удаления:")
    books = get_all_books()
    for i in books:
        print(i)
