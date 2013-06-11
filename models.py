from google.appengine.ext import ndb

class Configuration(ndb.Model):
	key = ndb.StringProperty()
	value = ndb.StringProperty()

class CapturedSelection(ndb.Model):
	checksum = ndb.StringProperty()
	text = ndb.StringProperty()
	datetime = ndb.DateTimeProperty(auto_now_add=True)