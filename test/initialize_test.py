import unittest
from webtest import TestApp
from google.appengine.ext import webapp

from controllers.home import *

class InititalizeTest(unittest.TestCase):
  def setUp(self):
    self.application = webapp.WSGIApplication([('/events', EventsPage)], debug=True)
  
  def test_initialize_store(self):
    i = InitializeStore()
    
    self.assertFalse(i.is_initialized())
    i.initialize_store()
    self.assertTrue(i.is_initialized())
    
    