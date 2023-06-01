from flask import Flask, render_template, session, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from mysql_db import MySQL
import mysql.connector

# Ограничение на список параметров для извлечения
PERMITED_PARAMS = ['login', 'password', 'last_name', 'first_name', 'middle_name', 'role_id']
# Список параметров разрешенных для редактирования
EDIT_PARAMS = ['last_name', 'first_name', 'middle_name', 'role_id']

app = Flask(__name__)
# Создаем экземпляр приложения
application = app
# Пишем, чтобы на хостинге всё запускалось

# Нужен секретный ключ, чтобы работать с сессией. Сам ключ генерируем в отдельном файле и импортируем его.
app.config.from_pyfile('config.py')

# Создаем объект класса MySQL
db = MySQL(app)

login_manager = LoginManager()
# Создан экземпляр класса
login_manager.init_app(app)
# Даем приложению знать о существования логин менеджера

login_manager.login_view = 'login'
login_manager.login_message = 'Для доступа к этой странице нужно авторизироваться.'
login_manager.login_message_category = 'warning'

class User(UserMixin):
    def __init__(self, user_id, user_login):
        self.id = user_id
        self.login = user_login

# Главная страничка
@app.route('/')
def index():
    return render_template('index.html')

# Страница c аутентификация пользователей
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form['login']
        password = request.form['password']
        remember = request.form.get('remember_me') == 'on'

        # SQL-запрос к базе данных, пароль хешируется предварительно
        query = 'SELECT * FROM users WHERE login = %s and password_hash = SHA2(%s, 256);'
        
        # 1' or '1' = '1' LIMIT 1#
        # user'#
        # query = f"SELECT * FROM users WHERE login = '{login}' and password_hash = SHA2('{password}', 256);"

        # C помощью with можно не закрывать cursor как делали это в load_user, это будет сделано автоматически
        with db.connection().cursor(named_tuple=True) as cursor:
            # Подставляем в верхний запрос (под %s) при помощи метода execute(принимает аргумен-запрос, передаем кортеж(tuple) со значениями)
            cursor.execute(query, (login, password)) # кортеж с одним элементом мохдается благодаря ЗАПЯТОЙ на конце, иначе работать не будет
            # print(cursor.statement) - ввыводит какой запрос был выполнен в БД
            print(cursor.statement)
            # Метод fetchone() возвращает либо None, если результат пустой, либо кортеж с найденной записью, если что-то нашлось
            user = cursor.fetchone()

        if user:
            login_user(User(user.id, user.login), remember = remember)
            flash('Вы успешно прошли аутентификацию!', 'success')
            param_url = request.args.get('next')
            return redirect(param_url or url_for('index'))
        flash('Введён неправильный логин или пароль.', 'danger')
    return render_template('login.html')

# Страничка с пользователями
@app.route('/users')
def users():
    # SQL-запрос к базе данных, вывод всех пользователей
    query = 'SELECT users.*, roles.name AS role_name FROM users LEFT JOIN roles ON roles.id = users.role_id'
    # C помощью with можно не закрывать cursor как делали это в load_user, это будет сделано автоматически
    with db.connection().cursor(named_tuple=True) as cursor:
        # Подставляем в верхний запрос при помощи метода execute(принимает аргумен-запрос, передаем кортеж(tuple) со значениями)
        cursor.execute(query) # кортеж с одним элементом мохдается благодаря ЗАПЯТОЙ на конце, иначе работать не будет
        # print(cursor.statement) - ввыводит какой запрос был выполнен в БД
        print(cursor.statement)
        # Метод fetchall() возвращает список с кортежами, если результатов нет, то вернется пустой список
        users_list = cursor.fetchall()
    return render_template('users.html', users_list=users_list)

# Страничка с добавлением пользователя
@app.route('/users/new')
@login_required # для того, чтобы только авторизованный пользователь мог отправить данные по этому руту
def users_new():
    roles_list = load_roles()
    return render_template('users_new.html', roles_list=roles_list, user={})

# Функция, которая загружает данные ролей из БД
def load_roles():
    # SQL-запрос к базе данных, вывод всех пользователей
    query = 'SELECT * FROM roles'
    # C помощью with можно не закрывать cursor как делали это в load_user, это будет сделано автоматически
    with db.connection().cursor(named_tuple=True) as cursor:
        # Подставляем в верхний запрос при помощи метода execute(принимает аргумен-запрос, передаем кортеж(tuple) со значениями)
        cursor.execute(query) # кортеж с одним элементом мохдается благодаря ЗАПЯТОЙ на конце, иначе работать не будет
        # print(cursor.statement) - ввыводит какой запрос был выполнен в БД
        print(cursor.statement)
        # Метод fetchall() возвращает список с кортежами, если результатов нет, то вернется пустой список
        roles = cursor.fetchall()
        return roles

