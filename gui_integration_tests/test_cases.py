from selenium import selenium
import unittest, time, re

from gui_integration_tests.test_settings import host 
from gui_integration_tests.datastore_interface import create_environment, armageddon, delete_user, set_create_rights


class TestEnv(object):
    
    def __init__(self, 
                 login_email = 'test@example.com', #set to None if you don't want to login as anyone
                 login_name = None,
                 organization = False, 
                 fv_environment = 'revolutionary_war',
                 create_new_user = None):

        self.login_email = login_email
        if login_name is None: 
            self.login_name = login_email
        else:
            self.login_name = login_name
            
        self.organization = organization
        self.fv_environment = fv_environment
        self.create_new_user = create_new_user



class BaseTestCase(unittest.TestCase):
  populate = False 
  stop_selenium_on_completion = False
  
  def setUp(self):
    try: 
        env = getattr(self, "test_env")
    except:
        raise 'FV test cases require test_env to be set (type: TestEnv)'
        
    if self.test_env.fv_environment is not None:
      self.test_objects = create_environment(name = self.test_env.fv_environment,
                                             session_id='test')
      self.test_object_index = []
      for k,v in self.test_objects.items():
          try:
              self.test_object_index += [(o.name, o) for o in v]
          except: pass
          
      self.test_object_index = dict(self.test_object_index)

    self.selenium = selenium("localhost", 4444, "*chrome", "http://%s"%host)
    self.selenium.start()
    
    if self.test_env.login_email is not None:
        if self.test_env.create_new_user:
            self.login_as_new_user()
        else:
            self.login_as_existing_user()
            
            
  def tearDown(self):
    sel = self.selenium
    
    #always logout at end of unit test
    try:
      sel.open("/_ah/login?action=Logout")
      sel.wait_for_page_to_load("30000")
    except Exception, e:
      print 'Could not logout of seleniumn: ' + str(e) 
      pass
    
    if self.stop_selenium_on_completion == True:
      sel.stop()
      
    try:
        armageddon(test_objects = self.test_objects)
    except Exception, e:
        raise 'Test environment cleanup failure: ' + str(e)
    

  def login_as_new_user(self):
    #login
    try:
        delete_user(name = self.test_env.login_email)
    except:
        pass
    
    self.selenium.open("/")
    self.selenium.click("//span[@id='l_create_account']")
    self.selenium.wait_for_page_to_load("30000")
    self.selenium.type("email", self.test_env.login_email)
    if self.test_env.organization:
      self.selenium.click("admin")
    self.selenium.click("submit-login")

    self.selenium.wait_for_page_to_load("30000")
    self.selenium.click("tosagree")
    self.selenium.click("s_create_account")
    self.selenium.wait_for_page_to_load("30000")   
    
    if self.test_env.organization: 
        set_create_rights(name = self.test_env.login_name)
        self.selenium.refresh()
        self.selenium.wait_for_page_to_load("30000")  
    
  
  def login_as_existing_user(self):
    #login
    self.selenium.open("/")
    self.selenium.click("//span[@id='l_login']")
    self.selenium.wait_for_page_to_load("30000")
    self.selenium.type("email", self.test_env.login_email)
    if self.test_env.organization:
      self.selenium.click("admin")
    self.selenium.click("submit-login")
    self.selenium.wait_for_page_to_load("30000")  

    if self.test_env.organization:      
      set_create_rights(name = self.test_env.login_name)
      self.selenium.refresh()
      self.selenium.wait_for_page_to_load("30000")   
          
          