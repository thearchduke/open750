#!/usr/bin/env python
import sys, os
from flask import Flask
from open750.views import open750
import config as cf
#import config_real as cf

app = Flask(__name__)
app.secret_key = cf.secret_key
app.register_blueprint(open750, url_prefix="/open750")

app.run(debug=True)
