import requests
import json
import csv
from collections import Counter

# Базовый URL API
DOMAIN = 'https://api.hh.ru/'

# URL для вакансий
url_vacancies = f'{DOMAIN}vacancies'

# Параметры запроса
params = {
    'text': 'QA OR "Инженер по тестированию" OR Тестировщик',  # Поисковый запрос
    'search_field': 'name',  # Искать только в названии вакансии
    'experience': 'noExperience',  # Без опыта работы
    'schedule': 'remote',  # Удаленная работа
    'page': 0,  # Первая страница
    'per_page': 10  # Количество вакансий на странице (можно увеличить до 100)
}


# Функция для получения всех вакансий
def fetch_all_vacancies(params):
    vacancies = []
    while True:
        response = requests.get(url_vacancies, params=params)
        data = response.json()
        vacancies.extend(data['items'])

        # Проверяем, есть ли следующая страница
        if data['pages'] - 1 > params['page']:
            params['page'] += 1
        else:
            break

    return vacancies


# Фильтруем и сохраняем вакансии
vacancies = fetch_all_vacancies(params)
filtered_vacancies = [
    vacancy for vacancy in vacancies
    if vacancy.get('employer', {}).get('name', '').lower() != 'aston'
]

# Сохраняем данные в JSON
output_file = 'vacancies_filtered.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(filtered_vacancies, f, ensure_ascii=False, indent=4)

print(f"Данные сохранены в файл {output_file}")
print(f"Общее количество найденных вакансий: {len(vacancies)}")
print(f"Количество вакансий после фильтрации: {len(filtered_vacancies)}")


# Функция для извлечения ключевых навыков из всех вакансий
def extract_key_skills(vacancies):
    all_skills = []

    for vacancy in vacancies:
        vacancy_detail = requests.get(f"{url_vacancies}/{vacancy['id']}").json()
        key_skills = vacancy_detail.get('key_skills', [])
        all_skills.extend([skill['name'] for skill in key_skills])

    return all_skills


# Функция для анализа и сохранения навыков
def analyze_key_skills(vacancies):
    all_skills = extract_key_skills(vacancies)
    skill_counts = Counter(all_skills)
    total_skills = sum(skill_counts.values())

    # Сортируем навыки по убыванию
    sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)

    # Вывод в консоль
    print("\nНавыки, упоминаемые в вакансиях:")
    for skill, count in sorted_skills:
        percentage = (count / total_skills) * 100
        print(f"{skill}: {count} / {percentage:.2f}%")

    # Сохранение в CSV
    csv_file = 'skills_analysis.csv'
    with open(csv_file, mode='w', encoding='utf-8', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Навык', 'Количество', 'Процент'])
        for skill, count in sorted_skills:
            percentage = (count / total_skills) * 100
            writer.writerow([skill, count, f"{percentage:.2f}%"])

    print(f"\nАнализ навыков сохранен в файл {csv_file}")

    # Сохранение в JSON
    json_file = 'skills_analysis.json'
    skills_data = [
        {'skill': skill, 'count': count, 'percentage': f"{(count / total_skills) * 100:.2f}%"}
        for skill, count in sorted_skills
    ]
    with open(json_file, mode='w', encoding='utf-8') as file:
        json.dump(skills_data, file, ensure_ascii=False, indent=4)

    print(f"Навыки также сохранены в файл {json_file}")


# Запускаем анализ
analyze_key_skills(filtered_vacancies)
