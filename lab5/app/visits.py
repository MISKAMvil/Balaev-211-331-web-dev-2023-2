# Импорт необходимых модулей и объектов
import io
from flask import render_template, Blueprint, request, send_file
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

# Описание маршрута для Flask приложения
@bp.route('/stat/pages')
# Функция pages_stat() является обработчиком запросов к маршруту /stat/pages
def pages_stat():
    '''Сначала формируется SQL-запрос `query` для получения количества визитов по каждой странице из таблицы `visit_logs`, который затем выполняется и результаты запроса сохраняются в переменной `records`.'''
    # Создание SQL-запроса для получения количества визитов по каждой странице
    query = 'SELECT path, COUNT(*) as count FROM visit_logs GROUP BY path ORDER BY count DESC;'
    # Получение соединения с базой данных и создание курсора для выполнения запроса
    with db.connection().cursor(named_tuple=True) as cursor:
        # Выполнение SQL-запроса
        cursor.execute(query)
        # Получение результатов выполнения запроса
        records = cursor.fetchall()

    '''Затем проверяется наличие параметра 'download_csv' в запросе. Если параметр присутствует, то вызывается функция `generate_report_file()` для создания CSV-файла по данным из `records`, а затем этот файл отправляется пользователю в качестве вложения.'''
    # Проверка наличия параметра 'download_csv' в запросе
    if request.args.get('download_csv'):
        # Создание CSV-файла с результатами выполнения запроса
        f = generate_report_file(records, ['path', 'count'])
        # Отправка файла пользователю как вложения
        return send_file(f, mimetype='text/csv', as_attachment=True, download_name='pages_stat.csv')

    '''Если параметр отсутствует, то происходит отправка шаблона страницы 'visits/pages_stat.html', в котором отображается статистика посещений всех страниц, полученная из `records`.'''
    # Отправка шаблона страницы со статистикой посещений
    return render_template('visits/pages_stat.html', records=records)
