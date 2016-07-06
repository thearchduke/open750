###
# Make this actually random!
# >>> import os
# >>> os.urandom(24)
# '\xfd{H\xe5<\x95\xf9\xe3\x96.5\xd1\x01O<!\xd5\xa2\xa0\x9fR"\xa1\xa8'
###
SECRET_KEY = 'flooble'

###
# For input on the textarea that people use to write.
# This lets them pass in arbitrary HTML.
# A XSS is possible here.
#
#TODO: this whole shebang can be avoided by setting the app up like the following:
# from flask import Markup
# message = Markup("<h1>I am safe!</h1>")
###
HTML_SAFE = True