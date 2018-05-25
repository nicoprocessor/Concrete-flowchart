from flask import Flask, render_template, url_for

app = Flask(__name__)

dummy_data = [
    {
        'name': 'Nicola',
        'surname': 'Onofri'
    }, {
        'name': 'Mario',
        'surname': 'Rossi'
    }
]


@app.route('/login')
@app.route('/')
def login():
    print('Hello')
    return render_template('login.html', data=dummy_data, title='Login')


if __name__ == '__main__':
    app.run()
