from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class CreateAgentForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=20)])
    submit = SubmitField('Create')

class CreateRoomForm(FlaskForm):
    query = StringField('Query', validators=[DataRequired(), Length(min=2, max=200)])
    submit = SubmitField('Create')