#!/usr/bin/env python
from flask import Blueprint, render_template, url_for, request, redirect, flash, Response, abort
from flask import session as flask_session
from models import session, SevenFifty, User
from forms import SevenFiftyForm, CreateUserForm
from functools import wraps

open750 = Blueprint('open750', __name__, template_folder='templates', static_folder='static')


## Errors and stuff
@open750.errorhandler(404)
def page_not_found(e):
    return render_template("404.html")


## Logins
def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    u = session.query(User).filter(User.name == username).first()
    flask_session['current_user'] = {'name': u.name, 'id': u.id}
    return u.verify_password(password)

def authenticate():
	"""Sends a 401 response that enables basic auth"""
	return Response(
	'Could not verify your access level for that URL.\n'
	'You have to login with proper credentials', 401,
	{'WWW-Authenticate': 'Basic realm="Login Required"'})

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated

@open750.route('/logout', methods=['GET'])
@requires_auth
def logout():
	flask_session['current_user'] = None
	return redirect(url_for('.landing')), 401


## Routes

@open750.route('/', methods=['GET', 'POST'])
def landing():
	form = CreateUserForm()
	if form.validate_on_submit():
		u = User(form.name.data, form.password.data, form.email.data)
		session.add(u)
		session.commit()
		return redirect(url_for('.home'))
	return render_template('landing.html', form=form)

@open750.route('/home', methods=['GET'])
@requires_auth
def home():
	flash('welcome, %s' % flask_session.get('current_user')['name'])
	sevenfiftys = session.query(SevenFifty).filter(\
		SevenFifty.user_id == flask_session.get('current_user')['id']).all()
	return render_template('index.html', s=sevenfiftys)

@open750.route('/write', methods=['GET', 'POST'])
def new():
	form = SevenFiftyForm()
	if form.validate_on_submit():
		s = SevenFifty(form.text.data, flask_session['current_user']['id'])
		session.add(s)
		session.commit()
		flash('Thanks for adding a new post. Come back tomorrow!')
		return redirect(url_for('.home'))
	return render_template('write.html', form=form)

"""
@open750.route('/<id>', methods=['GET'])
def read(id):
	s = session.query(SevenFifty).filter(SevenFifty.id == id).first()
	if s.user_id != flask_session['current_user']['id']:
		flash("You aren't authorized to view that post.")
		return redirect(url_for('home'))
	if not s: return render_template('404.html'), 404
	form = SevenFiftyForm(obj=s)
	if form.validate_on_submit():
		form.populate_obj(s)
		session.add(s)
		session.commit()
		flash('Thanks for updating your post \'%s.\'' % s.slug)
	return render_template('detail.html', form=form, s=s)
"""

@open750.route('/<id>/edit', methods=['GET', 'POST'])
def details(id):
	s = session.query(SevenFifty).filter(SevenFifty.id == id).first()
	if s.user_id != flask_session['current_user']['id']:
		flash("You aren't authorized to view that post.")
		return redirect(url_for('home'))
	if not s: return render_template('404.html'), 404
	form = SevenFiftyForm(obj=s)
	if form.validate_on_submit():
		form.populate_obj(s)
		session.add(s)
		session.commit()
		flash('Thanks for updating your post \'%s.\'' % s.slug)
	return render_template('detail.html', form=form, s=s)

