from gui_integration_tests.test_cases import BaseTestCase, TestEnv
from gui_integration_tests.datastore_interface import get_events, delete_event, get_users, \
            get_eventvolunteers, delete_eventvolunteer
from models.eventvolunteer import *

from selenium import selenium
import unittest

class VerifyAttendanceTestCase(BaseTestCase):
  test_env = TestEnv(
     organization = False,
     create_new_user = False,
     login_email = 'john_hancock@volunteer.org',
     login_name = 'John Hancock'
     )
  event_name = 'Sign the Declaration of Independence'

  def setUp(self):
    "unittest override"
    BaseTestCase.setUp(self)
    
  def test_verify_attendance(self):
    "click through past event page as owner, picking who has attended"
    sel = self.selenium
    events = [ee for ee in get_events(name = self.event_name)] 
    event = events[0]
    
    sel.open("/events/" + str(event.key().id()))
    sel.wait_for_page_to_load("30000")  
    
    events = get_events(self.event_name)

    volunteers_name = ("Samuel Adams", "Thomas Jefferson", "John Adams", "John Hancock")
    volunteers_email = ("samuel_adams@volunteer.org", "thomas_jefferson@volunteer.org", "john_adams@volunteer.org", "john_hancock@volunteer.org")
    volunteers = []
    volunteers_env = []
    eventvolunteers = []
    
    #attended
    volunteers.append(get_users(volunteers_name[0]))
    eventvolunteers.append(get_eventvolunteers(volunteer = volunteers[-1][0], event = events[0]))
    ev = [e for e in eventvolunteers[-1]]
    el0_true = "i_verify_" + str(ev[0].key().id()) + "_true"
    self.failUnless(sel.is_element_present("//input[@id='%s']" % el0_true))  
    sel.click(el0_true)

    #did not attend
    volunteers.append(get_users(volunteers_name[1]))
    eventvolunteers.append(get_eventvolunteers(volunteer = volunteers[-1][0], event = events[0]))
    ev = [e for e in eventvolunteers[-1]]
    el1_false = "i_verify_" + str(ev[0].key().id()) + "_false"
    self.failUnless(sel.is_element_present("//input[@id='%s']" % el1_false))  
    sel.click(el1_false)

    #don't know
    volunteers.append(get_users(volunteers_name[2]))
    eventvolunteers.append(get_eventvolunteers(volunteer = volunteers[-1][0], event = events[0]))
    ev = [e for e in eventvolunteers[-1]]
    el2_unknown = "i_verify_" + str(ev[0].key().id()) + "_unknown"
    self.failUnless(sel.is_element_present("//input[@id='%s']" % el2_unknown))  
    sel.click(el2_unknown)

    #attended for 2 hours
    volunteers.append(get_users(volunteers_name[3]))
    eventvolunteers.append(get_eventvolunteers(volunteer = volunteers[-1][0], event = events[0]))
    ev = [e for e in eventvolunteers[-1]]
    el3_true = "i_verify_" + str(ev[0].key().id()) + "_true"
    self.failUnless(sel.is_element_present("//input[@id='%s']" % el3_true))  
    sel.click(el3_true)
    el3_text = "i_verify_" + str(ev[0].key().id()) + "_text"
    my_hour = "2"
    sel.type("//input[@id='%s']" % el3_text, my_hour)
    
    sel.click("//input[@id='s_verify']")  #reloads page
    sel.wait_for_page_to_load("30000")  
    
    #check that all checkboxes are set the way we set them above
    self.failUnless(sel.is_checked(el0_true))
    self.failUnless(sel.is_checked(el1_false))
    self.failUnless(sel.is_checked(el2_unknown))
    self.failUnless(sel.is_checked(el3_true))
    #attribute value = my_hour
    self.assertEqual(sel.get_attribute(el3_text + "@value"), my_hour)
    
    #check against database
    ev = [e for e in eventvolunteers[0]]
    self.assertEqual(ev[0].attended, True)
    ev = [e for e in eventvolunteers[1]]
    self.assertEqual(ev[0].attended, False)
    ev = [e for e in eventvolunteers[2]]
    self.assertEqual(ev[0].attended, None)
    ev = [e for e in eventvolunteers[3]]
    self.assertEqual(ev[0].attended, True)
    self.assertEqual(ev[0].hours, int(my_hour))
    
    #get receipt for self = volunteers[3]
    sel.open("/events/" + str(event.key().id()) + "/verify")
    sel.wait_for_page_to_load("30000")  
    self.failUnless(sel.is_text_present(self.test_env.login_name))
    self.failUnless(sel.is_text_present(my_hour))
    
    #login as volunteers[0]
    self.logout()
    volunteers_env.append(TestEnv(login_email = volunteers_email[0]))
    self.login_as_existing_user(volunteers_env[-1])
    sel.open("/events/" + str(event.key().id()) + "/verify")
    sel.wait_for_page_to_load("30000")  
    self.failUnless(sel.is_text_present(self.test_env.login_name))
    self.failUnless(sel.is_text_present(volunteers_name[0]))
    self.failUnless(sel.is_text_present(self.event_name))
    self.failUnless(sel.is_text_present(self.event_name))
    
    #login as volunteers[1]
    self.logout()
    volunteers_env.append(TestEnv(login_email = volunteers_email[1]))
    self.login_as_existing_user(volunteers_env[-1])
    sel.open("/events/" + str(event.key().id()) + "/verify")
    sel.wait_for_page_to_load("30000")  
    self.failUnless(sel.is_text_present(self.test_env.login_name))
    self.failIf(sel.is_text_present(self.event_name))
    
    #login as volunteers[2]
    self.logout()
    volunteers_env.append(TestEnv(login_email = volunteers_email[2]))
    self.login_as_existing_user(volunteers_env[-1])
    sel.open("/events/" + str(event.key().id()) + "/verify")
    sel.wait_for_page_to_load("30000")  
    self.failUnless(sel.is_text_present(self.test_env.login_name))
    self.failIf(sel.is_text_present(self.event_name))
    
  def tearDown(self):
    "unittest override"
    sel = self.selenium
    BaseTestCase.tearDown(self)
    
if __name__ == "__main__":
    unittest.main()
