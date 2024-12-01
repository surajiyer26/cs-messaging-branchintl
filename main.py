from flask import Flask, render_template, url_for, flash, redirect, request, session
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase
from flask_sqlalchemy import SQLAlchemy
from forms import CreateAgentForm, CreateRoomForm
from datetime import datetime
import os
from dotenv import load_dotenv 


app = Flask(__name__)
app.config['SECRET_KEY'] = '1f5d157db8961410fa567f402f995634'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)
socketio = SocketIO(app)
load_dotenv()
CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
print("CLAUDE_API_KEY:", CLAUDE_API_KEY)


class Agent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=True, nullable=False)
    no_of_queries = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'Agent with id {self.id} and name {self.name} and with {self.no_of_queries} number of queries'
    

class Query(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    query = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    level = db.Column(db.Integer, nullable=False)
    agent_assigned = db.Column(db.String(20), nullable=False)
    code = db.Column(db.String(4), nullable=False)
    
    def __repr__(self):
        return f'Query with id {self.id}, level {self.level}, assigned to {self.agent_assigned}, code {self.code}, asked at {self.query}'


def generate_unique_code(length):
    while True:
        code = ''.join(random.choice(ascii_uppercase) for _ in range(length))
        if not db.session.query(Query).filter(Query.code == code).first():
            break
    return code


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
    if form.validate_on_submit():
        agentdb = Agent.query.all()
        if not agentdb:
            flash('No agents available, try again later!', 'warning')
            return render_template('create_room.html', form=form)

        import anthropic
        client = anthropic.Anthropic(api_key=CLAUDE_API_KEY)

        try:
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1000,
                temperature=0,
                system="Assign this message a single integer representing emergency level from 1 (lowest) to 10 (highest), reply with that single integer and nothing else",
                messages=[{"role": "user", "content": form.query.data}]
            )
            level = int(message.content.strip())
            print("The emergency level assigned is", level)
        except Exception as e:
            flash(f"Problem communicating with the AI service: {str(e)}", 'warning')
            level = random.randint(1, 10)

        agent_assigned = Agent.query.order_by(Agent.no_of_queries).first()
        code = generate_unique_code(4)

        query = Query(query=form.query.data, level=level, agent_assigned=agent_assigned.name, code=code)
        db.session.add(query)
        db.session.commit()
        flash('Query created successfully.', 'success')

        # db.session.delete(query)
        # db.session.commit()
        # flash('Query deleted successfully.', 'info')

        return redirect(url_for('room'))

    return render_template('create_room.html', form=form)


@app.route('/room')
def room():
    return render_template('room.html')


if __name__ == '__main__':
    socketio.run(app, debug=True)