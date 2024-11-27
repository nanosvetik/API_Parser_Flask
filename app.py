from flask import Flask, render_template, request, redirect, url_for
import json
from parser import fetch_vacancies, filter_vacancies, save_vacancies_to_json, analyze_and_save_skills

app = Flask(__name__)

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
