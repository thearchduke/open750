#!/usr/bin/env python
from flask import Blueprint, render_template, url_for, request, redirect, flash
from models import session, Scribble
from forms import ScribbleForm

open750 = Blueprint('open750', __name__, template_folder='templates')

@open750.route('/', methods=['GET'])
def home():
	scribbles = session.query(Scribble).limit(1).all()
	return render_template('index.html', s=scribbles)

@open750.route('/scribbles/<id>', methods=['GET', 'POST'])
def details(id):
	s = session.query(Scribble).filter(Scribble.id == id).first()
	form = ScribbleForm(obj=s)
	return render_template('detail.html', form=form, s=s)