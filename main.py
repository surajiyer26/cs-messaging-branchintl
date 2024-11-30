from flask import Flask, render_template, url_for
from forms import CreateAgentForm

app = Flask(__name__)
app.config['SECRET_KEY'] = '1f5d157db8961410fa567f402f995634'

agentdb = [
    {
        'name': 'General',
    },
    {
        'name': 'Suraj',
    },
    {
        'name': 'Pooraj',
    },
]

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/agents')
def agents():
    return render_template('agents.html', agentdb=agentdb)

@app.route('/create-agent')
def create_agent():
    form = CreateAgentForm()
    return render_template('create_agent.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)