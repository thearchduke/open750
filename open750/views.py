#!/usr/bin/env python
from flask import Blueprint, render_template, url_for, request, redirect, flash, Response, abort
from flask import session as flask_session
from models import session, SevenFifty, User
from forms import SevenFiftyForm, CreateUserForm
from functools import wraps
import datetime

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
    if u.verify_password(password):
    	flask_session['current_user'] = {'name': u.name, 'id': u.id}
    	return True
    else:
    	flask_session['current_user'] = None
    	return False

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


def not_authorized():
	flash("You aren't authorized to view that post.")
	return redirect(url_for('.home'))

def check_user_for_obj(kind, id):
	#kind = globals()[kind]
	obj = session.query(kind).filter(kind.id == id).first()

	## Does it exist
	if not obj: return render_template('404.html'), 404

	## Check auth
	uid = None
	if flask_session.get('current_user'):
		uid = flask_session['current_user'].get('id')
	if obj.user_id == uid:
		return True
	else:
		return False


@open750.route('/logout', methods=['GET'])
@requires_auth
def logout():
	flask_session['current_user'] = None
	return redirect(url_for('.landing')), 401


## Routes

@open750.route('/', methods=['GET', 'POST'])
def landing():
	if request.authorization:
		return redirect(url_for('.home'))
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
	flask_session['writable'] = False
	sevenfiftys = session.query(SevenFifty).filter(\
		SevenFifty.user_id == flask_session.get('current_user')['id']).all()
	if sevenfiftys:
		now = datetime.datetime.now()
		if sevenfiftys[-1].date.date() <= (datetime.datetime.now().date() - datetime.timedelta(days=1)):
			flask_session['writable'] = True
	else:
		flask_session['writable'] = True
	return render_template('index.html', s=sevenfiftys)

@open750.route('/write', methods=['GET', 'POST'])
@requires_auth
def write():
	if not flask_session['writable']:
		flash("Sorry, you can't write any more today")
		return redirect(url_for('.home'))
	form = SevenFiftyForm()
	if form.validate_on_submit():
		s = SevenFifty(form.text.data, flask_session['current_user']['id'])
		session.add(s)
		session.commit()
		flash('Thanks for adding a new post. Come back tomorrow!')
		flask_session['writable'] = False
		return redirect(url_for('.home'))
	new_post = True
	return render_template('write.html', form=form, new_post = new_post)

@open750.route('/<id>', methods=['GET'])
@requires_auth
def read(id):
	s = session.query(SevenFifty).filter(SevenFifty.id == id).first()
	if not check_user_for_obj(SevenFifty, id):
		return not_authorized()
	if not s: return render_template('404.html'), 404
	return render_template('read.html', s=s)

@open750.route('/<id>/edit', methods=['GET', 'POST'])
@requires_auth
def edit(id):
	s = session.query(SevenFifty).filter(SevenFifty.id == id).first()
	if not check_user_for_obj(SevenFifty, id):
		return not_authorized()
	if not s: return render_template('404.html'), 404
	form = SevenFiftyForm(obj=s)
	if form.validate_on_submit():
		form.populate_obj(s)
		s.wordCount = len(s.text.split())
		session.add(s)
		session.commit()
		flash('Thanks for updating your post \'%s.\'' % s.slug)
		return redirect(url_for('.home'))
	new_post = False
	return render_template('write.html', form=form, s=s, new_post = new_post)


### Testing and stuff
@open750.route('/test_write', methods=['GET'])
def test_write():
	form = SevenFiftyForm()
	new_post = True
	return render_template('write.html', form=form, new_post=new_post)