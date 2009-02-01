import unittest
from webtest import TestApp
from google.appengine.ext import webapp
from google.appengine.api import urlfetch

from controllers.events import *

class EventsTest(unittest.TestCase):
  def setUp(self):
      self.application = webapp.WSGIApplication([('/events', EventsPage)], debug=True)

  def test_event_create(self):
    
	name = 'create unit test'
	neighborhood = 1
	
	e = EventsPage()
	params = { 'name' : name,
	           'neighborhood' : neighborhood }
	volunteer = Volunteer()
	volunteer.put()

	n = Event.all().count()
	event_id = e.create(params, volunteer)
	self.assertEqual(n+1, Event.all().count())

	event = Event.get_by_id(int(event_id))
	owner = EventVolunteer.gql("where event = :event", event=event).get()
	self.assertTrue(event)
	self.assertTrue(owner)
	self.assertTrue(owner.isowner)
	self.assertEqual(event.name, name)
	self.assertEqual(event.neighborhood, Neighborhood.get_by_id(int(params['neighborhood'])))
	
	volunteer.delete()


  def test_event_delete(self):
	e = EventsPage()

	name = 'delete unit test'
	neighborhood = 1
	
	e = EventsPage()
	params = { 'name' : name,
	           'neighborhood' : neighborhood }
	volunteer = Volunteer()
	volunteer.put()

	n = Event.all().count()
	event_id = e.create(params, volunteer)
	self.assertEqual(n+1, Event.all().count())

	event = Event.get_by_id(int(event_id))
	owner = EventVolunteer.gql("where event = :event", event=event).get()
	self.assertTrue(event)
	self.assertTrue(owner)
	
	params['id'] = event_id
	params['delete'] = 'true'
	
	e.delete(params, volunteer)
	self.assertEqual(n, Event.all().count())
	
	event = Event.get_by_id(int(event_id))
	owner = EventVolunteer.gql("where event = :event", event=event).get()
	self.assertFalse(event)
	self.assertFalse(owner)
	
	volunteer.delete()

  def test_event_post_create(self):
	e = EventsPage()

	name = 'delete unit test'
	neighborhood = 1
	port = '8083'
	
	params = { 'name' : name,
	           'neighborhood' : neighborhood }

	e = EventsPage()
	volunteer = Volunteer()
	volunteer.put()
	
	#e.post(params)
	
	volunteer.delete()