from gui_integration_tests.test_cases import BaseTestCase, TestEnv

from gui_integration_tests.datastore_interface import get_events, delete_event

from selenium import selenium
import unittest

###############################################
####  PRIVACY SETTINGS FOR EVENT ATTENDEES ####
###############################################
class TestPrivacySettingsBase(BaseTestCase):
    
    def _see_all_attendees(self, future = False):
        
        permission_for = ['George Wythe','Elbridge Gerry','Arthur Middleton','Lyman Hall',
                          'William Williams','Matthew Thornton','John Witherspoon'] 

        self.__test_attendees(permission_for = permission_for, 
                              no_permission_for = [], 
                              future = future)
        #TODO: George doesn't want anyone to see where he's been ever...should other event attenders be able to see he attended?
        
    def _see_only_attendees_user_has_permission_for(self, permission_for, no_permission_for,
                                                    future = False):
        self.__test_attendees(permission_for = permission_for, 
                              no_permission_for = no_permission_for, 
                              future = future)
        
    def __test_attendees(self, permission_for, no_permission_for, future):
        
        sel = self.selenium
    
        if future:
            event = 'Four-hundred year Signing reunion'
        else:
            event = 'Sign the Declaration of Independence'
        
        sel.open('/events/%i'%self.test_object_index[event].key().id())
        sel.wait_for_page_to_load("30000")
        
        #always see event creator
        self.failUnless(sel.is_text_present("John Hancock"))    


        
        if sel.is_element_present("//div[@class='pagination_entry']"):
          sel.open('/events/%i/attendees/1' % self.test_object_index[event].key().id())  
          sel.wait_for_page_to_load("30000")
          morepages = True
          pagenum = 1
          while (morepages):
            # people attendee should not be able to see
            for volunteer in no_permission_for:
                self.failIf(sel.is_element_present("//a[@id='volunteer_link[%i]']" % self.test_object_index[volunteer].key().id()))    
  
            # people attendee should be able to see
            # we remove everybody we see from permission_for, and then at the end, permission_for should be empty
            seen = []
            for volunteer in permission_for:
              if (sel.is_element_present("//a[@id='volunteer_link[%i]']" % self.test_object_index[volunteer].key().id())):
                seen.append(self.test_object_index[volunteer].name)
            #remove the ones we have seen from the original list
            for volunteer in seen:
              permission_for.remove(self.test_object_index[volunteer].name)
            
            if (sel.is_element_present("//a[@href='/events/%i/attendees/%i']" % (self.test_object_index[event].key().id(), pagenum+1))): 
              #goto next page
              pagenum = pagenum + 1
              sel.open('/events/%i/attendees/%i' % (self.test_object_index[event].key().id(), pagenum))  
              sel.wait_for_page_to_load("30000")
            else:
              morepages = False
          self.failUnless(len(permission_for) == 0)
        else:
          # people attendee should be able to see
          for volunteer in permission_for:
              self.failUnless(sel.is_element_present("//a[@id='volunteer_link[%i]']"%self.test_object_index[volunteer].key().id()))    
  
          # people attendee should not be able to see
          for volunteer in no_permission_for:
              self.failIf(sel.is_element_present("//a[@id='volunteer_link[%i]']"%self.test_object_index[volunteer].key().id()))    

        
### for event attender Thomas Jefferson
# Jefferson is friends with Geirge Whythe, James Madison
# He follows Benjamin Harrison
# He is an attender of the Signing of the Declaration

class TestPrivacySettings(TestPrivacySettingsBase):
  test_env = TestEnv(
     organization = False,
     create_new_user = False,
     login_email = 'thomas_jefferson@volunteer.org',
     login_name = 'Thomas Jefferson'
     )


  
  ### tests what an event attender can see about who is attending an upcoming event signing of declaration
  def test_event_list_upcoming_attender(self):
      permission = ['George Wythe', 'Thomas McKean', 'Charles Carroll']
      no_permission = ['Elbridge Gerry','Arthur Middleton','Lyman Hall',
                       'William Williams','Matthew Thornton','John Witherspoon'] 

      self._see_only_attendees_user_has_permission_for(
                   permission_for = permission, 
                   no_permission_for = no_permission,
                   future = True)

  ### tests what an event attender can see about who attended a past event signing of declaration
  def test_event_list_past_attender(self):
      self._see_all_attendees()
#      


#### for someone who is not attending the event "signing of declaration"...
class TestPrivacySettings__anyone(TestPrivacySettingsBase):
  test_env = TestEnv(
     organization = False,
     create_new_user = False,
     login_email = 'george_washington@volunteer.org',
     login_name = 'George Washington'
     )

  ### tests what anyone can see about who is attending an upcoming event signing of declaration 
  def test_event_list_upcoming_anyone(self):
      permission = ['Thomas Jefferson', 'Samuel Adams', 'Charles Carroll']
      no_permission = ['Benjamin Harrison']

      self._see_only_attendees_user_has_permission_for(
                   permission_for = permission, 
                   no_permission_for = no_permission,
                   future = True)


  ### tests what anyone can see about who attended a past event
  def test_event_list_past_anyone(self):
      permission = ['Thomas Jefferson', 'Samuel Adams', 'Charles Carroll']
      no_permission = ['Benjamin Harrison']

      self._see_only_attendees_user_has_permission_for(
                   permission_for = permission, 
                   no_permission_for = no_permission,
                   future = False)
     


#### for event creator
class TestPrivacySettings_EventCreator(TestPrivacySettingsBase):
  test_env = TestEnv(
     organization = True,
     create_new_user = False,
     login_email = 'john_hancock@volunteer.org',
     login_name = 'John Hancock'
     )
  
  def test_event_creator_upcoming(self):
    self._see_all_attendees(future = True)

  def test_event_creator_past(self):
    self._see_all_attendees() 
    
###############################################
####  PRIVACY SETTINGS FOR PROFILE PAGES ####
###############################################

## Thomas is friends with George Washington, George Wythe, Thomas McKean
## Thomas is following Benjamin Harrison
## Thomas is followed by Aaron Burr
## George Washington doesn't want anyone to see his events
## Aaron Burr lets anyone see his events
## Thomas doesn't know Arthur Middleton

class TestPrivacySettings_Profile(TestPrivacySettingsBase):
  test_env = TestEnv(
     organization = False,
     create_new_user = False,
     login_email = 'thomas_jefferson@volunteer.org',
     login_name = 'Thomas Jefferson'
     )

  def test_profile_events(self):

      sel = self.selenium
      
      no_permission = ['George Washington', 'Benjamin Harrison', 'Arthur Middleton']
      permission = ['George Wythe', 'Thomas McKean', 'Aaron Burr']

      for volunteer in no_permission:
          sel.open('/volunteers/%i'%self.test_object_index[volunteer].key().id())
          sel.wait_for_page_to_load("30000")

          self.failIf(sel.is_element_present("//div[@id='volunteer_upcoming_events']"))

      for volunteer in permission:
          sel.open('/volunteers/%i'%self.test_object_index[volunteer].key().id())
          sel.wait_for_page_to_load("30000")
          self.failUnless(sel.is_element_present("//div[@id='volunteer_upcoming_events']"))

if __name__ == "__main__":
    unittest.main()
