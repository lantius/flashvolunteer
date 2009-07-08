from gui_integration_tests.test_cases import BaseTestCase, TestEnv
from gui_integration_tests.datastore_interface import get_events, delete_event, get_users, \
            get_eventvolunteers, delete_eventvolunteer
from models.eventvolunteer import *

from selenium import selenium
import unittest

class VolunteerForEventTestCase(BaseTestCase):
  test_env = TestEnv(
     organization = False,
     create_new_user = False,
     login_email = 'john_hancock@volunteer.org',
     login_name = 'John Hancock'
     )
  event_name = 'Penobscot Expedition Reunion'

  def setUp(self):
    "unittest override"
    BaseTestCase.setUp(self)
    

  def ui_volunteer_for_event(self, sel):
    "volunteer for event by clicking through website"
    #make sure we are not already signed up
    delete_eventvolunteer(volunteer = self.test_env.login_name, 
                          event = self.event_name)
    
    sel.open("/events")
    sel.click("l_events")
    sel.wait_for_page_to_load("30000")
    sel.select("neighborhood", "label=Neighborhood...")
    sel.click("//input[@value='submit']")
    sel.wait_for_page_to_load("30000")  
    
    events = [ee for ee in get_events(name = self.event_name)] 
    ee = events[0]
    id = str(ee.key().id())
    sel.click("//a[@id='event_upcoming[" + id + "]']")
    sel.wait_for_page_to_load("30000")
    sel.click("//input[@id='s_volunteer']") #volunteer button
    sel.wait_for_page_to_load("30000")  
  
    
  def test01_volunteer_for_event(self):
    """volunteer for event, and check if successful, 
    called automatically by unittest"""
    sel = self.selenium
    self.ui_volunteer_for_event(sel)
    
    volunteers = get_users(self.test_env.login_name)
    events = get_events(self.event_name)
    eventvolunteers = get_eventvolunteers(volunteer = volunteers[0], event = events[0])
    ev = [e for e in eventvolunteers]
    try:
      self.assertTrue(len(ev) == 1) #Make sure we are only signed up once
      self.assertEqual(ev[0].event.name, self.event_name)
      self.assertEqual(ev[0].volunteer.name, self.test_env.login_name)

      self.failUnless(sel.is_text_present(self.event_name))
      self.failUnless(sel.is_element_present("//input[@id='s_unvolunteer']"))  
       
      sel.click("l_home")
      sel.wait_for_page_to_load("30000")
      #should show up on home page for volunteer
      self.failUnless(sel.is_text_present(self.event_name))
    finally:
      ev[0].delete()  #delete the eventvolunteer 
      
      
  def ui_unvolunteer_for_event(self, sel):
    "unvolunteer for event by clicking through website"
    sel.open("/")
    events = [ee for ee in get_events(name = self.event_name)] 
    ee = events[0]
    id = str(ee.key().id())
    sel.click("//a[@id='event_upcoming[" + id + "]']")
    sel.wait_for_page_to_load("30000")
    sel.click("//input[@id='s_unvolunteer']") #unvolunteer button
    sel.wait_for_page_to_load("30000")  

  
  def db_volunteer_for_event(self):
    "volunteer for event by creating database objects directly"
    volunteers = get_users(self.test_env.login_name)
    events = get_events(self.event_name)
    eventvolunteer = EventVolunteer(volunteer=volunteers[0], event=events[0], isowner=False)
    eventvolunteer.put()
  
  def test02_unvolunteer_for_event(self):
    """get out of event, and check if successful, 
    called automatically by unittest"""
    sel = self.selenium
    self.db_volunteer_for_event()
    self.ui_unvolunteer_for_event(sel)

    try:
      volunteers = get_users(self.test_env.login_name)
      events = get_events(self.event_name)
      eventvolunteers = get_eventvolunteers(volunteer = volunteers[0], event = events[0])
      ev = [e for e in eventvolunteers]
      self.assertTrue(len(ev) == 0) #Make sure we are not signed up any longer

      self.failUnless(sel.is_text_present(self.event_name))   #event name somewhere on page
      self.failUnless(sel.is_element_present("//input[@id='s_volunteer']"))  #volunteer button available
       
      sel.click("l_home")
      sel.wait_for_page_to_load("30000")
      #event should not show up on home page for volunteer any longer
      self.failIf(sel.is_text_present(self.event_name))
    finally:
      if len(ev) > 0:
        ev[0].delete()
    
  def tearDown(self):
    "unittest override"
    sel = self.selenium
    BaseTestCase.tearDown(self)
    
if __name__ == "__main__":
    unittest.main()
