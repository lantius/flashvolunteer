from gui_integration_tests.test_cases import BaseTestCase, TestEnv

from gui_integration_tests.datastore_interface import get_events, delete_event

from selenium import selenium
import unittest

class TestRecommendedEvents(BaseTestCase):
  test_env = TestEnv(
     organization = False,
     create_new_user = False,
     login_email = 'samuel_adams@volunteer.org',
     login_name = 'Samuel Adams'
     )


  ## TODO: need to check for interest categories successfully being recommended

  def test_recommended_events(self):
    
    sel = self.selenium
    
    sel.click("//a[@id='l_events']")
    sel.wait_for_page_to_load("30000")
    
    neighborhood_events = ['Boston Tea Party Reunion AFTERPARTY!!!']
    interest_events = []
    past_events = ['Boston Tea Party']
    attending_events = ['Boston Tea Party Reunion']
    
    
    self._test_helper(neighborhood_events, interest_events,
                      past_events, attending_events)

    ### unvolunteer from an event in neighborhood
    sel.open("/events/%i"%self.test_object_index['Boston Tea Party Reunion'].key().id())
    sel.wait_for_page_to_load("30000")
    sel.click("//input[@id='s_unvolunteer']")    
    sel.wait_for_page_to_load("30000")
    sel.click("//a[@id='l_events']")
    sel.wait_for_page_to_load("30000")
    
    neighborhood_events = ['Boston Tea Party Reunion AFTERPARTY!!!', 'Boston Tea Party Reunion']
    interest_events = []
    past_events = ['Boston Tea Party']
    attending_events = []

    self._test_helper(neighborhood_events, interest_events,
                      past_events, attending_events)


    ### delete home / work neighborhood
    sel.open("/settings")
    sel.wait_for_page_to_load("30000")
    sel.select("home_neighborhood", "Neighborhood...")
    sel.select("work_neighborhood", "Neighborhood...")
    sel.click("//a[@id='l_events']")
    sel.wait_for_page_to_load("30000")
    
    neighborhood_events = []
    interest_events = []
    past_events = ['Boston Tea Party']
    attending_events = []
 
    self._test_helper(neighborhood_events, interest_events,
                      past_events, attending_events)
    

  
  def _test_helper(self, neighborhood_events, interest_events,
                         past_events, attending_events):

    sel = self.selenium
    ## check if home / work neighborhood triggers recommendation
    for event in neighborhood_events:
        self.failUnless(
            sel.is_element_present("//div[@id='recommendedevents']//a[@id='event_upcoming[%i]']"%self.test_object_index[event].key().id()))    


    ## check if interests triggers recommendation
    for event in interest_events:
        self.failUnless(
            sel.is_element_present("//div[@id='recommendedevents']//a[@id='event_upcoming[%i]']"%self.test_object_index[event].key().id()))    

    ## check if events in past are not recommended
    for event in past_events:
        # TODO: when issue 58: "links to past events still encapsulated in "event_upcoming" id" is resolved,
        #       need to change name to that new tag
        self.failIf(
            sel.is_element_present("//div[@id='recommendedevents']//a[@id='event_upcoming[%i]']"%self.test_object_index[event].key().id()))    
    
    ## check if events you are signed up for are not recommended
    for event in attending_events:
        self.failIf(
            sel.is_element_present("//div[@id='recommendedevents']//a[@id='event_upcoming[%i]']"%self.test_object_index[event].key().id()))    

    



if __name__ == "__main__":
    unittest.main()
