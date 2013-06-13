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

class AllTodayHandler(webapp2.RequestHandler):
	def get(self):
		headers.json(self.response)

		today = datetime.date.today()

		all_query = Summary.query(Summary.date == today).order(-Summary.count)

		def summary_as_map(summary):
			return {"count" : x.count,
				"text" : x.text,
				"detail_url" : "http://gu-text-catcher.appspot.com/content/{id}".format(id=x.checksum),
				}

		all_data = [summary_as_map(x) for x in all_query.iter()]

		self.response.out.write(json.dumps(all_data))

app = webapp2.WSGIApplication([('/api/all', AllTodayHandler),],
                              debug=True)