import unittest
from webtest import TestApp
from google.appengine.ext import webapp

from controllers._helpers import InitializeStore

class InititalizeTest(unittest.TestCase):
  def test_initialize_store(self):
    i = InitializeStore()
    
    self.assertFalse(i.is_initialized())
    i.initialize_store()
    self.assertTrue(i.is_initialized())
    
    