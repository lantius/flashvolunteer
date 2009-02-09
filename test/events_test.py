import unittest
from webtest import TestApp
from google.appengine.ext import webapp

from controllers.events import *

class EventsTest(unittest.TestCase):
  def setUp(self):
    self.application = webapp.WSGIApplication([('/events', EventsPage)], debug=True)
    
    self.volunteer  = Volunteer()
    self.volunteer.put()
    
  def tearDown(self):
    self.volunteer.delete()
    
  def test_event_create(self):
    name = 'create unit test'
    neighborhood = 1

    e = EventsPage()
    params = { 'name' : name,
               'neighborhood' : neighborhood }

    n = Event.all().count()
    event_id = e.create(params, self.volunteer)
    self.assertEqual(n+1, Event.all().count())

    event = Event.get_by_id(int(event_id))
    owner = EventVolunteer.gql("where event = :event", event=event).get()
    self.assertTrue(event)
    self.assertTrue(owner)
    self.assertTrue(owner.isowner)
    self.assertEqual(event.name, name)
    self.assertEqual(event.neighborhood, Neighborhood.get_by_id(int(params['neighborhood'])))

  def test_event_delete(self):
    e = EventsPage()
    params = { 'name' : 'delete unit test',
               'neighborhood' : 1 }

    n = Event.all().count()
    event_id = e.create(params, self.volunteer)

    params = { 'id' : event_id, 
               'delete' : 'true' }
    e.delete(params, self.volunteer)
    self.assertEqual(n, Event.all().count())
  
    event = Event.get_by_id(int(event_id))
    owner = EventVolunteer.gql("where event = :event", event=event).get()
    self.assertFalse(event)
    self.assertFalse(owner)
  
  def test_event_post_create(self):
    e = EventsPage()
    
    name = 'delete unit test'
    neighborhood = 1
    port = '8083'
    
    params = { 'name' : name,
               'neighborhood' : neighborhood }
    
    e = EventsPage()
    
    #e.post(params)
    
  def test_event_update(self):
    ee = EditEventPage()
    e = EventsPage()
    params = { 'name' : 'edit unit test',
               'neighborhood' : 1 }
    
    event_id = e.create(params, self.volunteer)
    
    params = { 'id' : event_id, 
               'name' : 'edit unit test -- edited',
               'neighborhood' : 2, 
    }
    ee.update(params, self.volunteer)
    
    event = Event.get_by_id(int(event_id))
    self.assertEqual(event.name, params['name'])
    self.assertEqual(event.neighborhood, Neighborhood.get_by_id(int(params['neighborhood'])))
