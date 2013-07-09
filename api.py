import webapp2
import jinja2
import os
import json
import logging
import hashlib
import datetime
from collections import namedtuple

from urlparse import urlparse

from urllib import quote, urlencode
from google.appengine.api import urlfetch
from google.appengine.ext import ndb
from google.appengine.api import memcache
from google.appengine.ext.webapp import template

import headers
from models import CapturedSelection, Text, Summary
from tuples import SummaryInfo
from formats import jsonp

def read_summary_data(target_date):
	all_query = Summary.query(Summary.date == target_date, Summary.count > 5).order(-Summary.count)

	def summary_as_map(summary):
		return {"count" : x.count,
			"text" : x.text,
			"detail_url" : "http://gu-text-catcher.appspot.com/content/{id}".format(id=x.checksum),
			}

	return [summary_as_map(x) for x in all_query.iter()]

class AllTodayHandler(webapp2.RequestHandler):
	def get(self):
		headers.json(self.response)

		cache_key = "json.today"

		json_result = memcache.get(cache_key)

		if not json_result:

			today = datetime.date.today()

			json_result = json.dumps(read_summary_data(today))

			try:
				memcache.set(cache_key, json_result, 60)
			except:
				pass

		headers.set_cache_headers(self.response, 60)

		self.response.out.write(jsonp(self.request, json_result))

class HistoricDayHandler(webapp2.RequestHandler):
	def get(self, target_date):
		headers.json(self.response)

		cache_key = "json.%s" % target_date

		json_result = memcache.get(cache_key)

		if not json_result:

			archive_date = datetime.datetime.strptime(target_date, '%Y-%m-%d')

			json_result = json.dumps(read_summary_data(archive_date))

			try:
				memcache.set(cache_key, json_result, 60)
			except:
				pass

		headers.set_cache_headers(self.response, 60)

		self.response.out.write(jsonp(self.request, json_result))


app = webapp2.WSGIApplication([
	('/api/all', AllTodayHandler),
	webapp2.Route('/api/archive/<target_date:\d{4}-\d{2}-\d{2}>',
		handler=HistoricDayHandler),],
                              debug=True)