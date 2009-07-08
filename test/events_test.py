import unittest
from webtest import TestApp
from google.appengine.ext import webapp

from controllers.events import *
from controllers.eventattendance import *

class EventsTest(unittest.TestCase):
  
  def setUp(self):
    self.application = webapp.WSGIApplication([('/events', EventsPage)], debug=True)
    
    self.volunteer  = Volunteer()
    self.volunteer.create_rights = True
    self.volunteer.put()
    
    self.interestcategory1 = InterestCategory()
    self.interestcategory1.put()

    self.interestcategory2 = InterestCategory()
    self.interestcategory2.put()
    
    self.neighborhood1 = Neighborhood()
    self.neighborhood1.put()
    
    self.neighborhood2 = Neighborhood()
    self.neighborhood2.put()
    
  def tearDown(self):
    self.volunteer.delete()
    self.interestcategory1.delete()
    self.interestcategory2.delete()
    self.neighborhood1.delete()
    self.neighborhood2.delete()
  
  # CREATE  
  def test_event_create(self):
    e = EventsPage()
    params = { 'name' : 'create unit test',
               'neighborhood' : 1,
               'date' : '01/01/2009',
               'time' : '03:00',
               'duration' : '2',               
               'description' : 'test description\non the internet with two lines!',
               'special_instructions' : 'special instructions',
               'address' : '3334 NE Blakeley St.\nSeattle, WA 98105',
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
    self.assertEqual(event.date.strftime("%m/%d/%Y"), params['date'])
    self.assertEqual(event.duration, int(params['duration']))
    self.assertEqual(event.date.strftime("%H:%M"), params['time'])
    self.assertEqual(event.description, params['description'])
    self.assertEqual(event.neighborhood, Neighborhood.get_by_id(int(params['neighborhood'])))
    
    self.assertEqual(event.interestcategories().next().key().id, self.interestcategory1.key().id )
    return event
    
  # DELETE
  def test_event_delete(self):
    e = EventsPage()

    n = Event.all().count()
    event_id = self.test_event_create().key().id()
    
    e.delete(event_id, self.volunteer)
    self.assertEqual(n, Event.all().count())

    event = Event.get_by_id(int(event_id))
    owner = EventVolunteer.gql("where event = :event", event=event).get()
    self.assertFalse(event)
    self.assertFalse(owner)
    
  # UPDATE  
  def test_event_update(self):
    e = EventsPage()
    event = self.test_event_create()

    params = { 'id' : event.key().id() , 
               'name' : 'edit unit test -- edited',
               'date' : '01/02/2009',
               'time' : '13:00',
               'duration' : '2',               
               'description' : 'test description -- edited',
               'special_instructions' : 'special instructions',
               'address' : '3334 NE Blakeley St. Seattle, WA 98105',
               'neighborhood' : '2',
               'interestcategory[' + str(self.interestcategory1.key().id()) + ']' : '1',
               'interestcategory[' + str(self.interestcategory2.key().id()) + ']' : ['1','1'],
    }
    e.update(params, self.volunteer)
    
    event = Event.get_by_id(int(event.key().id() ))
    self.assertEqual(event.name, params['name'])
    self.assertEqual(event.date.strftime("%m/%d/%Y"), params['date'])    
    self.assertEqual(event.description, params['description'])
    self.assertEqual(event.neighborhood, Neighborhood.get_by_id(int(params['neighborhood'])))
    self.assertEqual(event.eventinterestcategories.count(), 1)
    self.assertEqual(event.interestcategories().next().key().id, self.interestcategory2.key().id )

  # SEARCH
  def test_event_search(self):
    e = EventsPage()
    search_params = { 'neighborhood' : str(self.neighborhood1.key().id()),
                      'fromdate' : '12/12/2008', 
                      'todate' : '01/01/2010', }
    (neighborhood, fromdate, todate, events) = e.do_search(search_params)
    
    self.assertEqual(neighborhood.key().id(), int(search_params['neighborhood']))
    self.assertEqual(fromdate.strftime("%m/%d/%Y"), search_params['fromdate'])    
    self.assertEqual(todate.strftime("%m/%d/%Y"), search_params['todate'])    
    self.assertEqual(len(events), 0)    
    
    # insert 3 events to play with
    event_params = { 'name' : 'create unit test',
               'neighborhood' : str(self.neighborhood1.key().id()),
               'date' : '01/01/2009',
               'time' : '15:00',
               'duration' : '2',
               'description' : 'test description',
               'special_instructions' : 'special instructions',
               'address' : '3334 NE Blakeley St. Seattle, WA 98105',
               'interestcategory[' + str(self.interestcategory1.key().id()) + ']' : ['1','1'],
               'interestcategory[' + str(self.interestcategory2.key().id()) + ']' : '1'  }
    event_id = e.create(event_params, self.volunteer)

    event_params = { 'name' : 'create unit test',
               'neighborhood' : str(self.neighborhood1.key().id()),
               'date' : '01/02/2010',
               'time' : '23:01',
               'duration' : '3',
               'description' : 'test description',
               'special_instructions' : 'special instructions',
               'address' : '3334 NE Blakeley St. Seattle, WA 98105',
               'interestcategory[' + str(self.interestcategory1.key().id()) + ']' : ['1','1'],
               'interestcategory[' + str(self.interestcategory2.key().id()) + ']' : '1'  }
    event_id = e.create(event_params, self.volunteer)

    event_params = { 'name' : 'create unit test',
               'neighborhood' : str(self.neighborhood2.key().id()),
               'date' : '05/05/2008',
               'time' : '12:01',   
               'duration' : '1',
               'description' : 'test description',
               'special_instructions' : 'special instructions',
               'address' : '3334 NE Blakeley St. Seattle, WA 98105',
               'interestcategory[' + str(self.interestcategory1.key().id()) + ']' : ['1','1'],
               'interestcategory[' + str(self.interestcategory2.key().id()) + ']' : '1'  }
    event_id = e.create(event_params, self.volunteer)

    (neighborhood, fromdate, todate, events) = e.do_search(search_params)
    self.assertEqual(len(events), 1)
    
    event = events[0]
    self.assertEqual(event.neighborhood.key().id(), int(search_params['neighborhood']))
    self.assertTrue(event.date >= fromdate)
    self.assertTrue(event.date <= todate)
    
    search_params = { 'neighborhood' : 'bad neighborhood',
                      'fromdate' : 'bad fromdate', 
                      'todate' : 'bad to date', }
    (neighborhood, fromdate, todate, events) = e.do_search(search_params)
    self.assertEqual(neighborhood, None)    
    self.assertEqual(fromdate, None)    
    self.assertEqual(todate, None)    
    self.assertEqual(len(events), 3)

  # VERIFY
  def test_event_verify_attendance(self):
    event = self.test_event_create()
    attender = Volunteer()
    attender.put()
    
    eventvolunteer = EventVolunteer(volunteer=attender, event=event, isowner=False)
    eventvolunteer.put()
    
    vf = VerifyEventAttendance()
    params = { 'id' : str(event.key().id()),
               'event_volunteer_' + str(eventvolunteer.key().id()) : 'True',
               'hours_' + str(eventvolunteer.key().id()) : '3'  }
    
    vf.update(params, self.volunteer)
    
    eventvolunteer = EventVolunteer.get_by_id(eventvolunteer.key().id())
    self.assertTrue(eventvolunteer.attended)
    self.assertEqual(3, eventvolunteer.hours)
    
    attender = Volunteer()
    attender.put()
    
    eventvolunteer = EventVolunteer(volunteer=attender, event=event, isowner=False)
    eventvolunteer.put()
    
    vf = VerifyEventAttendance()
    params = { 'id' : str(event.key().id()),
               'event_volunteer_' + str(eventvolunteer.key().id()) : 'True'  }
    
    vf.update(params, self.volunteer)
    
    eventvolunteer = EventVolunteer.get_by_id(eventvolunteer.key().id())
    self.assertTrue(eventvolunteer.attended)
    self.assertEqual(None, eventvolunteer.hours)
    
  # VALIDATE
  def test_event_validate(self):
    event = Event()
    params = { 'name' : 'create unit test',
               'neighborhood' : str(self.neighborhood1.key().id()),
               'date' : '01/01/2009',
               'time' : '03:00',
               'duration' : '2',               
               'description' : 'test description\non the internet with two lines!',
               'special_instructions' : 'special instructions',
               'address' : '3334 NE Blakeley St.\nSeattle, WA 98105',
               'interestcategory[' + str(self.interestcategory1.key().id()) + ']' : ['1','1'],
               'interestcategory[' + str(self.interestcategory2.key().id()) + ']' : '1'  }

    for p in params.keys():
      self.assertEqual(None, event.error.get(p))
    
    
    