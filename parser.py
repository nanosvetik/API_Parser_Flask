import requests
import json
from collections import Counter
import sqlite3  # Добавляем библиотеку для работы с SQLite

# Базовый URL API hh.ru
DOMAIN = 'https://api.hh.ru/'
URL_VACANCIES = f'{DOMAIN}vacancies'

# Функция для подключения к базе данных
def get_db_connection():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    return conn

# Функция для сохранения данных в базу данных
def save_to_database(vacancies):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Сохранение вакансий
    for vacancy in vacancies:
        # Получение деталей вакансии
        vacancy_detail = requests.get(f"{URL_VACANCIES}/{vacancy['id']}").json()
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

# Базовый URL API hh.ru
DOMAIN = 'https://api.hh.ru/'
URL_VACANCIES = f'{DOMAIN}vacancies'


def fetch_vacancies(search_text, experience, schedule, location=None):
    """
    Получает вакансии по заданным параметрам.
    """
    vacancies = []
    params = {
        'text': search_text,
        'search_field': 'name',
        'experience': experience,
        'schedule': schedule,
        'page': 0,
        'per_page': 50
    }

    if location:  # Если указан город, добавляем его в параметры поиска
        params['area'] = location

    while len(vacancies) < 20:
        response = requests.get(URL_VACANCIES, params=params)
        if response.status_code != 200:
            break

        data = response.json()
        vacancies.extend(data['items'])

        # Если страницы закончились, выходим из цикла
        if params['page'] >= data['pages'] - 1:
            break

        params['page'] += 1

    return vacancies[:20]  # Вернем первые 20 вакансий


def filter_vacancies(vacancies, exclude_employers=None):
    """
    Фильтрует вакансии по работодателям.
    """
    if exclude_employers is None:
        exclude_employers = ['aston']  # Пример исключения работодателя

    filtered_vacancies = [
        vacancy for vacancy in vacancies
        if vacancy.get('employer', {}).get('name', '').lower() not in [e.lower() for e in exclude_employers]
    ]
    return filtered_vacancies


def extract_key_skills(vacancies):
    """
    Извлекает ключевые навыки из каждой вакансии.
    """
    all_skills = []
    for vacancy in vacancies:
        vacancy_detail = requests.get(f"{URL_VACANCIES}/{vacancy['id']}").json()
        key_skills = vacancy_detail.get('key_skills', [])
        all_skills.extend([skill['name'] for skill in key_skills])

    return all_skills


def analyze_and_save_skills(vacancies):
    """
    Анализирует и сохраняет навыки в JSON.
    """
    all_skills = extract_key_skills(vacancies)
    skill_counts = Counter(all_skills)

    # Сортируем навыки по частоте упоминания
    sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)

    skills_data = [{'skill': skill, 'count': count} for skill, count in sorted_skills]

    with open('data/skills.json', 'w', encoding='utf-8') as f:
        json.dump(skills_data, f, ensure_ascii=False, indent=4)

    print("Навыки сохранены в файл data/skills.json")


def save_vacancies_to_json(vacancies):
    """
    Сохраняет список вакансий в файл JSON.
    """
    formatted_vacancies = [
        {
            'name': vacancy['name'],
            'snippet': vacancy['snippet']['responsibility'] if vacancy['snippet'].get('responsibility') else 'Описание не указано',
            'url': vacancy['alternate_url']
        }
        for vacancy in vacancies
    ]

    with open('data/vacancies.json', 'w', encoding='utf-8') as f:
        json.dump(formatted_vacancies, f, ensure_ascii=False, indent=4)

    print("Вакансии сохранены в файл data/vacancies.json")


if __name__ == '__main__':
    search_text = 'QA OR "Инженер по тестированию" OR Тестировщик'
    experience = 'noExperience'
    schedule = 'remote'
    location = 'Москва'

    all_vacancies = fetch_vacancies(search_text, experience, schedule, location)
    filtered_vacancies = filter_vacancies(all_vacancies)

    # Сохранение данных в базу данных
    save_to_database(filtered_vacancies)
    print("Данные успешно сохранены в базу данных!")