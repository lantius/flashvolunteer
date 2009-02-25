import unittest
from webtest import TestApp
from google.appengine.ext import webapp

from controllers.events import *

class EventsTest(unittest.TestCase):
  def setUp(self):
    self.application = webapp.WSGIApplication([('/events', EventsPage)], debug=True)
    
    self.volunteer  = Volunteer()
    self.volunteer.put()
    
    self.interestcategory1 = InterestCategory()
    self.interestcategory1.put()

    self.interestcategory2 = InterestCategory()
    self.interestcategory2.put()
    
  def tearDown(self):
    self.volunteer.delete()
    self.interestcategory1.delete()
    self.interestcategory2.delete()
  
  # CREATE  
  def test_event_create(self):
    e = EventsPage()
    params = { 'name' : 'create unit test',
               'neighborhood' : 1,
               'interestcategory[' + str(self.interestcategory1.key().id()) + ']' : ['1','1'],
               'interestcategory[' + str(self.interestcategory2.key().id()) + ']' : '1'  }

    n = Event.all().count()
    event_id = e.create(params, self.volunteer)
    self.assertEqual(n+1, Event.all().count())

    event = Event.get_by_id(int(event_id))
    owner = EventVolunteer.gql("where event = :event", event=event).get()
    self.assertTrue(event)
    self.assertTrue(owner)
    self.assertTrue(owner.isowner)
    self.assertEqual(event.name, params['name'])
    self.assertEqual(event.neighborhood, Neighborhood.get_by_id(int(params['neighborhood'])))
    
    self.assertEqual(event.interestcategories().next().key().id, self.interestcategory1.key().id )
    
  # DELETE
  def test_event_delete(self):
    e = EventsPage()
    params = { 'name' : 'delete unit test',
               'neighborhood' : 1,
                'interestcategory[' + str(self.interestcategory1.key().id()) + ']' : ['1','1'],
                'interestcategory[' + str(self.interestcategory2.key().id()) + ']' : '1' }

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
    
  # UPDATE  
  def test_event_update(self):
    ee = EditEventPage()
    e = EventsPage()
    params = { 'name' : 'edit unit test',
               'neighborhood' : '1',
               'interestcategory[' + str(self.interestcategory1.key().id()) + ']' : ['1','1'],
               'interestcategory[' + str(self.interestcategory2.key().id()) + ']' : '1',
               }
    
    event_id = e.create(params, self.volunteer)

    event = Event.get_by_id(int(event_id))
    self.assertEqual(event.name, params['name'])
    self.assertEqual(event.neighborhood, Neighborhood.get_by_id(int(params['neighborhood'])))
    self.assertEqual(event.eventinterestcategories.count(), 1)
    self.assertEqual(event.interestcategories().next().key().id, self.interestcategory1.key().id )
    
    params = { 'id' : event_id, 
               'name' : 'edit unit test -- edited',
               'neighborhood' : '2',
               'interestcategory[' + str(self.interestcategory1.key().id()) + ']' : '1',
               'interestcategory[' + str(self.interestcategory2.key().id()) + ']' : ['1','1'],
    }
    ee.update(params, self.volunteer)
    
    event = Event.get_by_id(int(event_id))
    self.assertEqual(event.name, params['name'])
    self.assertEqual(event.neighborhood, Neighborhood.get_by_id(int(params['neighborhood'])))
    self.assertEqual(event.eventinterestcategories.count(), 1)
    self.assertEqual(event.interestcategories().next().key().id, self.interestcategory2.key().id )
