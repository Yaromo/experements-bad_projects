from data import db_session, __all_models
from flask import Flask, render_template, redirect
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from classes import *
import os


app = Flask(__name__)
SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(__all_models.User).get(user_id)


@app.route("/", methods=['GET', 'POST'])
def home():
    db_sess = db_session.create_session()
    posts = db_sess.query(__all_models.Message)
    form = MessageForm()
    if form.validate_on_submit():
        message = __all_models.Message()
        message.name = f'Автор: {current_user.name}'
        print(message.name)
        message.content = form.content.data
        print(message.content)
        try:
            db_sess.add(message)
            db_sess.commit()
        except:
            return 'Произошла ошибка'
    return render_template('home.html', posts=posts, form=form)



@app.route('/registration', methods=['GET', 'POST'])
def registration():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('registration.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        db_sess = db_session.create_session()
        if db_sess.query(__all_models.User).filter(__all_models.User.email == form.email.data).first():
            return render_template('registration.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = __all_models.User(
            name=form.name.data,
            email=form.email.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/sign_up')
    return render_template('registration.html', title='Регистрация', form=form)



@app.route("/sign_up", methods=['GET', 'POST'])
def sign_up():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(__all_models.User).filter(__all_models.User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect('/')
        return render_template('sign_up.html',
                               message="Неправильная почта или пароль",
                               form=form)
    return render_template('sign_up.html', title='Авторизация', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


if __name__ == '__main__':
    db_session.global_init("db/user_data.db")
    app.run(port=8080, host='127.0.0.1')