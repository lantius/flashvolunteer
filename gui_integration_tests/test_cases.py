from selenium import selenium
import unittest, time, re

from gui_integration_tests.test_settings import host 
from gui_integration_tests.datastore_interface import populate, armageddon

class BaseTestCase(unittest.TestCase):
  populate = False 
  stop_selenium_on_completion = True
  
  def setUp(self):
    self.verificationErrors = []
    self.selenium = selenium("localhost", 4444, "*chrome", "http://%s"%host)
    self.selenium.start()
    
    self.volunteers = []
    self.events = []
    self.organizations = []
    
    if self.populate == True:
      populate(sessionid='test')
      
  def tearDown(self):
    sel = self.selenium
    
    #always logout at end of unit test
    try:
      sel.open("/_ah/login?action=Logout")
      sel.wait_for_page_to_load("30000")
    except Exception, e:
      print e 
      pass
    
    if self.stop_selenium_on_completion == True:
      sel.stop()
    
    if self.populate == True:
      armageddon(sessionid='test')

    self.assertEqual([], self.verificationErrors)

  
  
class AbstractLoginFirst(BaseTestCase):
  name = None
  admin = False
  
  def setUp(self):
    self.populate = True
    BaseTestCase.setUp(self)
  
    sel = self.selenium
  
    #login
    sel.open("/")
    sel.click("//span[@id='l_create_account']")
    sel.wait_for_page_to_load("30000")
    sel.type("email", self.name)
    if self.admin:
      sel.click("admin")
    sel.click("submit-login")
      
  
  
class LoginFirst_Volunteer(AbstractLoginFirst):
  
  def setUp(self):
    self.name = "volunteer0@test.org"
    AbstractLoginFirst.setUp(self)

class LoginFirst_Organization(AbstractLoginFirst):
  
  def setUp(self):
    self.name = "organization0@test.org"
    self.admin = True
    AbstractLoginFirst.setUp(self)
      
