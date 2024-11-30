from flask import Flask, render_template, url_for, flash, redirect, request, session
from flask_socketio import join_room, leave_room, send, SocketIO
import random
from string import ascii_uppercase
from forms import CreateAgentForm, CreateRoomForm

app = Flask(__name__)
app.config['SECRET_KEY'] = '1f5d157db8961410fa567f402f995634'
socketio = SocketIO(app)

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

@app.route('/create-agent', methods=['GET', 'POST'])
def create_agent():
    form = CreateAgentForm()
    if form.validate_on_submit():
        if {'name': form.name.data} in agentdb:
            flash(f'Agent with name {form.name.data} already exists.', 'warning')
        else:
            agentdb.append({'name': form.name.data})
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