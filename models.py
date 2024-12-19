from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# Инициализация SQLAlchemy
db = SQLAlchemy()

# Модель пользователя
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    search_history = db.relationship('SearchHistory', backref='user', lazy=True)

# Модель региона
class Region(db.Model):
    __tablename__ = 'regions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    vacancies = db.relationship('Vacancy', backref='region', lazy=True)

# Модель вакансии
class Vacancy(db.Model):
    __tablename__ = 'vacancies'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    url = db.Column(db.String(255), nullable=False)
    location_id = db.Column(db.Integer, db.ForeignKey('regions.id'), nullable=True)
    experience = db.Column(db.String(100), nullable=True)
    schedule = db.Column(db.String(100), nullable=True)
    skills = db.relationship('Skill', secondary='vacancy_skills', backref='vacancies', lazy=True)

# Модель навыка
class Skill(db.Model):
    __tablename__ = 'skills'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

# Связь между вакансиями и навыками (многие ко многим)
class VacancySkill(db.Model):
    __tablename__ = 'vacancy_skills'
    vacancy_id = db.Column(db.Integer, db.ForeignKey('vacancies.id'), primary_key=True)
    skill_id = db.Column(db.Integer, db.ForeignKey('skills.id'), primary_key=True)

# Модель истории поиска
class SearchHistory(db.Model):
    __tablename__ = 'search_history'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    query = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)  # Используем datetime.utcnow