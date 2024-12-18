import sqlite3

# Функция для создания базы данных и таблиц
def create_database():
    # Подключение к базе данных (если файла нет, он будет создан)
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Создание таблиц
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vacancies (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT,
        url TEXT NOT NULL,
        location TEXT,
        experience TEXT,
        schedule TEXT
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS skills (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS vacancy_skills (
        vacancy_id INTEGER,
        skill_id INTEGER,
        FOREIGN KEY (vacancy_id) REFERENCES vacancies(id),
        FOREIGN KEY (skill_id) REFERENCES skills(id),
        PRIMARY KEY (vacancy_id, skill_id)
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    )
    ''')

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS search_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        query TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )
    ''')

    # Сохранение изменений и закрытие соединения
    conn.commit()
    conn.close()

# Вызов функции для создания базы данных
if __name__ == '__main__':
    create_database()
    print("База данных и таблицы успешно созданы!")