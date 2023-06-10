# Импорт необходимых модулей и объектов
import io
from flask import render_template, Blueprint, request, send_file
from app import db, app
from math import ceil
from flask_login import current_user, login_required

# Определение количества записей на страницу
PER_PAGE = 10

# Создание объекта для маршрутизации и установки префикса для URL
bp = Blueprint('visits', __name__, url_prefix='/visits')

# Импортирует декоратор
from auth import permission_check, init_login_manager

init_login_manager(app)

@bp.route('/')
@login_required
def logging():
    page = request.args.get('page', 1, type = int)
    if current_user.can('show_logs'):
        query = ('SELECT visit_logs.*, users.login '
                'FROM users RIGHT JOIN visit_logs ON visit_logs.user_id = users.id '
                'ORDER BY created_at DESC LIMIT %s OFFSET %s')
        with db.connection().cursor(named_tuple=True) as cursor:
            cursor.execute(query, (PER_PAGE, (page-1)*PER_PAGE))
            logs = cursor.fetchall()

        query = 'SELECT COUNT(*) AS count FROM visit_logs'
        with db.connection().cursor(named_tuple=True) as cursor:
            cursor.execute(query)
            count = cursor.fetchone().count
    else:
        query = ('SELECT visit_logs.*, users.login '
                'FROM visit_logs RIGHT JOIN users ON visit_logs.user_id = users.id WHERE users.id=%s '
                'ORDER BY created_at DESC LIMIT %s OFFSET %s')
        with db.connection().cursor(named_tuple=True) as cursor:
            cursor.execute(query, (current_user.id, PER_PAGE, (page-1)*PER_PAGE))
            logs = cursor.fetchall()

        query = 'SELECT COUNT(*) AS count FROM visit_logs WHERE visit_logs.user_id = %s'
        with db.connection().cursor(named_tuple=True) as cursor:
            cursor.execute(query, (current_user.id, ))
            count = cursor.fetchone().count
    
    last_page = ceil(count/PER_PAGE)

    if request.args.get('download_csv'):
        query = ('SELECT visit_logs.*, users.login '
                 'FROM users RIGHT JOIN visit_logs ON visit_logs.user_id = users.id '
                 'ORDER BY created_at DESC')
        with db.connection().cursor(named_tuple=True) as cursor:
            cursor.execute(query)
            records = cursor.fetchall()
        f = generate_report_file(records, ['path', 'login', 'created_at'])
        return send_file(f, mimetype='text/csv', as_attachment=True, download_name='logs.csv')

    return render_template('visits/logs.html', logs = logs, last_page = last_page, current_page = page, PER_PAGE=PER_PAGE)


# Функция generate_report_file() предназначена для преобразования списка записей `records` в CSV-файл, содержащий данные об этих записях.
# Функция принимает два параметра:
# - `records` - список записей, которые необходимо преобразовать в CSV формат
# - `fields` - список полей, которые должны быть включены в CSV файл.
def generate_report_file(records, fields):
    '''Сначала создаем заголовок CSV файла, который содержит перечисление всех полей, отделенных запятыми и с префиксом "№". Затем мы итерируемся по каждой записи `record` в списке `records` и добавляем соответствующие значения полей в CSV файл, разделив каждое поле запятой. Для этого мы используем функцию `getattr()`, которая позволяет получить значение поля объекта записи по его имени.'''
    # Создаем заголовок CSV файла
    csv_content = '№, ' + ', '.join(fields) + '\n'
    # Обходим список записей (records), добавляем значение полей в CSV файл
    for i, record in enumerate(records):
        values = [str(getattr(record, f, '')) for f in fields]
        csv_content += f'{i+1}, ' + ', '.join(values) + '\n'
    '''После того как все записи добавлены в CSV файл, мы оборачиваем его в объект буфера `io.BytesIO()`, записываем в него данные и перематываем его в начало (`f.seek(0)`), чтобы иметь возможность прочитать файл позднее, если это потребуется. Наконец, мы возвращаем объект буфера с содержимым CSV файла для дальнейшего использования в коде.'''
    # Создаем объект буфера и записываем в него данные CSV файла
    f = io.BytesIO()
    f.write(csv_content.encode('utf-8'))
    f.seek(0)
    # Возвращаем объект буфера с содержимым CSV файла
    return f

@bp.route('/stat/pages')
@login_required
@permission_check('show_statistics')
def pages_stat():
    # Получение номера текущей страницы из GET-параметра запроса, либо установка значения по умолчанию
    page = request.args.get('page', 1, type=int)
    # Формирование SQL-запроса на выборку страниц и их частоты посещений, сортировка по убыванию частоты посещений
    query = 'SELECT path, COUNT(*) as count FROM visit_logs GROUP BY path ORDER BY count DESC LIMIT %s OFFSET %s'
    with db.connection().cursor(named_tuple=True) as cursor:
        cursor.execute(query, (PER_PAGE, (page-1)*PER_PAGE))
        records = cursor.fetchall()

    # Формирование SQL-запроса для получения общего количества записей в таблице
    query = 'SELECT COUNT(*) AS count FROM (SELECT path FROM visit_logs GROUP BY path) AS paths'
    with db.connection().cursor(named_tuple=True) as cursor:
        cursor.execute(query)
        count = cursor.fetchone().count

    # Вычисление количества страниц на основе общего количества записей и количества записей на странице
    last_page = ceil(count/PER_PAGE)

    if request.args.get('download_csv'):
        query = 'SELECT path, COUNT(*) as count FROM visit_logs GROUP BY path ORDER BY count DESC'
        with db.connection().cursor(named_tuple=True) as cursor:
            cursor.execute(query)
            records = cursor.fetchall()
        f = generate_report_file(records, ['path', 'count'])
        return send_file(f, mimetype='text/csv', as_attachment=True, download_name='pages_stat.csv')
    # Отображение шаблона pages_stat.html и передача на него объекта с данными страниц, удовлетворяющих запросу,
    # а также объектов с количеством страниц и номером текущей страницы
    return render_template('visits/pages_stat.html', records=records, last_page=last_page, current_page=page, PER_PAGE=PER_PAGE)

# -------------------------------------------------------------------------

@bp.route('/stat/users')
@login_required
@permission_check('show_statistics')
def users_stat():
    page = request.args.get('page', 1, type=int)

    query = ('SELECT users.first_name, users.last_name, users.middle_name, COUNT(visit_logs.id) AS count '
            'FROM users RIGHT JOIN visit_logs ON users.id = visit_logs.user_id '
            'GROUP BY users.login ORDER BY count DESC;')
    with db.connection().cursor(named_tuple=True) as cursor:
        cursor.execute(query)
        records = cursor.fetchall()

    query = 'SELECT COUNT(DISTINCT user_id) as count FROM visit_logs;'
    with db.connection().cursor(named_tuple=True) as cursor:
        cursor.execute(query)
        count = cursor.fetchone().count
    last_page = ceil(count/PER_PAGE)

    if request.args.get('download_csv'):
        f = generate_report_file(records, ['first_name', 'last_name', 'middle_name', 'count'])
        return send_file(f, mimetype='text/csv', as_attachment=True, download_name='users_stat.csv')
    return render_template('visits/users_stat.html', records=records, last_page=last_page, current_page=page, PER_PAGE=PER_PAGE)