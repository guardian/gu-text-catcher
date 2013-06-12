from google.appengine.ext import ndb

class Configuration(ndb.Model):
	key = ndb.StringProperty()
	value = ndb.StringProperty()

class CapturedSelection(ndb.Model):
	checksum = ndb.StringProperty(required=True)
	text = ndb.StringProperty(required=True)
	datetime = ndb.DateTimeProperty(auto_now_add=True)
	path = ndb.StringProperty()

class Text(ndb.Model):
	text = ndb.StringProperty(required=True)

class Summary(ndb.Model):
	checksum = ndb.StringProperty(required=True)
	text = ndb.StringProperty(required=True)
	count = ndb.IntegerProperty(default=0)
	size = ndb.IntegerProperty(required=True)
	date = ndb.DateProperty(auto_now_add=True)
