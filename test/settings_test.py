import unittest
from webtest import TestApp
from google.appengine.ext import webapp
from google.appengine.api import users

from controllers.settings import *
from controllers.volunteers import *

class SettingsTest(unittest.TestCase):
  def setUp(self):
    self.application = webapp.WSGIApplication([('/settings', SettingsPage)], debug=True)
    self.user = users.get_current_user()

    self.interestcategory1 = InterestCategory()
    self.interestcategory1.put()

    self.interestcategory2 = InterestCategory()
    self.interestcategory2.put()

  def tearDown(self):
    self.interestcategory1.delete()
    self.interestcategory2.delete() 

  # UPDATE
  def test_update(self):
    params = {'home_neighborhood' : 1,
              'work_neighborhood' : 2,
              'quote' : 'test quote',
              'name' : 'test name',
              'avatar' : None }
        
    s = SettingsPage()
    v = Volunteer()
    v.home_neighborhood = Neighborhood.get_by_id(params['home_neighborhood'])
    v.work_neighborhood = Neighborhood.get_by_id(params['work_neighborhood'])
    v.quote = params['quote']
    v.name = params['name']
    v.put()
    self.assertEqual(v.home_neighborhood, Neighborhood.get_by_id(params['home_neighborhood']))
    self.assertEqual(v.work_neighborhood, Neighborhood.get_by_id(params['work_neighborhood']))
    self.assertEqual(v.quote, params['quote'])
    self.assertEqual(v.name, params['name'])
    self.assertEqual(v.volunteerinterestcategories.count(), 0)
    
    # now update the new volunteeer
    params = {'home_neighborhood' : 2,
              'work_neighborhood' : 3,
              'quote' : 'updated test quote',
              'name' : 'updated test name',
              'avatar' : None, 
              'interestcategory[' + str(self.interestcategory1.key().id()) + ']' : ['1','1'],
              'interestcategory[' + str(self.interestcategory2.key().id()) + ']' : '1' }
    s.update(params, v)
    self.assertEqual(v.home_neighborhood, Neighborhood.get_by_id(params['home_neighborhood']))
    self.assertEqual(v.work_neighborhood, Neighborhood.get_by_id(params['work_neighborhood']))
    self.assertEqual(v.quote, params['quote'])
    self.assertEqual(v.name, params['name'])
    self.assertEqual(v.volunteerinterestcategories.count(), 1)
    self.assertEqual(v.interestcategories().next().key().id, self.interestcategory1.key().id )

    params = {'home_neighborhood' : 2,
              'work_neighborhood' : 3,
              'quote' : 'updated test quote',
              'name' : 'updated test name',
              'avatar' : None, 
              'interestcategory[' + str(self.interestcategory1.key().id()) + ']' : '1',
              'interestcategory[' + str(self.interestcategory2.key().id()) + ']' : ['1','1'], }
    s.update(params, v)
    self.assertEqual(v.home_neighborhood, Neighborhood.get_by_id(params['home_neighborhood']))
    self.assertEqual(v.work_neighborhood, Neighborhood.get_by_id(params['work_neighborhood']))
    self.assertEqual(v.quote, params['quote'])
    self.assertEqual(v.name, params['name'])
    self.assertEqual(v.volunteerinterestcategories.count(), 1)
    self.assertEqual(v.interestcategories().next().key().id, self.interestcategory2.key().id )

  
  # DELETE
  def test_delete(self):
    s = SettingsPage()
    v = Volunteer()
    v.put()
    follower = Volunteer()
    follower.put()
    
    n = Volunteer.all().count()
    
    vf = VolunteerFollower(volunteer = v, follower = follower)
    vf.put()
    fv = VolunteerFollower(volunteer = follower, follower = v)
    fv.put()
    
    self.assertEqual(v.volunteerfollowing.count(), 1)
    self.assertEqual(v.volunteerfollowers.count(), 1)

    self.assertEqual(follower.volunteerfollowers.count(), 1)
    self.assertEqual(follower.volunteerfollowing.count(), 1)
    
    s.delete(v)
    
    self.assertEqual(n-1, Volunteer.all().count())
    self.assertEqual(follower.volunteerfollowers.count(), 0)
    self.assertEqual(follower.volunteerfollowing.count(), 0)  
    
    
    
    
    
    