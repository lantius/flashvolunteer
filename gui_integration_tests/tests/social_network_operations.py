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

    
  # TODO: re-enable. This broke with pagination
  def update_me_test_social_network_basic(self):
    
    sel = self.selenium
    
    sel.click("//a[@id='l_friends']")
    sel.wait_for_page_to_load("30000")
    
    friends = ["George Wythe", "James Madison", "George Washington", "Thomas McKean"]
    following = ["Benjamin Harrison"] #Mixed in with the friends on the page
    followers = ["Aaron Burr"]

    self.failUnless(sel.is_element_present("//div[@id='friends_and_followers']"))

    for friend in friends:
        self.failUnless(sel.is_element_present("//div[@id='friends_and_followers']//a[@id='volunteer_link[%i]']"%self.test_object_index[friend].key().id()))    
    
    for friend in following:
        self.failUnless(sel.is_element_present("//div[@id='friends_and_followers']//a[@id='volunteer_link[%i]']"%self.test_object_index[friend].key().id()))    
    
    for friend in followers:
        self.failUnless(sel.is_element_present("//div[@id='followers']//a[@id='volunteer_link[%i]']"%self.test_object_index[friend].key().id()))    

    
    sel.click("//input[@id='operation_add_to_team[%i]']"%self.test_object_index['Aaron Burr'].key().id())
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_element_present("//div[@id='friends_and_following']//a[@id='volunteer_link[%i]']"%self.test_object_index['Aaron Burr'].key().id()))    
    self.failUnless(sel.is_element_present("//input[@id='operation_remove_from_team[%i]']"%self.test_object_index['Aaron Burr'].key().id()))    
      
      
    sel.click("//input[@id='operation_remove_from_team[%i]']"%self.test_object_index['Benjamin Harrison'].key().id())
    sel.wait_for_page_to_load("30000")
    self.failIf(sel.is_element_present("//div[@class='volunteer_summary_following']//a[@id='volunteer_link[%i]']"%self.test_object_index["Benjamin Harrison"].key().id()))    
    self.failIf(sel.is_text_present("Benjamin Harrison"))    
    

    sel.click("//input[@id='operation_remove_from_team[%i]']"%self.test_object_index['George Wythe'].key().id())
    sel.wait_for_page_to_load("30000")
    self.failUnless(sel.is_element_present("//div[@class='followers']//a[@id='volunteer_link[%i]']"%self.test_object_index['George Wythe'].key().id()))    
    self.failUnless(sel.is_element_present("//input[@id='operation_add_to_team[%i]']"%self.test_object_index['George Wythe'].key().id()))    
    
    sel.open('/volunteers/%i'%self.test_object_index['Benjamin Harrison'].key().id())
    sel.wait_for_page_to_load('30000')
    self.failUnless(sel.is_element_present("//input[@id='operation_add_to_team[%i]']"%self.test_object_index['Benjamin Harrison'].key().id()))    
    sel.click("//input[@id='operation_add_to_team[%i]']"%self.test_object_index['Benjamin Harrison'].key().id())
    sel.wait_for_page_to_load('30000')
    self.failUnless(sel.is_element_present("//input[@id='operation_remove_from_team[%i]']"%self.test_object_index['Benjamin Harrison'].key().id()))    
    sel.open('/team')
    sel.wait_for_page_to_load('30000')
    self.failUnless(sel.is_element_present("//div[@class='friends_and_following']//a[@id='volunteer_link[%i]']"%self.test_object_index['Benjamin Harrison'].key().id()))    

    sel.open('/volunteers/%i'%self.test_object_index['James Madison'].key().id())
    sel.wait_for_page_to_load('30000')
    self.failUnless(sel.is_element_present("//input[@id='operation_remove_from_team[%i]']"%self.test_object_index['James Madison'].key().id()))    
    sel.click("//input[@id='operation_remove_from_team[%i]']"%self.test_object_index['James Madison'].key().id())
    sel.wait_for_page_to_load('30000')
    self.failUnless(sel.is_element_present("//input[@id='operation_add_to_team[%i]']"%self.test_object_index['James Madison'].key().id()))    
    sel.open('/team')
    sel.wait_for_page_to_load('30000')
    self.failUnless(sel.is_element_present("//div[@class='followers']//a[@id='volunteer_link[%i]']"%self.test_object_index['James Madison'].key().id()))    



if __name__ == "__main__":
    unittest.main()
