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

class AllTodayHandler(webapp2.RequestHandler):
	def get(self):
		headers.json(self.response)

		cache_key = "json.today"

		json_result = memcache.get(cache_key)

		if not json_result:

			today = datetime.date.today()

			all_query = Summary.query(Summary.date == today).order(-Summary.count)

			def summary_as_map(summary):
				return {"count" : x.count,
					"text" : x.text,
					"detail_url" : "http://gu-text-catcher.appspot.com/content/{id}".format(id=x.checksum),
					}

			all_data = [summary_as_map(x) for x in all_query.iter()]

			json_result = json.dumps(all_data)

			memcache.set(cache_key, json_result, 60)

		self.response.out.write(jsonp(self.request, json_result))

app = webapp2.WSGIApplication([('/api/all', AllTodayHandler),],
                              debug=True)