#!/usr/bin/env python
import sys, os
from flask import Flask
from open750.views import open750

app = Flask(__name__)
app.secret_key = 'flooble'
app.register_blueprint(open750, url_prefix="/open750")

app.run(debug=True)