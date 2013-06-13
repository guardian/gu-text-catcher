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


class DeleteHandler(webapp2.RequestHandler):
	def get(self, checksum):
		captures_qry = CapturedSelection.query(CapturedSelection.checksum == checksum)

		count = 0
		for capture in captures_qry.iter():
			capture.key.delete()
			count += 1

		headers.json(self.response)
		self.response.out.write({"Entries deleted" : count})


app = webapp2.WSGIApplication([
	('/admin/delete/([a-f0-9]+)', DeleteHandler),],
                              debug=True)