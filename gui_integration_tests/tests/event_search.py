from gui_integration_tests.test_cases import BaseTestCase, TestEnv

from gui_integration_tests.datastore_interface import get_events, delete_event

from selenium import selenium
import unittest


class TestEventSearch(BaseTestCase):
    test_env = TestEnv(
     organization = False,
     create_new_user = False,
     login_email = 'thomas_jefferson@volunteer.org',
     login_name = 'Thomas Jefferson'
     )

        
    past = {
            'Maine': ['Penobscot Expedition'],
            'Pennsylvania': ['Sign the Declaration of Independence'],
            'Massachusetts': ['Battle of Bunker Hill',
                              'Battle of Lexington and Concord',
                              'Boston Tea Party'
                              ],
            'Rhode Island': ['Gaspee Affair']

    }
            
    future = {
            'Maine': ['Penobscot Expedition'],
            'Pennsylvania': ['Four-hundred year Signing reunion'],
            'Massachusetts': ['Battle of Bunker Hill Reunion',
                              'Battle of Lexington and Concord Reunion',
                              'Boston Tea Party Reunion'
                              ]
    }


    def test_search_all(self):
        sel = self.selenium
        sel.open('/events')
        sel.wait_for_page_to_load("30000")
        
        sel.select("neighborhood", "label=Neighborhood...")

        sel.click("//input[@id='s_events_wide_search']")
        
        sel.wait_for_page_to_load("30000")
        
        for k,v in self.past.items():
            for event in v:
                self.failUnless(sel.is_element_present("//a[@id='event_upcoming[%i]']"%self.test_object_index[event].key().id()))    

        for k,v in self.future.items():
            for event in v:
                self.failUnless(sel.is_element_present("//a[@id='event_upcoming[%i]']"%self.test_object_index[event].key().id()))    
    
    def test_search_neighborhood(self):
        sel = self.selenium
        sel.open('/events')
        sel.wait_for_page_to_load("30000")
        
        sel.select("neighborhood", "label=Massachusetts")

        sel.click("//input[@id='s_events_wide_search']")
        
        sel.wait_for_page_to_load("30000")
        
        for event in self.past['Massachusetts']:
            self.failUnless(sel.is_element_present("//a[@id='event_upcoming[%i]']"%self.test_object_index[event].key().id()))    

        for event in self.future['Massachusetts']:
            self.failUnless(sel.is_element_present("//a[@id='event_upcoming[%i]']"%self.test_object_index[event].key().id()))    
        
    #TODO: tests for date limit
if __name__ == "__main__":
    unittest.main()
