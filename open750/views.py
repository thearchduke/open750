#!/usr/bin/env python
from flask import render_template, url_for, request, redirect, flash
from models import session, Scribble
from open750 import app

@app.route('/', methods=['GET'])
def home():
	scribbles = session.query(Scribble).limit(1).all()
	return render_template('index.html', s=scribbles)