# Функция, которая извлекает из запроса нужные параметры и складывает их в словарь, а затем возвращает его
# В качестве агрумента передается список параметров (params_list), которые мы хотим извлечь из запроса
def extract_params(params_list):
    params_dict = {}
    for param in params_list:
        params_dict[param] = request.form[param] or None
        # or None используется для избегания бага с добавлением в БД пустой строки
    return params_dict

# Сохранение данных нового пользователя
@app.route('/users/create', methods=['POST'])
@login_required # для того, чтобы только авторизованный пользователь мог отправить данные по этому руту
def create_user():
    # Получение данных из запроса
    params = extract_params(PERMITED_PARAMS)
    # -------------------------------------------------------------------------
    # ДАЛЕЕ ЗАКОМЕНТИРОВАННЫЙ КОД НЕ ИСПОЛЬЗУЕТСЯ, Т,К ВМЕСТО НЕГО ЕСТЬ ФУН-ИЯ (extract_params)
    # or None используется для избегания бага с добавлением в БД пустой строки
    # login = request.form['login'] or None 
    # password = request.form['password'] or None
    # last_name = request.form['last_name'] or None
    # first_name = request.form['first_name'] or None
    # middle_name = request.form['middle_name'] or None
    # role_id = request.form['role_id'] or None
    # -------------------------------------------------------------------------
    # Запрос для отправления данных в БД
    query = 'INSERT INTO users (login, password_hash, last_name, first_name, middle_name, role_id) VALUES (%(login)s, SHA2(%(password)s, 256), %(last_name)s, %(first_name)s, %(middle_name)s, %(role_id)s);' # с помощью конструкции %()s подставляем из словаря
    # Для перехвата ошибок (если ввели неуникальный логин) оборачиваем выполнение запроса в try
    try:
        # C помощью with можно не закрывать cursor как делали это в load_user, это будет сделано автоматически
        with db.connection().cursor(named_tuple=True) as cursor:
            # Подставляем в верхний запрос при помощи метода execute(принимает аргумен-запрос, передаем кортеж(tuple) со значениями)
            cursor.execute(query, params)
            # .commit() - для окончательного добавления записи в БД
            db.connection().commit()
            flash('Обработка данных прошла успешно!', 'success')
    # mysql.connector.errors.DatabaseError - базовый класс для всех ошибок с БД (нарушение целостности, соединения и тд.)
    except mysql.connector.errors.DatabaseError:
        # Если случались ошибка, то идет откатить ти изменения, что были внесены до этого
        db.connection().rollback() # для этого используется метод rollback()
        flash('При сохранении данных возникла ошибка.', 'danger')
        return render_template('users_new.html', user=params, roles_list=load_roles()) # передается список ролей для рендеринга
        # user=params, чтобы данный вставлялись в форму в случае ошибки
    return redirect(url_for('users'))

# Страничка для изменения пользователя
@app.route('/users/<int:user_id>/update', methods=['POST'])
@login_required # для того, чтобы только авторизованный пользователь мог отправить данные по этому руту
def update_user(user_id):
    # Получение данных из запроса
    params = extract_params(EDIT_PARAMS)
    params['id'] = user_id
    # Запрос для отправления данных в БД
    query = ('UPDATE users SET last_name=%(last_name)s, first_name=%(first_name)s, '
             'middle_name=%(middle_name)s, role_id=%(role_id)s WHERE id=%(id)s;')
            # с помощью конструкции %()s подставляем из словаря
    # Для перехвата ошибок (если ввели неуникальный логин) оборачиваем выполнение запроса в try
    try:
        # C помощью with можно не закрывать cursor как делали это в load_user, это будет сделано автоматически
        with db.connection().cursor(named_tuple=True) as cursor:
            # Подставляем в верхний запрос при помощи метода execute(принимает аргумен-запрос, передаем кортеж(tuple) со значениями)
            cursor.execute(query, params)
            # .commit() - для окончательного добавления записи в БД
            db.connection().commit()
            flash('Обработка данных прошла успешно!', 'success')
    # mysql.connector.errors.DatabaseError - базовый класс для всех ошибок с БД (нарушение целостности, соединения и тд.)
    except mysql.connector.errors.DatabaseError:
        # Если случались ошибка, то идет откатить ти изменения, что были внесены до этого
        db.connection().rollback() # для этого используется метод rollback()
        flash('При сохранении данных возникла ошибка.', 'danger')
        return render_template('users_edit.html', user=params, roles_list=load_roles()) # передается список ролей для рендеринга
        # user=params, чтобы данный вставлялись в форму в случае ошибки
    return redirect(url_for('users'))

