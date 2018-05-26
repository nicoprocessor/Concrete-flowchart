from flask import Flask, render_template
from app.register import RegistrationForm
from app.login import LoginForm

app = Flask(__name__)

app.config['SECRET_KEY'] = '322aaa35662adf0d1e0ecc141413994e'

dummy_data = [
    {
        'name': 'Nicola',
        'surname': 'Onofri'
    }, {
        'name': 'Mario',
        'surname': 'Rossi'
    }
]

@app.route('/')
def login():
    return render_template('login.html', data=dummy_data)


@app.route('/login')
def login():
    form = LoginForm()
    return render_template('login.html', title='Login', form=form)


@app.route('/register')
def register():
    form = RegistrationForm()
    return render_template('register.html', title='Register', form=form)


if __name__ == '__main__':
    app.run()
