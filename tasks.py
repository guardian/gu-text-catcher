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

jinja_environment.filters['nice_timestamp'] = nice_timestamp

class MainPage(webapp2.RequestHandler):
	def get(self):

		cache_key = "today.all"

		all_data = memcache.get(cache_key)

		today = datetime.date.today()

		if not all_data:

			all_query = Summary.query(Summary.date == today, Summary.count > 1).order(-Summary.count)

			all_data = [SummaryInfo(count=x.count, text=x.text, checksum=x.checksum) for x in all_query.iter()]

			memcache.set(cache_key, all_data, 45)

		self.response.out.write("OK")




app = webapp2.WSGIApplication([('/tasks/summary', SummaryGenerator),],
                              debug=True)