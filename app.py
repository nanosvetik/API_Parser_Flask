from flask import Flask, render_template, request, redirect, url_for
import json
import sqlite3  # Добавляем библиотеку для работы с SQLite
import requests  # Добавляем импорт requests
from parser import fetch_vacancies, filter_vacancies, save_vacancies_to_json, analyze_and_save_skills

app = Flask(__name__)

# Базовый URL API hh.ru
DOMAIN = 'https://api.hh.ru/'
URL_VACANCIES = f'{DOMAIN}vacancies'

# Функция для подключения к базе данных
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Функция для сохранения данных в базу данных
def save_to_database(vacancies, url_vacancies):
    print("Сохранение данных в базу данных...")  # Отладочное сообщение
    conn = get_db_connection()
    cursor = conn.cursor()

    # Сохранение вакансий
    for vacancy in vacancies:
        # Получение деталей вакансии
        vacancy_detail = requests.get(f"{url_vacancies}/{vacancy['id']}").json()
        key_skills = [skill['name'] for skill in vacancy_detail.get('key_skills', [])]

        # Добавление вакансии в таблицу vacancies
        cursor.execute('''
        INSERT INTO vacancies (title, description, url, location, experience, schedule)
        VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            vacancy['name'],
            vacancy['snippet'].get('responsibility', 'Описание не указано'),
            vacancy['alternate_url'],
            vacancy.get('area', {}).get('name', 'Не указано'),
            vacancy.get('experience', {}).get('name', 'Не указано'),
            vacancy.get('schedule', {}).get('name', 'Не указано')
        ))

        # Получение ID добавленной вакансии
        vacancy_id = cursor.lastrowid

        # Добавление навыков
        for skill_name in key_skills:
            # Проверка, существует ли навык в базе данных
            cursor.execute('SELECT id FROM skills WHERE name = ?', (skill_name,))
            skill_row = cursor.fetchone()

            if skill_row:
                # Если навык уже существует, используем его ID
                skill_id = skill_row[0]
            else:
                # Если навыка нет, добавляем его в базу данных
                cursor.execute('INSERT INTO skills (name) VALUES (?)', (skill_name,))
                skill_id = cursor.lastrowid

            # Связываем вакансию и навык
            cursor.execute('INSERT INTO vacancy_skills (vacancy_id, skill_id) VALUES (?, ?)', (vacancy_id, skill_id))

    # Сохранение изменений и закрытие соединения
    conn.commit()
    conn.close()

    # Вывод данных в консоль
    print_database_data()

# Функция для вывода данных из базы данных в консоль
def print_database_data():
    conn = get_db_connection()
    cursor = conn.cursor()

    # Вывод данных из таблицы vacancies
    print("\n=== Вакансии ===")
    cursor.execute("SELECT * FROM vacancies")
    vacancies = cursor.fetchall()
    for vacancy in vacancies:
        print(f"ID: {vacancy['id']}, Название: {vacancy['title']}, URL: {vacancy['url']}")

    # Вывод данных из таблицы skills
    print("\n=== Навыки ===")
    cursor.execute("SELECT * FROM skills")
    skills = cursor.fetchall()
    for skill in skills:
        print(f"ID: {skill['id']}, Название: {skill['name']}")

    # Вывод данных из таблицы vacancy_skills
    print("\n=== Связи вакансий и навыков ===")
    cursor.execute("SELECT * FROM vacancy_skills")
    vacancy_skills = cursor.fetchall()
    for vs in vacancy_skills:
        print(f"Вакансия ID: {vs['vacancy_id']}, Навык ID: {vs['skill_id']}")

    conn.close()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        # Получение данных из формы
        search_text = request.form.get('jobTitle')  # Используем 'jobTitle' вместо 'text'
        location = request.form.get('location')     # Получаем 'location' (опционально)
        experience = request.form.get('experience') # Получаем 'experience'
        schedule = request.form.get('schedule')     # Получаем 'schedule'

        # Печать полученных данных для проверки
        print(f"Полученные данные: {search_text}, {location}, {experience}, {schedule}")

        # Получение вакансий по указанным параметрам
        all_vacancies = fetch_vacancies(search_text, experience, schedule, location)

        # Фильтрация вакансий
        filtered_vacancies = filter_vacancies(all_vacancies)

        # Сохранение вакансий в файл
        save_vacancies_to_json(filtered_vacancies)

        # Анализ и сохранение навыков
        analyze_and_save_skills(filtered_vacancies)

        # Сохранение данных в базу данных
        save_to_database(filtered_vacancies, URL_VACANCIES)

        # После обработки и сохранения данных перенаправляем на страницу результатов
        return redirect(url_for('results'))

    return render_template('form.html')

@app.route('/results', methods=['GET'])
def results():
    # Чтение вакансий из JSON файла
    with open('data/vacancies.json', 'r', encoding='utf-8') as f:
        vacancies = json.load(f)

    # Чтение навыков из JSON файла
    with open('data/skills.json', 'r', encoding='utf-8') as f:
        skills = json.load(f)

    # Отправка данных в шаблон
    return render_template('results.html', vacancies=vacancies, skills=skills)

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    app.run(debug=True)