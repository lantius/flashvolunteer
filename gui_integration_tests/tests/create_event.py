from gui_integration_tests.test_cases import BaseTestCase, TestEnv

from gui_integration_tests.datastore_interface import get_events, delete_event

from selenium import selenium
import unittest

class CreateEvent(BaseTestCase):
  test_env = TestEnv(
     organization = True,
     create_new_user = False,
     login_email = 'john_hancock@volunteer.org',
     login_name = 'John Hancock'
     )
  
  event_name = 'test event'
  time = '7pm'
  maxattend = '1'
  minattend = '50'
  description = 'my test event'
  duration = '2'
  instructions = 'please show up'
  neighborhood = 'West Seattle'
  address = 'Seattle'

  interest_categories = ['Animals', 'Hunger', 'Senior Citizens']
  
  def create_event_basic(self):
    
    sel = self.selenium

    delete_event(name = self.event_name)
    
    sel.wait_for_page_to_load("30000")
    sel.click("//a[@id='l_create_event']")
    sel.wait_for_page_to_load("30000")
    sel.type("eventname", self.event_name)
    #sel.click("link=Choose date")
    #sel.click("//div[@id='dp-popup']/div[3]/table/tbody/tr[3]/td[3]")
    sel.type("eventdate", '05/13/2019')
    
    sel.select("time", "label=%s"%self.time)
    sel.select("neighborhood", "label=%s"%self.neighborhood)
    sel.type("eventduration", self.duration)
    sel.type("address1", self.address)
    #Removed from the UI
    #sel.type("maxattend", self.maxattend)
    #sel.type("minattend", self.minattend)
    sel.type("description", self.description)
    sel.type("special_instructions", self.instructions)
    
    for interest in self.interest_categories:
        self._click_interestcategory(name = interest, checked = True)
        
    sel.click("submit")
    

  def test_create_event_errors(self):
    #test that proper error messages are shown when missing information
    
    sel = self.selenium
    
    events = [e for e in get_events(name = self.event_name)]
    try:
        self.assertTrue(len(events) == 0) #Make sure we there aren't any events already created.
    except:
        delete_event(name = self.event_name)
        
    sel.open("/events/new")
    sel.wait_for_page_to_load("30000")  
    #leave everything blank
    #misselect neighborhoods
    sel.select("neighborhood", "label=Neighborhood...")

    sel.click("submit")
    sel.wait_for_page_to_load("30000")
    
    try:
      #XPath: look for <strong class='error'/> after <div class='eventinput'/> with sibling <input id='eventname'/>
      self.failUnless(sel.is_element_present("//div[@class='eventinput'][input[@id='eventname']]/strong[@class='error']"))
      self.failUnless(sel.is_element_present("//div[@class='eventinput'][input[@id='eventdate']]/strong[@class='error']"))
      self.failUnless(sel.is_element_present("//div[@class='eventinput'][input[@id='eventduration']]/strong[@class='error']"))
      self.failUnless(sel.is_element_present("//div[@class='eventinput'][select[@name='neighborhood']]/strong[@class='error']"))
      self.failUnless(sel.is_element_present("//div[@class='eventinput'][textarea[@name='description']]/strong[@class='error']"))
    finally:
      delete_event(name = self.event_name)

        
  def test_create_event_basic(self):
    
    sel = self.selenium
    
    events = [e for e in get_events(name = self.event_name)]
    try:
        self.assertTrue(len(events) == 0) #Make sure we there aren't any events already created.
    except:
        delete_event(name = self.event_name)
        
    self.create_event_basic()
    sel.wait_for_page_to_load("30000")
    try:
      self.failUnless(sel.is_text_present("Event: %s"%self.event_name))
      self.failUnless(sel.is_text_present("Neighborhood: %s"%self.neighborhood))
      self.failUnless(sel.is_text_present("Date: Monday, 13 May 2019"))
    
      events = [e for e in get_events(name = self.event_name)]
      self.assertTrue(len(events) == 1) #Make sure we only created one event
    
      e = events[0]
    
      self.assertEqual(e.name, self.event_name)
      self.assertEqual(e.description, self.description)
      self.assertEqual(e.special_instructions, self.instructions)
      self.assertEqual(e.address, self.address)
    
      #TODO: when interest categories show up on event pages (Issue 60), add this in...
#      for interest in self.interest_categories:
#          self._verify_interestcategory(name = interest, checked = True)  
    finally:
      delete_event(name = self.event_name)
  
  def test_delete_event_basic(self):

    sel = self.selenium

    events = [e for e in get_events(name = self.event_name)]
    self.assertTrue(len(events) == 0)

    self.create_event_basic()
    sel.wait_for_page_to_load("30000")
    try:
      events = [e for e in get_events(name = self.event_name)]
      self.assertTrue(len(events) == 1)
            
      e = events[0]
    
      id = e.key().id()
      sel.open("/events") #TODO WHY DOES THIS BREAK EVERYTHING!?!
      sel.wait_for_page_to_load("30000")
      #l_event_1175
      sel.click("//a[@id='event_upcoming[%i]']"%id)
      sel.wait_for_page_to_load("30000")
      sel.click("//input[@id='s_cancel_event']")
      sel.wait_for_page_to_load("30000")

      self.failIf(sel.is_text_present("Event: %s"%self.event_name))
    
      events = [e for e in get_events(name = self.event_name)]
      self.assertTrue(len(events) == 0)
    finally:
      delete_event(name = self.event_name)
      
    
if __name__ == "__main__":
    unittest.main()
