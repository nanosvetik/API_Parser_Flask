import requests
import json
from collections import Counter

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
    # Пример, как бы был вызван парсер
    search_text = 'QA OR "Инженер по тестированию" OR Тестировщик'
    experience = 'noExperience'
    schedule = 'remote'
    location = 'Москва'  # Пример местоположения, это может быть пустым

    all_vacancies = fetch_vacancies(search_text, experience, schedule, location)
    filtered_vacancies = filter_vacancies(all_vacancies)
    save_vacancies_to_json(filtered_vacancies)
    analyze_and_save_skills(filtered_vacancies)
