from flask import Flask, render_template, request
from flask import make_response

app = Flask(__name__)
application = app

@app.route('/')
def index():
    # url = request.url
    # return render_template('index.html', url=url)
    return render_template('index.html')

@app.route('/headers')
def headers():
    return render_template('headers.html')

@app.route('/args')
def args():
    return render_template('args.html')

@app.route('/cookies')
def cookies():
    resp = make_response(render_template('cookies.html'))
    # Удаляем куки, если есть и создаем куки, если их нет
    if 'name' in request.cookies:
        resp.delete_cookie('name')
    else:
        resp.set_cookie('name','value')
    return resp

@app.route('/form', methods=['GET', 'POST'])
def form():
    return render_template('form.html')

@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404
# 404 - статус код вывода ошибки в терминале

@app.route('/calc', methods=['GET', 'POST'])
def calc():
    result = ''
    error_text = ''
    
    if request.method == 'POST':
        
        try:
            first_num = int(request.form['firstnumber'])
            second_num = int(request.form['secondnumber'])
        except ValueError:
            error_text = 'Содержимое ввода не является цифрой!'
            return render_template('calc.html', result=result, error_text=error_text)
        
        operation = request.form['operation']
        
        if operation == '+':
            result = first_num + second_num
        elif operation == '-':
            result = first_num - second_num
        elif operation == '*':
            result = first_num * second_num
        elif operation == '/':
            try:
                result = first_num / second_num
            except ZeroDivisionError:
                error_text = 'На ноль делить нельзя!'

    return render_template('calc.html', result=result, error_text=error_text)

# -----------------------------------------------------------------------------------------------------------------------------------------

# Функция, которая приводит номер в последовательность чисел
def convert_tel_to_number(tel):
    tel = tel.replace(' ', '').replace('-', '').replace('+', '').replace('(', '').replace(')', '').replace('.', '')
    return tel

# Функция, которая проверяет все ли символы в строке являются числами
def check_digit(tel):
    if tel.isdigit() == True:
        return tel
    else:
        None

# Функция, которая проверяет длину номера телефона (только числа) и проверка на 7,8 в 11 символах
def check_len(tel):
    if len(tel) == 10:
        return tel
    elif len(tel) == 11 and tel[0] != '7' or tel[0] != '8':
        return None
    else:
        return None

# Проверка номера на выполняемость условий ввода
def input_tel(tel):
    tel = convert_tel_to_number(tel)
    if check_digit(tel) == tel:
        if check_len(tel) == tel:
            message = 'Номер телефона верный'
            bootstrap_class = {'input_class': 'is-valid', 'div_class': 'valid-feedback'}
            return message, tel, bootstrap_class
        else:
            message = 'Недопустимый ввод. Неверное количество цифр!'
            bootstrap_class = {'input_class': 'is-invalid', 'div_class': 'invalid-feedback'}
            return message, None, bootstrap_class
    else:
        message = 'Недопустимый ввод. В номере телефона встречаются недопустимые символы!'
        bootstrap_class = {'input_class': 'is-invalid', 'div_class': 'invalid-feedback'}
        return message, None, bootstrap_class

# Функция преобразования номера телефона под стандартный вывод
def standart(tel):
    standart_phone_number = ''
    if len(tel) == 11:
        if tel[0] == '8':
            # standart_phone_number = tel[0]+'('+tel[1:4]+')'+tel[4:11]
            standart_phone_number = tel[0]+'-'+tel[1:4]+'-'+tel[4:7]+'-'+tel[7:9]+'-'+tel[9:11]
        elif tel[0] == '7':
            # standart_phone_number = '+'+tel[0]+' ('+tel[1:4]+') '+tel[4:7]+'-'+tel[7:9]+'-'+tel[9:11]
            standart_phone_number = '8-'+tel[1:4]+'-'+tel[4:7]+'-'+tel[7:9]+'-'+tel[9:11]
        # else:
            # standart_phone_number = tel[0:10]+' странный номер))'
    elif len(tel) == 10:
        # standart_phone_number = tel[0:3]+'.'+tel[3:6]+'.'+tel[6:8]+'.'+tel[8:10]
        standart_phone_number = '8-'+tel[0:3]+'-'+tel[3:6]+'-'+tel[6:8]+'-'+tel[8:10]
    return standart_phone_number

# Пример:
# +7 (123) 456-75-90
# 8(123)4567590
# 123.456.75.90

# Вывод
# 8-***-***-**-**

@app.route('/tel_form', methods=['GET', 'POST'])
def tel_form():
    message = ''
    tel = ''
    bootstrap_class = {}
    input_class, div_class = '', ''
    if request.method == 'POST':
        phone_number = str(request.form['tel'])
        message, tel, bootstrap_class = input_tel(phone_number)
        # Костыль ------->
        input_class = bootstrap_class['input_class']
        div_class = bootstrap_class['div_class']
        # --------------->
        if tel != None:
            tel = standart(tel)
    # return render_template('tel_form.html', message=message, phone_number=tel, bootstrap_class=bootstrap_class)
    return render_template('tel_form.html', message=message, phone_number=tel, bootstrap_class=bootstrap_class, input_class=input_class, div_class=div_class)