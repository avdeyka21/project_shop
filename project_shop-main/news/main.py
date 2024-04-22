import os

from flask import Flask, flash, request, redirect, url_for, render_template
from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from werkzeug.utils import secure_filename
from wtforms.fields.simple import SubmitField
from wtforms.validators import InputRequired
from data.tovar import Tov
from data import db_session
from data.users import User
from data.position import Post
from forms.user import RegisterForm, LoginForm
from flask_login import LoginManager, login_user, logout_user, login_required

app = Flask(__name__)

app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['UPLOAD_FOLDER'] = 'static/img'

login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/')
def index():
    return render_template("main.html")


@app.route('/about')
def about():
    return render_template('about_comp.html')


@app.route('/contacts')
def conn():
    return render_template('conn.html')


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")

        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route('/kata')
def katalog():
    db_sess = db_session.create_session()
    tov = db_sess.query(Tov)
    return render_template('katalog.html', tov=tov)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/korzina')
def korz():
    pass


@app.route('/profile', methods=['POST', 'GET'])
def profile():
    db_sess = db_session.create_session()
    if request.method == 'POST':
        name = request.form['name']
        name_zakaza = request.form['name_zakaza']
        email = request.form['email']
        address = request.form['address']
        post = Post(name_zakaza=name_zakaza, name=name, email=email, address=address)
        db_sess.add(post)
        db_sess.commit()
        return redirect('/')
    else:
        return render_template('profile.html')


class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")


@app.route('/index', methods=['GET', "POST"])
@app.route('/home', methods=['GET', "POST"])
def home():
    db_sess = db_session.create_session()
    form1 = UploadFileForm()
    if form1.validate_on_submit():
        file = form1.file.data  # First grab the file
        file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'],
                               secure_filename(file.filename)))
        name_file = file.filename
        name = request.form['name']
        cost = request.form['cost']
        disc = request.form['disc']
        post = Tov(name=name, disc=disc, cost=cost, name_file=name_file)
        db_sess.add(post)
        db_sess.commit()
        return redirect('/')
    return render_template('index.html', form=form1)


def main():
    db_session.global_init("db/blogs.db")
    app.run(port=5499)


if __name__ == '__main__':
    main()
