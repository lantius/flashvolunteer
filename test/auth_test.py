import unittest
from webtest import TestApp
from google.appengine.ext import webapp
from google.appengine.api import users

from controllers._auth import *

# http://appengine-cookbook.appspot.com/recipe/testing-apps-with-authentication/
class AuthorizeTest(unittest.TestCase):
  def setUp(self):
    self.temp_gcu = users.get_current_user
  
  def tearDown(self):
    users.get_current_user = self.temp_gcu
    
  def login(self, user):
    users.get_current_user = lambda user=user : users.User(user) if user else None

  def logout(self):
    self.login(None)

  #### ugly testing harness idea ####
  class harness_req():
    class harness_request():

      def get(self, id):
        return self.params[id]
    
      method = 'GET'
      uri = '/'
      
    request = harness_request()
    
    new_url = None
    
    def redirect(self, url):
      self.new_url = url
  #### ugliness ends here #### 
  
  def test_login(self):
    req = self.harness_req()
    req.request.method = "GET"

    self.login('test@example.com')
    
    user = users.get_current_user()
    volunteer = Authorize.login(req, requireVolunteer=False, redirectTo='/test_url')
    self.assertEqual(volunteer, None)

    volunteer  = Volunteer()
    volunteer.user = user
    volunteer.put()
    
    volunteer = Authorize.login(req, requireVolunteer=False, redirectTo='/test_url')
    self.assertEqual(volunteer.user.email(), 'test@example.com')
    
    self.logout()
    volunteer = Authorize.login(req, requireVolunteer=True, redirectTo='/test_url')
    
    #login_url = users.create_login_url('/')
    #self.assertEqual(req.new_url, login_url)

    self.login('test-2@example.com')
    volunteer = Authorize.login(req, requireVolunteer=True, redirectTo='/test_url')
    
    self.assertEqual(req.new_url, '/test_url')
    
  def test_authenticated_post(self):  
    req = self.harness_req()
    req.request.method = "POST"
    req.request.params = {'session_id' : '12345'}
    
    self.login('test@example.com')
    user = users.get_current_user()
    volunteer  = Volunteer()
    volunteer.user = user
    volunteer.session_id = '12345'
    volunteer.put()

    self.assertEqual(req.request.method, 'POST')
    self.assertEqual(req.request.get('session_id'), '12345')
    self.assertEqual(volunteer.session_id, '12345')
    self.assertTrue(volunteer.check_session_id(req.request.get('session_id')))
    volunteer = Authorize.login(req, requireVolunteer=True, redirectTo='/test_url')
    self.assertEqual(volunteer.user.email(), 'test@example.com')
    
    volunteer.session_id = 'abcde'
    volunteer.put()
    
    self.assertEqual(req.request.method, 'POST')
    self.assertEqual(req.request.get('session_id'), '12345')
    self.assertEqual(volunteer.session_id, 'abcde')
    self.assertFalse(volunteer.check_session_id(req.request.get('session_id')))
    
    volunteer = Authorize.login(req, requireVolunteer=True, redirectTo='/test_url')
    self.assertEqual(req.new_url, '/timeout')
    
