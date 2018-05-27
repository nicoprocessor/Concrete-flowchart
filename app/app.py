from flask import Flask, render_template

from login import LoginForm
from register import RegistrationForm

app = Flask(__name__)

app.config['SECRET_KEY'] = '322aaa35662adf0d1e0ecc141413994e'


@app.route('/')
def home():
    form = LoginForm()
    return render_template('home.html', title='Login', form=form)


@app.route('/login')
def login():
    form = LoginForm()
    return render_template('home.html', title='Login', form=form)


@app.route('/register')
def register():
    form = RegistrationForm()
    return render_template('register.html', title='Register', form=form)


if __name__ == '__main__':
    app.run()
