from gui_integration_tests.test_cases import BaseTestCase, TestEnv

from gui_integration_tests.datastore_interface import get_events, delete_event

from selenium import selenium
import unittest

  ###TODO: different people should have different privacy settings, not all set to "friends" 
  ###TODO: tests for viewing someone else's profile
  ###TODO: tests for upcoming event
  
class TestPrivacySettingsBase(BaseTestCase):
    
    def _see_all_attendees(self):
        sel = self.selenium
    
        sel.click("//a[@id='l_events']")
        sel.wait_for_page_to_load("30000")
    
        sel.click("//a[@id='event_past[%i]']"%self.test_object_index['Sign the Declaration of Independence'].key().id())
        sel.wait_for_page_to_load("30000")
        
        self.failUnless(sel.is_text_present("John Hancock"))    
        self.failUnless(sel.is_element_present("//a[@id='volunteer_link[%i]']"%self.test_object_index['George Wythe'].key().id()))  
        self.failUnless(sel.is_element_present("//a[@id='volunteer_link[%i]']"%self.test_object_index['Elbridge Gerry'].key().id()))
        self.failUnless(sel.is_element_present("//a[@id='volunteer_link[%i]']"%self.test_object_index['Arthur Middleton'].key().id()))    
        self.failUnless(sel.is_element_present("//a[@id='volunteer_link[%i]']"%self.test_object_index['Lyman Hall'].key().id()))    
        self.failUnless(sel.is_element_present("//a[@id='volunteer_link[%i]']"%self.test_object_index['William Williams'].key().id()))    
        self.failUnless(sel.is_element_present("//a[@id='volunteer_link[%i]']"%self.test_object_index['Matthew Thornton'].key().id()))          
        self.failUnless(sel.is_element_present("//a[@id='volunteer_link[%i]']"%self.test_object_index['John Witherspoon'].key().id()))  

    def _see_only_attendees_user_has_permission_for(self):
        sel = self.selenium
    
        sel.click("//a[@id='l_events']")
        sel.wait_for_page_to_load("30000")
    
        sel.click("//a[@id='event_past[%i]']"%self.test_object_index['Sign the Declaration of Independence'].key().id())
        sel.wait_for_page_to_load("30000")
        
        self.failUnless(sel.is_element_present("//a[@id='volunteer_link[%i]']"%self.test_object_index['George Wythe'].key().id()))    
        self.failUnless(sel.is_text_present("John Hancock"))    
        self.failUnless(not sel.is_element_present("//a[@id='volunteer_link[%i]']"%self.test_object_index['John Hart'].key().id()))    

### for event attender
class TestPrivacySettings(TestPrivacySettingsBase):
  test_env = TestEnv(
     organization = False,
     create_new_user = False,
     login_email = 'thomas_jefferson@volunteer.org',
     login_name = 'Thomas Jefferson'
     )


  
  ### tests what an event attender can see about who is attending an upcoming event signing of declaration
#  def test_event_list_upcoming_attender(self):
#      self._see_only_attendees_user_has_permission_for()

  ### tests what an event attender can see about who attended a past event signing of declaration
  def test_event_list_past_attender(self):
      self._see_all_attendees()
      


#### for someone who is not attending the event signing of declaration...
class TestPrivacySettings__anyone(TestPrivacySettingsBase):
  test_env = TestEnv(
     organization = False,
     create_new_user = True,
     login_email = 'test@example.com',
     )

  ### tests what anyone can see about who is attending an upcoming event signing of declaration 
#  def test_event_list_upcoming_anyone(self):
#      self._see_only_attendees_user_has_permission_for()


  ### tests what anyone can see about who attended a past event
  def test_event_list_past_anyone(self):
      self._see_only_attendees_user_has_permission_for()      


### for event creator
class TestPrivacySettings_EventCreator(TestPrivacySettingsBase):
  test_env = TestEnv(
     organization = True,
     create_new_user = False,
     login_email = 'john_hancock@volunteer.org',
     login_name = 'John Hancock'
     )
  
#  def test_event_creator_upcoming(self):
#    self._see_all_attendees()

  def test_event_creator_past(self):
    self._see_all_attendees() 
    
if __name__ == "__main__":
    unittest.main()
