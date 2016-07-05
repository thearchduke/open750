#!/usr/bin/env python
import sys, os
from flask import Flask
from open750.views import open750

'''
CONFIG DETAILS:
Put actual info in config.py instead of my mock info
'''
import config as cf


#TODO: word count is inaccurate on both javascript side and python side
#TODO: textarea is currently formatted as |safe. look up ways to make this safer!
app = Flask(__name__)
app.secret_key = cf.secret_key
app.register_blueprint(open750, url_prefix="/open750")

app.run(debug=True)
