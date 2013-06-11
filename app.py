import webapp2
import jinja2
import os
import json
import logging
import hashlib

from urllib import quote, urlencode
from google.appengine.api import urlfetch

from models import CapturedSelection

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")))

class MainPage(webapp2.RequestHandler):
	def get(self):
		template = jinja_environment.get_template('index.html')
		
		template_values = {}

		self.response.out.write(template.render(template_values))

class CaptureHandler(webapp2.RequestHandler):
	def post(self):
		selection = self.request.get("selection")
		if selection:
			sha = hashlib.sha1(selection).hexdigest()
			selection_record = CapturedSelection(text=selection, checksum=sha)
			selection_record.put()


app = webapp2.WSGIApplication([('/', MainPage), ('/capture', CaptureHandler)],
                              debug=True)