# Импорт необходимых модулей и объектов
from flask import render_template, Blueprint, request, redirect, url_for, flash, current_app
from app import db
from math import ceil

# Определение количества записей на страницу
PER_PAGE = 10

# Создание объекта для маршрутизации и установки префикса для URL
bp = Blueprint('visits', __name__, url_prefix='/visits')

# Функция logging() используется для записи сообщений в журнал.
@bp.route('/')
def logging():
    # Получение номера текущей страницы из GET-параметра запроса, либо установка значения по умолчанию
    page = request.args.get('page', 1, type = int)
    # Формирование SQL-запроса на выборку логов с указанием нужных параметров и сортировкой по дате создания в обратном порядке
    query = ('SELECT visit_logs.*, users.login '
            'FROM users RIGHT JOIN visit_logs ON visit_logs.user_id = users.id '
            'ORDER BY created_at DESC LIMIT %s OFFSET %s')
    # Выполнение SQL-запроса и получение данных на основе запроса в объект logs
    with db.connection().cursor(named_tuple=True) as cursor:
        cursor.execute(query, (PER_PAGE, (page-1)*PER_PAGE))
        logs = cursor.fetchall()

    # Формирование SQL-запроса для получения общего количества записей в таблице
    query = 'SELECT COUNT(*) AS count FROM visit_logs'
    # Выполнение SQL-запроса и получение данных на основе запроса в объект count
    with db.connection().cursor(named_tuple=True) as cursor:
        cursor.execute(query)
        count = cursor.fetchone().count
    
    # Вычисление количества страниц на основе общего количества записей и количества записей на странице
    last_page = ceil(count/PER_PAGE)

    # Отображение страницы с логами посещений и передача на нее объектов с данными логов, количеством страниц и номером текущей страницы
    return render_template('visits/logs.html', logs = logs, last_page = last_page, current_page = page)