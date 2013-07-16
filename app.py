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
from google.appengine.api import memcache
from google.appengine.ext.webapp import template

import headers
from models import CapturedSelection, Text, Summary
from tuples import SummaryInfo

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")),
    autoescape=True,
    extensions=['jinja2.ext.autoescape'])

def nice_timestamp(datetime):
	return datetime.strftime("%d/%m/%Y %H:%M:%S")

CORS_HOST = "http://www.guardian.co.uk"

jinja_environment.filters['nice_timestamp'] = nice_timestamp

if os.environ.get('SERVER_SOFTWARE','').startswith('Development'):
	CORS_HOST = "localhost"

class MainPage(webapp2.RequestHandler):
	def get(self):
		template = jinja_environment.get_template('index.html')
		
		template_values = {}

		cache_key = "today.all"

		all_data = memcache.get(cache_key)

		today = datetime.date.today()

		if not all_data:

			all_query = Summary.query(Summary.date == today, Summary.count > 1).order(-Summary.count)

			all_data = [SummaryInfo(count=x.count, text=x.text, checksum=x.checksum) for x in all_query.iter()]

		template_values["all"] = all_data

		headers.set_cache_headers(self.response, 60)

		self.response.out.write(template.render(template_values))

class DetailPage(webapp2.RequestHandler):
	def get(self):
		template = jinja_environment.get_template('detail.html')
		
		template_values = {}

		today = datetime.date.today()

		twitter_qry = Summary.query(Summary.date == today, Summary.size <= 140).order(-Summary.size, -Summary.count)
		longform_query = Summary.query(Summary.date == today, Summary.size > 140).order(-Summary.size, -Summary.count)
		template_values["twitter"] = twitter_qry.iter()
		template_values["longform"] = longform_query.iter()

		self.response.out.write(template.render(template_values))


class CaptureHandler(webapp2.RequestHandler):
	def post(self):
		selection = self.request.get("selection")
		selection = selection.lstrip()
		selection = selection.rstrip()

		path = self.request.get("path")

		today = datetime.date.today().isoformat()
		if selection and len(selection) <= 500:
			sha = hashlib.sha1(selection.encode('utf-8')).hexdigest()

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

		headers.set_cors_headers(self.response, host=CORS_HOST)

class ContentPage(webapp2.RequestHandler):
	def get(self, checksum):
		template = jinja_environment.get_template('content.html')
		
		captures_qry = CapturedSelection.query(CapturedSelection.checksum == checksum).order(-CapturedSelection.datetime)

		captures = [captures for captures in captures_qry.iter()]

		template_values = {
			"domain" : "www.guardian.co.uk",
			"text" : ndb.Key('Text', checksum).get().text,
			"captures" : captures,
			"total_captures" : len(captures),
			"unique_paths" : set([c.path for c in captures if c.path]), }

		self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([('/', MainPage),
	('/capture', CaptureHandler),
	('/detail', DetailPage),
	('/content/([a-f0-9]+)', ContentPage),],
                              debug=True)