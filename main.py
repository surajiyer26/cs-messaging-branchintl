from flask import Flask, render_template, url_for, flash, redirect, request, session
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase
from flask_sqlalchemy import SQLAlchemy
from forms import CreateAgentForm, CreateRoomForm
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = '1f5d157db8961410fa567f402f995634'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
socketio = SocketIO(app)

class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    sum_of_ratings = db.Column(db.Integer, default=0)
    no_of_ratings = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'Agent with id {self.id} and name {self.name}'
    
class Query(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    query = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    level = db.Column(db.Integer, nullable=False)
    agent_assigned = db.Column(db.String(20), nullable=False)
    code = db.Column(db.String(4), nullable=False)
    
    def __repr__(self):
        return f'Query with id {self.id}, level {self.level}, assigned to {self.agent_assigned}, code {self.code}, asked at {self.query}'

# agentdb = [
#     {
#         'name': 'General',
#     },
#     {
#         'name': 'Suraj',
#     },
#     {
#         'name': 'Pooraj',
#     },
# ]

@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/agents')
def agents():
    agentdb = Agent.query.all()
    return render_template('agents.html', agentdb=agentdb)

@app.route('/create-agent', methods=['GET', 'POST'])
def create_agent():
    form = CreateAgentForm()
    if form.validate_on_submit():
        if Agent.query.filter_by(name=form.name.data).first():  
            flash(f'Agent with name {form.name.data} already exists.', 'warning')
        else:
            new_agent = Agent(name=form.name.data)
            db.session.add(new_agent)
            db.session.commit()
            flash(f'Agent with name {form.name.data} created.', 'success')
            return redirect(url_for('agents'))
    else:
        if request.method == 'POST':
            flash('Form validation failed. Please check your input.', 'danger')
    return render_template('create_agent.html', form=form)

@app.route('/create-room', methods=['GET', 'POST'])
def create_room():
    form = CreateRoomForm()
    return render_template('create_room.html', form=form)

if __name__ == '__main__':
    socketio.run(app, debug=True)