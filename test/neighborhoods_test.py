import unittest
from webtest import TestApp
from google.appengine.ext import webapp
from google.appengine.api import urlfetch

from models.neighborhood import *

class NeighborhoodsTest(unittest.TestCase):
  
  #dev_appserver.py can only handle on request at a time. Be smarter (run a second server)
  def test_url(self):      
      neighborhood = Neighborhood()
      neighborhood.put()
      #response = urlfetch.fetch(neighborhood.url())
      #response = urlfetch.fetch('http://localhost:8083/')
      #self.assertEquals(0, response.conten.find('<html>'))
      self.assertTrue(1)
      neighborhood.delete()
