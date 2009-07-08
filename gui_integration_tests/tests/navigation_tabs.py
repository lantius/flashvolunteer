from selenium import selenium
import unittest, time, re, os
from gui_integration_tests.test_cases import BaseTestCase, TestEnv


class TestOrganizationNavigation(BaseTestCase):

  test_env = TestEnv(
     organization = True,
     create_new_user = True)
  
  
  #TODO: This is bad, we don't want to test again copy. We should be IDs on the fields
  #      it looks for and look for those instead.
  def test_nav_menu(self):
    
    
    sel = self.selenium
    sel.wait_for_page_to_load("30000")
    sel.click("//a[@id='l_events']") # This takes you back to the profile page
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("My Upcoming Events"))

    sel.click("//a[@id='l_neighborhoods']")
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("Supported Neighborhoods"))
    
    sel.click("//a[@id='l_friends']")
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("My FlashTeam"))
    
    sel.click("//a[@id='l_help']")
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("Temporary Help Information"))
    
    sel.click("//a[@id='l_profile']") # Go to the profile page last
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("Change picture"))
    
    sel.click("//a[@id='l_create_event']") 
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("Create An Event"))
    
class TestVolunteerNavigation(BaseTestCase):
  test_env = TestEnv()

  def test_nav_menu(self):
    sel = self.selenium
    sel.wait_for_page_to_load("30000")
    sel.click("//a[@id='l_events']") # This takes you back to the profile page
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("My Upcoming Events"))

    sel.click("//a[@id='l_neighborhoods']")
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("Supported Neighborhoods"))
    
    sel.click("//a[@id='l_friends']")
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("My FlashTeam"))
    
    sel.click("//a[@id='l_help']")
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("Temporary Help Information"))
    
    sel.click("//a[@id='l_profile']") # Go to the profile page last
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("Change picture"))
        
        
if __name__ == "__main__":
    unittest.main()
