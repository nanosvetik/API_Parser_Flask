from flask import Flask, render_template, request, redirect, url_for
from models import db, Region, Vacancy, Skill, VacancySkill
from parser import fetch_vacancies, filter_vacancies
import requests

app = Flask(__name__)

# Настройка подключения к базе данных с абсолютным путём
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/avemy/PycharmProjects/pythonProject/API_Parser_Flask/myalchemy.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Базовый URL API hh.ru
DOMAIN = 'https://api.hh.ru/'
URL_VACANCIES = f'{DOMAIN}vacancies'

# Функция для сохранения данных в базу данных через ORM
def save_to_database(vacancies):
    print("Сохранение данных в базу данных...")  # Отладочное сообщение

    for vacancy in vacancies:
        # Получение деталей вакансии
        vacancy_detail = fetch_vacancy_detail(vacancy['id'])
        key_skills = [skill['name'] for skill in vacancy_detail.get('key_skills', [])]

        # Создание или получение региона
        region = Region.query.filter_by(name=vacancy['area']['name']).first()
        if not region:
            region = Region(name=vacancy['area']['name'])
            db.session.add(region)

        # Создание вакансии
        new_vacancy = Vacancy(
            title=vacancy['name'],
            description=vacancy['snippet'].get('responsibility', 'Описание не указано'),
            url=vacancy['alternate_url'],
            location_id=region.id,
            experience=vacancy['experience']['name'],
            schedule=vacancy['schedule']['name']
        )
        db.session.add(new_vacancy)
        db.session.commit()  # Коммитим, чтобы получить ID вакансии

        # Создание или получение навыков
        for skill_name in key_skills:
            skill = Skill.query.filter_by(name=skill_name).first()
            if not skill:
                skill = Skill(name=skill_name)
                db.session.add(skill)
                db.session.commit()  # Коммитим, чтобы получить ID навыка

            # Связываем вакансию и навык
            db.session.add(VacancySkill(vacancy_id=new_vacancy.id, skill_id=skill.id))

    # Сохранение изменений
    db.session.commit()
    print("Данные успешно сохранены в базу данных!")

# Функция для получения деталей вакансии
def fetch_vacancy_detail(vacancy_id):
    url = f"{URL_VACANCIES}/{vacancy_id}"
    response = requests.get(url)
    return response.json()

# Функция для вывода данных из базы данных в консоль
def print_database_data():
    print("\n=== Вакансии ===")
    vacancies = Vacancy.query.all()
    for vacancy in vacancies:
        print(f"ID: {vacancy.id}, Название: {vacancy.title}, URL: {vacancy.url}")

    print("\n=== Навыки ===")
    skills = Skill.query.all()
    for skill in skills:
        print(f"ID: {skill.id}, Название: {skill.name}")

    print("\n=== Связи вакансий и навыков ===")
    vacancy_skills = VacancySkill.query.all()
    for vs in vacancy_skills:
        print(f"Вакансия ID: {vs.vacancy_id}, Навык ID: {vs.skill_id}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/form', methods=['GET', 'POST'])
def form():
    if request.method == 'POST':
        # Получение данных из формы
        search_text = request.form.get('jobTitle')
        location = request.form.get('location')
        experience = request.form.get('experience')
        schedule = request.form.get('schedule')

        # Печать полученных данных для проверки
        print(f"Полученные данные: {search_text}, {location}, {experience}, {schedule}")

        # Получение вакансий по указанным параметрам
        all_vacancies = fetch_vacancies(search_text, experience, schedule, location)

        # Фильтрация вакансий
        filtered_vacancies = filter_vacancies(all_vacancies)

        # Сохранение данных в базу данных
        save_to_database(filtered_vacancies)

        # После обработки и сохранения данных перенаправляем на страницу результатов
        return redirect(url_for('results'))

    return render_template('form.html')

@app.route('/results', methods=['GET'])
def results():
    # Выборка данных из базы данных
    vacancies = Vacancy.query.all()
    skills = Skill.query.all()

    # Отправка данных в шаблон
    return render_template('results.html', vacancies=vacancies, skills=skills)

@app.route('/contact')
def contact():
    return render_template('contact.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Создаем таблицы, если их нет
        print_database_data()  # Печатаем данные из базы в консоль
    app.run(debug=True)
