import unittest
from webtest import TestApp
from google.appengine.ext import webapp
from google.appengine.api import urlfetch

from controllers.volunteers import *

from models.neighborhood import Neighborhood

class VolunteersTest(unittest.TestCase):
  
  def setUp(self):
    self.neighborhood1 = Neighborhood()
    self.neighborhood1.put()
    self.neighborhood2 = Neighborhood()
    self.neighborhood2.put()
    
  def tearDown(self):
    self.neighborhood1.delete()
    self.neighborhood2.delete()
  
  #dev_appserver.py can only handle on request at a time. Be smarter (run a second server)  
  def test_url(self):
      volunteer = Volunteer()
      volunteer.put()
      #response = urlfetch.fetch(volunteer.url)
      #self.assertEquals(0, response.content.find('<html>'))
      self.assertTrue(1)
      volunteer.delete()
  
  def test_validate_no_name(self):
    params = { 'name' : '' }
    volunteer = Volunteer()
    self.assertFalse(volunteer.validate(params))
    params['tosagree'] = '1'
    self.assertFalse(volunteer.validate(params))
    self.assertFalse((not 'tosagree' in params) or params['tosagree'] != '1')
  
  def test_validate_no_tos(self):
    params = { 'name' : 'a name!' }
    volunteer = Volunteer()
    self.assertTrue(not volunteer.is_saved())
    self.assertFalse(volunteer.validate(params))
    self.assertTrue((not 'tosagree' in params) or params['tosagree'] != '1')
    
  def test_validate_working(self):
    params = { 'name' : 'A. Nameous',
               'tosagree' : '1'}
    volunteer = Volunteer()
    self.assertTrue(volunteer.validate(params))

  def test_follow_friend(self):
    volunteer  = Volunteer()
    volunteer.put()
    follower = Volunteer()
    follower.put()
    
    vf = VolunteerFollower(volunteer = volunteer, follower = follower)
    vf.put()
    
    self.assertEqual(volunteer.volunteerfollowing.count(), 0)
    self.assertEqual(volunteer.volunteerfollowers.count(), 1)

    self.assertEqual(follower.volunteerfollowers.count(), 0)
    self.assertEqual(follower.volunteerfollowing.count(), 1)

    self.assertEqual(volunteer.followers().next().key().id, follower.key().id )
    self.assertEqual(follower.following().next().key().id, volunteer.key().id )
    
    fv = VolunteerFollower(volunteer = follower, follower = volunteer)
    fv.put()
    
    self.assertEqual(volunteer.volunteerfollowing.count(), 1)
    self.assertEqual(volunteer.volunteerfollowers.count(), 1)

    self.assertEqual(follower.volunteerfollowers.count(), 1)
    self.assertEqual(follower.volunteerfollowing.count(), 1)
    
    self.assertEqual(volunteer.followers().next().key().id, follower.key().id )
    self.assertEqual(follower.following().next().key().id, volunteer.key().id )
    
    self.assertEqual(volunteer.friends()[0].key().id, follower.key().id )
    self.assertEqual(follower.friends()[0].key().id, volunteer.key().id )

    vf.delete()
    
    self.assertEqual(volunteer.volunteerfollowing.count(), 1)
    self.assertEqual(volunteer.volunteerfollowers.count(), 0)

    self.assertEqual(follower.volunteerfollowers.count(), 1)
    self.assertEqual(follower.volunteerfollowing.count(), 0)
    
    fv.delete()
    
    self.assertEqual(volunteer.volunteerfollowing.count(), 0)
    self.assertEqual(volunteer.volunteerfollowers.count(), 0)

    self.assertEqual(follower.volunteerfollowers.count(), 0)
    self.assertEqual(follower.volunteerfollowing.count(), 0)
    
  def test_volunteer_search(self):
    v = VolunteersPage();

    search_params = { 'name' : 'testsearchy',
                      'email' : 'foo@foo.com', 
                      'neighborhood' : str(self.neighborhood1.key().id()), }

    (name, email, neighborhood, volunteers)  = v.do_search(search_params)
    
    self.assertEqual(name, search_params['name'])
    self.assertEqual(email, search_params['email'])
    self.assertEqual(neighborhood.key().id(), int(search_params['neighborhood']))
    self.assertEqual(len(volunteers), 0)
    
    # put in some test volunteers
    volunteer1 = Volunteer(name = 'search_name',
                          preferred_email = 'testsearch@example.com',
                          home_neighborhood = self.neighborhood1)
    volunteer1.put()
    volunteer2 = Volunteer(name = 'another search_name',
                          preferred_email = 'testsearch@examples.com',
                          home_neighborhood = self.neighborhood2)
    volunteer2.put()
    volunteer3 = Volunteer(name = 'another name',
                          preferred_email = '',
                          home_neighborhood = self.neighborhood1)
    volunteer3.put()

    # search by name
    search_params = { 'name' : 'search_name', }
    (name, email, neighborhood, volunteers)  = v.do_search(search_params)
    self.assertEqual(name, search_params['name'])
    self.assertEqual(email, None)
    self.assertEqual(neighborhood, None)
    self.assertEqual(len(volunteers), 1)
    volunteer = volunteers[0]
    self.assertEqual(volunteer.name, search_params['name'])
    
    # search by email
    search_params = { 'email' : 'testsearch@example.com', }
    (name, email, neighborhood, volunteers)  = v.do_search(search_params)
    self.assertEqual(name, None)
    self.assertEqual(email, search_params['email'])
    self.assertEqual(neighborhood, None)
    self.assertEqual(len(volunteers), 1)
    volunteer = volunteers[0]
    self.assertEqual(volunteer.preferred_email, search_params['email'])
    
    # search by neighborhood
    search_params = { 'neighborhood' : str(self.neighborhood1.key().id()), }
    (name, email, neighborhood, volunteers)  = v.do_search(search_params)
    self.assertEqual(name, None)
    self.assertEqual(email, None)
    self.assertEqual(neighborhood.key().id(), int(search_params['neighborhood']))
    self.assertEqual(len(volunteers), 2)
    volunteer = volunteers[0]
    self.assertEqual(volunteer.home_neighborhood.key().id(),int(search_params['neighborhood']))
    
    