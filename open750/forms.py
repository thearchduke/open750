from flask_wtf import Form
from wtforms import TextField, TextAreaField, SubmitField, ValidationError
from flask.ext.pagedown.fields import PageDownField
from wtforms.validators import DataRequired

class ScribbleForm(Form):
	slug = TextField('Title?')
	text = TextAreaField('Scribble!', validators=[DataRequired()])

	def validate_text(form, field):
		if len(field.data.split(' ')) < 750:
			raise ValidationError("You have to write at least 750 words, silly!")

	submit = SubmitField('Save it!', validators=[DataRequired()])
