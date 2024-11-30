from flask import Flask, render_template

app = Flask(__name__)

agents = [
    {
        'name': 'General'
    },
    {
        'name': 'Suraj'
    },
    {
        'name': 'Pooraj'
    },
]

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html', agents=agents)

if __name__ == '__main__':
    app.run(debug=True)