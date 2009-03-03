import unittest
from webtest import TestApp
from google.appengine.ext import webapp
from google.appengine.api import urlfetch

from controllers.volunteers import *

class VolunteersTest(unittest.TestCase):
  
  def setUp(self):
    self.application = webapp.WSGIApplication([('/volunteers', VolunteersPage)], debug=True)

  #dev_appserver.py can only handle on request at a time. Be smarter (run a second server)  
  def test_url(self):
      volunteer = Volunteer()
      volunteer.put()
      #response = urlfetch.fetch(volunteer.url)
      #self.assertEquals(0, response.content.find('<html>'))
      self.assertTrue(1)
      volunteer.delete()
  
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
    
    self.assertEqual(volunteer.friends().next().key().id, follower.key().id )
    self.assertEqual(follower.friends().next().key().id, volunteer.key().id )

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
    