from flask import Flask, render_template, url_for, flash, redirect, request, session
from flask_socketio import join_room, leave_room, send, SocketIO
from flask_sqlalchemy import SQLAlchemy
from forms import CreateAgentForm, CreateRoomForm
from datetime import datetime
import os
import random
from string import ascii_uppercase
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
        return f'Agent({self.id}, {self.name}, {self.no_of_queries})'


class Query(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    query = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.now)
    level = db.Column(db.Integer, nullable=False)
    agent_assigned = db.Column(db.String(20), nullable=False)
    code = db.Column(db.String(4), nullable=False)

    def __repr__(self):
        return f'Query({self.id}, {self.level}, {self.agent_assigned}, {self.code})'


def generate_unique_code(length):
    while True:
        code = ''.join(random.choice(ascii_uppercase) for _ in range(length))
        if not db.session.query(Query).filter(Query.code == code).first():
            return code


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/agents', methods=['GET', 'POST'])
def agents():
    agentdb = Agent.query.all()
    if request.method == 'POST':
        session.clear()
        session['name'] = request.form.get('name')
        return redirect(url_for('join_room_view'))
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
            flash(f'Agent {form.name.data} created.', 'success')
            return redirect(url_for('agents'))
    return render_template('create_agent.html', form=form)


@app.route('/join-room', methods=['GET', 'POST'])
def join_room_view():
    querydb = db.session.query(Query).filter(Query.agent_assigned == session['name']).order_by(Query.level.desc(), Query.date).all()
    if request.method == 'POST':
        session['code'] = request.form.get('code')
        query = db.session.query(Query).filter(Query.code == session['code']).first()
        session['query'] = query.query
        db.session.delete(query)
        agent = Agent.query.filter_by(name=session['name']).first()
        agent.no_of_queries += 1
        db.session.commit()
        return redirect(url_for('room'))
    return render_template('join_room.html', querydb=querydb)


@app.route('/create-room', methods=['GET', 'POST'])
def create_room():
    form = CreateRoomForm()
    if form.validate_on_submit():
        print('query is', form.query.data)
        agentdb = Agent.query.all()
        if not agentdb:
            flash('No agents available. Try again later.', 'warning')
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

        if code not in rooms:
            rooms[code] = {"messages": [], "members": 0}

        session['name'] = 'Customer'
        session['query'] = form.query.data
        session['code'] = code
        return redirect(url_for('room'))
    return render_template('create_room.html', form=form)


@app.route('/room')
def room():
    room = session.get("code")

    if session.get("query") is None:
        query = "Branch Out With Us!"
    else:
        query = session.get("query")

    predefined_messages = []
    if session.get("name") is 'Customer':
        pass
    else:
            predefined_messages = ['How may I help you with?', 'Please give us your contact information.', 'Have a great day!', 'Do you want us to call?']

    if room is None or room not in rooms:
        flash('Room not found.', 'danger')
        return redirect(url_for('home'))
    return render_template("room.html", code=room, messages=rooms[room]["messages"], query=query, predefined_messages=predefined_messages)


rooms = {}


@socketio.on("message")
def handle_message(data):
    room = session.get("code")
    if not room or room not in rooms:
        return

    content = {
        "name": session.get("name"),
        "message": data["data"],
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{session.get('name')} said: {data['data']}")


@socketio.on("connect")
def handle_connect():
    room = session.get("code")
    name = session.get("name")
    if not room or not name:
        return
    join_room(room)
    send({"name": name, "message": "has joined the room"}, to=room)
    if room in rooms:
        rooms[room]["members"] += 1
    else:
        rooms[room] = {"messages": [], "members": 1}


@socketio.on("disconnect")
def handle_disconnect():
    room = session.get("code")
    name = session.get("name")
    leave_room(room)
    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]
    send({"name": name, "message": "has left the room"}, to=room)


if __name__ == '__main__':
    db.create_all()
    socketio.run(app, debug=True)