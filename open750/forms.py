from flask_wtf import Form
from wtforms import TextField, TextAreaField, SubmitField
from flask.ext.pagedown.fields import PageDownField
from wtforms.validators import DataRequired

class ScribbleForm(Form):
	title = TextField('Title?')
	body = PageDownField('Scribble!', validators=[DataRequired()])
	submit = SubmitField('Save it!', validators=[DataRequired()])
