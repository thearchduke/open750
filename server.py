#!/usr/bin/env python
import sys, os
from flask import Flask
from open750.views import open750

#TODO: word count is inaccurate on both javascript side and python side
#TODO: textarea is currently formatted as |safe. look up ways to make this safer!
app = Flask(__name__)
app.config.from_object('config')

app.register_blueprint(open750, url_prefix="/open750")

if __name__ == '__main__':
	app.run(debug=True)