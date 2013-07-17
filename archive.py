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
from tuples import SummaryInfo, ArchiveLink

jinja_environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), "templates")),
    autoescape=True,
    extensions=['jinja2.ext.autoescape'])

class ArchiveToday(webapp2.RequestHandler):
	def get(self):
		today = datetime.date.today().isoformat()
		self.redirect('/archive/' + today)

class Archive(webapp2.RequestHandler):
	def get(self, target_date, restriction=None):
		template = jinja_environment.get_template('index.html')
		
		template_values = {}

		cache_key = "today." + target_date

		all_data = memcache.get(cache_key)

		target_day = datetime.datetime.strptime(target_date, '%Y-%m-%d').date()

		if not all_data:

			all_query = Summary.query(Summary.date == target_day, Summary.count > 1).order(-Summary.count)

			all_data = [SummaryInfo(count=x.count, text=x.text, checksum=x.checksum, length=len(x.text)) for x in all_query.iter()]

			try:
				memcache.set(cache_key, all_data, 5 * 60)
			except:
				pass

		template_values["all"] = all_data

		headers.set_cache_headers(self.response, 60)

		self.response.out.write(template.render(template_values))

class ArchiveList(webapp2.RequestHandler):
	def get(self):
		template = jinja_environment.get_template('archive.html')

		def create_link(offset_days):
			link_date = datetime.date.today() - datetime.timedelta(days=i)
			return ArchiveLink(link="/archive/%s" % link_date.isoformat(), label=link_date.strftime('%d/%m/%Y (%A)'))


		template_values = {'dates' : [create_link(i) for i in range(0, 7)]}
		self.response.out.write(template.render(template_values))

app = webapp2.WSGIApplication([
	('/archive', ArchiveList),
	('/archive/today', ArchiveToday),
	webapp2.Route('/archive/<target_date>', handler=Archive),
	webapp2.Route('/archive/<target_date>/<restriction>', handler=Archive),],
                              debug=True)