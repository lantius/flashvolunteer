from gui_integration_tests.test_cases import BaseTestCase, TestEnv

from gui_integration_tests.datastore_interface import get_events, delete_event

from selenium import selenium
import unittest

class TestSocialNetworkOperations(BaseTestCase):
  test_env = TestEnv(
     organization = False,
     create_new_user = False,
     login_email = 'thomas_jefferson@volunteer.org',
     login_name = 'Thomas Jefferson'
     )

    

  def test_default_environment_privacy_settings__friend_list(self):
    
    sel = self.selenium
    
    sel.click("//a[@id='l_friends']")
    sel.wait_for_page_to_load("30000")
    
    self.failUnless(sel.is_text_present("Aaron Burr"))
    self.failUnless(sel.is_text_present("Benjamin Harrison"))
    self.failUnless(sel.is_text_present("George Wythe"))
    self.failUnless(sel.is_text_present("James Madison"))

    
    sel.click("//a[@id='volunteer_link[%i]']"%self.test_object_index['Aaron Burr'].key().id())
    sel.wait_for_page_to_load("30000")
    self.failUnless(not sel.is_text_present("Upcoming Events"))

    sel.click("//a[@id='l_friends']")
    sel.wait_for_page_to_load("30000")
    
    sel.click("//a[@id='volunteer_link[%i]']"%self.test_object_index['Benjamin Harrison'].key().id())
    sel.wait_for_page_to_load("30000")
    self.failUnless(not sel.is_text_present("Upcoming Events"))

    sel.click("//a[@id='l_friends']")
    sel.wait_for_page_to_load("30000")

    sel.click("//a[@id='volunteer_link[%i]']"%self.test_object_index['George Wythe'].key().id())
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("Upcoming Events"))

    sel.click("//a[@id='l_friends']")
    sel.wait_for_page_to_load("30000")

    sel.click("//a[@id='volunteer_link[%i]']"%self.test_object_index['James Madison'].key().id())
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_text_present("Upcoming Events"))

    sel.click("//a[@id='l_friends']")
    sel.wait_for_page_to_load("30000")

  def test_adding_to_family__friend_list(self):
      
    sel = self.selenium
    
    sel.click("//a[@id='l_friends']")
    sel.wait_for_page_to_load("30000")
    
    sel.click("//input[@id='operation_add_to_family[%i]']"%self.test_object_index['Aaron Burr'].key().id())
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_element_present("//input[@id='operation_remove_from_family[%i]']"%self.test_object_index['Aaron Burr'].key().id()))    
      
    sel.click("//input[@id='operation_remove_as_neighbor[%i]']"%self.test_object_index['Benjamin Harrison'].key().id())
    sel.wait_for_page_to_load("30000")
    self.failUnless(not sel.is_text_present("Benjamin Harrison"))    
      
    sel.click("//input[@id='operation_remove_from_family[%i]']"%self.test_object_index['George Wythe'].key().id())
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_element_present("//input[@id='operation_add_to_family[%i]']"%self.test_object_index['George Wythe'].key().id()))    
        
if __name__ == "__main__":
    unittest.main()
