from flask_wtf import Form
from wtforms import TextField, TextAreaField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo

class SevenFiftyForm(Form):
	text = TextAreaField('Write!', validators=[DataRequired()])

	def validate_text(form, field):
		if len(field.data.split()) < 750:
			raise ValidationError("You have to write at least 750 words, silly!")

	submit = SubmitField('Save it!', validators=[DataRequired()])

class CreateUserForm(Form):
	name = TextField("User name", validators=[DataRequired()])
	email = TextField("Email (optional)")
	password = PasswordField("Password", validators=[DataRequired(), \
		EqualTo('confirm', message='Passwords must match')])
	confirm = PasswordField("Repeat password", validators=[DataRequired()])
	robot = BooleanField('i am not a robot', validators=[DataRequired()])
	submit = SubmitField("Let's go!")