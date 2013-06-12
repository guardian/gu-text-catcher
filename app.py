import webapp2
import jinja2
import os
import json
import logging
import hashlib
import datetime

from urlparse import urlparse

from urllib import quote, urlencode
from google.appengine.api import urlfetch
from google.appengine.ext import ndb

import headers
from models import CapturedSelection, Text, Summary

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")))

class MainPage(webapp2.RequestHandler):
	def get(self):
		template = jinja_environment.get_template('index.html')
		
		template_values = {}

		today = datetime.date.today()

		all_query = Summary.query(Summary.date == today).order(-Summary.count)

		template_values["all"] = all_query.iter()

		self.response.out.write(template.render(template_values))

class DetailPage(webapp2.RequestHandler):
	def get(self):
		template = jinja_environment.get_template('detail.html')
		
		template_values = {}

		today = datetime.date.today()
		logging.info(today)

		twitter_qry = Summary.query(Summary.date == today, Summary.size <= 140).order(-Summary.size, -Summary.count)
		longform_query = Summary.query(Summary.date == today, Summary.size > 140).order(-Summary.size, -Summary.count)
		template_values["twitter"] = twitter_qry.iter()
		template_values["longform"] = longform_query.iter()

		self.response.out.write(template.render(template_values))


class CaptureHandler(webapp2.RequestHandler):
	def post(self):
		selection = self.request.get("selection")
		path = self.request.get("path")

		today = datetime.date.today().isoformat()
		if selection and len(selection) <= 500:
			sha = hashlib.sha1(selection).hexdigest()

			if path:
				CapturedSelection(text=selection, checksum=sha, path=path).put()
			else:
				CapturedSelection(text=selection, checksum=sha).put()

			text_key = ndb.Key("Text", sha)
			text_entity = text_key.get()

			if not text_entity:
				Text(id=sha, text=selection).put()

			count_key_id = today + "." + sha

			count_key = ndb.Key('Summary', count_key_id)

			count = count_key.get()

			if count:
				count.count = count.count + 1
				count.put()
			else:
				Summary(id=count_key_id, text=selection, checksum=sha, count=1, size=len(selection)).put()

		headers.set_cors_headers(self.response)


app = webapp2.WSGIApplication([('/', MainPage),
	('/capture', CaptureHandler),
	('/detail', DetailPage),],
                              debug=True)