# Страничка редактирования с формой
@app.route('/users/<int:user_id>/edit')
@login_required # для того, чтобы только авторизованный пользователь мог отправить данные по этому руту
def edit_user(user_id):
    # SQL-запрос к базе данных, вывод всех пользователей
    query = 'SELECT * FROM users WHERE users.id = %s'
    # C помощью with можно не закрывать cursor как делали это в load_user, это будет сделано автоматически
    with db.connection().cursor(named_tuple=True) as cursor:
        # Подставляем в верхний запрос при помощи метода execute(принимает аргумен-запрос, передаем кортеж(tuple) со значениями)
        cursor.execute(query, (user_id,)) # кортеж с одним элементом мохдается благодаря ЗАПЯТОЙ на конце, иначе работать не будет
        # print(cursor.statement) - ввыводит какой запрос был выполнен в БД
        print(cursor.statement)
        # Метод fetchone() возвращает либо None, если результат пустой, либо кортеж с найденной записью, если что-то нашлось
        user = cursor.fetchone()
    return render_template('users_edit.html', user=user, roles_list=load_roles())
    # user передает данные пользователя, которые затем мы подставим в html

# Страничка для просмотра пользователя
@app.route('/user/<int:user_id>')
def show_user(user_id):
    # SQL-запрос к базе данных, вывод всех пользователей
    query = 'SELECT * FROM users WHERE users.id = %s'
    # C помощью with можно не закрывать cursor как делали это в load_user, это будет сделано автоматически
    with db.connection().cursor(named_tuple=True) as cursor:
        # Подставляем в верхний запрос при помощи метода execute(принимает аргумен-запрос, передаем кортеж(tuple) со значениями)
        cursor.execute(query, (user_id,)) # кортеж с одним элементом мохдается благодаря ЗАПЯТОЙ на конце, иначе работать не будет
        # print(cursor.statement) - ввыводит какой запрос был выполнен в БД
        print(cursor.statement)
        # Метод fetchone() возвращает либо None, если результат пустой, либо кортеж с найденной записью, если что-то нашлось
        user = cursor.fetchone()
    return render_template('users_show.html', user=user)
    # user передает данные пользователя, которые затем мы подставим в html

# Страничка удаления пользователей
@app.route('/users/<int:user_id>/delete', methods=['POST'])
@login_required # для того, чтобы только авторизованный пользователь мог отправить данные по этому руту
def delete_user(user_id):
    # SQL-запрос к базе данных, вывод всех пользователей
    query = 'DELETE FROM users WHERE users.id=%s;'
    # Для перехвата ошибок (если ввели неуникальный логин) оборачиваем выполнение запроса в try
    try:
        # C помощью with можно не закрывать cursor как делали это в load_user, это будет сделано автоматически
        with db.connection().cursor(named_tuple=True) as cursor:
            # Подставляем в верхний запрос при помощи метода execute(принимает аргумен-запрос, передаем кортеж(tuple) со значениями)
            cursor.execute(query, (user_id,)) # кортеж с одним элементом мохдается благодаря ЗАПЯТОЙ на конце, иначе работать не будет
            # .commit() - для окончательного добавления записи в БД
            db.connection().commit()
            # print(cursor.statement) - ввыводит какой запрос был выполнен в БД
            print(cursor.statement)
        flash('Пользователь успешно удален.', 'success')
    except mysql.connector.errors.DatabaseError:
        db.connection().rollback()
        flash('При удалении пользователя возникла ошибка.', 'danger')
    return redirect(url_for('users'))
    # user передает данные пользователя, которые затем мы подставим в html

@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('index'))

# Функция загрузки пользователя по идентификатору из БД
@login_manager.user_loader
def load_user(user_id):
    # SQL-запрос к базе данных / %s работает как .format() - позволяет подставлять значение 
    query = 'SELECT * FROM users WHERE users.id = %s;'
    # У объекта соединения есть метод курсор. Через метод cursor выпонлятся запрос
    cursor = db.connection().cursor(named_tuple=True) # named_tuple=True - позволяет обращаться далее по названию полей таблицы БД
    # Подставляем в верхний запрос (под %s) при помощи метода execute(принимает аргумен-запрос, передаем кортеж(tuple) со значениями)
    cursor.execute(query, (user_id,)) # кортеж с одним элементом создается благодаря ЗАПЯТОЙ на конце, иначе работать не будет
    # Метод fetchone() возвращает либо None, если результат пустой, либо кортеж с найденной записью, если что-то нашлось
    user = cursor.fetchone()
    # После всех манипуляций закрываем метод cursor
    cursor.close()
    # Далее идет проверка
    # Если нашелся прользователь в БД по такому id, то возвращается объект класса user с данными этого пользователя
    # Если не нашелся, то возвращается None
    if user:
        # Возвращает id пользователя и его логин
        return User(user.id, user.login)
    return None