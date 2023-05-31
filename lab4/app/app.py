from flask import Flask, render_template, session, request, redirect, url_for, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required
from mysql_db import MySQL

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
    cursor.execute(query, (user_id,)) # кортеж с одним элементом мохдается благодаря ЗАПЯТОЙ на конце, иначе работать не будет
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