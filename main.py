from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///my_base.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config.from_object(__name__)

db = SQLAlchemy(app)


# Models
class MyBase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    device_type = db.Column(db.String(100), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    success = db.Column(db.Integer)

    def __repr__(self):
        return f"<my_base {self.id}>"


@app.route('/', methods=('POST', 'GET'))
@app.route('/<int:page_num>', methods=('POST', 'GET'))
def index(page_num=1):
    """Главная страница"""
    try:
        tabel_all = MyBase.query.order_by(MyBase.id.desc()).paginate(per_page=20, page=page_num, error_out=True)
        return render_template('index.html', tabel_all=tabel_all)
    except:
        return 'Ошибка чтения из БД в /'



@app.route('/result', methods=('POST', 'GET'))
def result():
    """Подсчет объектов"""
    list_value = []  # список с подсчетами в HTML
    dict_return = {}  # словарь для параметров
    dev_type = []  # список device_type

    operator = (request.form['name']).replace(" ", "")
    if operator:
        if bool(MyBase.query.filter_by(name=f'{operator}').first()):

            for el in list(set(MyBase.query.with_entities(MyBase.device_type))):  # создание уникальных device_type
                dev_type.append(el[0])

            for dev in dev_type:
                all_value = len(MyBase.query.filter(MyBase.name == f"{operator}", MyBase.device_type == f"{dev}").all())
                yes = len(MyBase.query.filter(MyBase.name == f"{operator}", MyBase.device_type == f"{dev}", MyBase.success == 1).all())
                no = len(MyBase.query.filter(MyBase.name == f"{operator}", MyBase.device_type == f"{dev}", MyBase.success == 0).all())

                dict_return[f'{dev}'] = all_value, yes, no

            list_value.append(dict_return)

            return render_template('result.html', list_value=list_value, name=operator)

        else:
            return "Введите имя существующее в базе данных"
    else:
        return "Ввведите хоть что-нибудь"


@app.route('/delete/<int:id>', methods=('POST', 'GET'))
def delete(id):
    """ Удаляет элементы по id """
    rec = MyBase.query.get_or_404(id)
    try:
        db.session.delete(rec)
        db.session.commit()
        return redirect('/')
    except:
        return "При удалении возникла ошибка"


@app.route('/create', methods=('POST', 'GET'))
def create():
    """ДОбавляет элемент в таблицу"""
    if request.method == "POST":
        item = MyBase(device_type=request.form['device_type'], name=request.form['name'],
                      success=request.form['success'])

        try:
            db.session.add(item)
            db.session.commit()
            return redirect('/')
        except:
            return 'Ошибка при добавлении новых данных в БД'

    return render_template('create.html')


if __name__ == "__main__":
    app.run(debug=True)
