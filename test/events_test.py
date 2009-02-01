import unittest
from webtest import TestApp
from google.appengine.ext import webapp
from controllers.events import *

class EventsTest(unittest.TestCase):
  def setUp(self):
      self.application = webapp.WSGIApplication([('/events', EventsPage)], debug=True)

  def test_event_create(self):
    
    e = EventsPage()
    params = { 'name' : 'failgate party',
               'neighborhood' : 1 }
    volunteer = Volunteer()
    volunteer.put()

    n = Event.all().count()
    ekey = e.create(params, volunteer)
    self.assertEqual(n+1, Event.all().count())
    
  def test_event_delete(self):
    e = EventsPage()