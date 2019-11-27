from google.appengine.ext import ndb

class Event(ndb.Model):
    venue = ndb.StringProperty()
    location = ndb.StringProperty()
    date = ndb.DateProperty()
    time = ndb.StringProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    created_by = ndb.UserProperty()
    updated_by = ndb.UserProperty()

class News(ndb.Model):
    title = ndb.StringProperty()
    body = ndb.TextProperty()
    expiry = ndb.DateTimeProperty()
    created = ndb.DateTimeProperty(auto_now_add=True)
    updated = ndb.DateTimeProperty(auto_now=True)
    created_by = ndb.UserProperty()
    updated_by = ndb.UserProperty()
