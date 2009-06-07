from gui_integration_tests.test_cases import BaseTestCase, TestEnv

from gui_integration_tests.datastore_interface import get_events, delete_event

from selenium import selenium
import unittest


def navigate_to_event(sel, test_object_index, future):
    if future:
        event = 'Four-hundred year Signing reunion'
    else:
        event = 'Sign the Declaration of Independence'
    
    sel.open('/events/%i'%test_object_index[event].key().id())
    sel.wait_for_page_to_load("30000")

class TestEditEvent__Owner(BaseTestCase):
    test_env = TestEnv(
     organization = False,
     create_new_user = False,
     login_email = 'john_hancock@volunteer.org',
     login_name = 'John Hancock'
     )
        
    ### TODO: what should be the proper behavior here? (Issue 57)
#    def test_edit_past_event(self):
#        pass
        
    
    def test_edit_upcoming_event(self):
        sel = self.selenium
        
        navigate_to_event(sel = sel, 
                          future = True,
                          test_object_index = self.test_object_index)
        
        desc = "Come celebrate the signing of the declaration with the rest of the zombie founders! Party like its 1776 again!"
        special_instr = "Don't forget that feather in your cap."
        
        sel.click("//input[@id='s_edit_event']")
        sel.wait_for_page_to_load("30000")

        sel.type("eventduration", "16")
        sel.select("time", "label=7am")
        sel.type("address1", "Convention center")
        sel.type("maxattend", "45")
        sel.type("minattend", "50")
        sel.type("description", desc)
        sel.type("special_instructions", special_instr)
        #sel.click("//input[@name='interestcategory[267]' and @value='1' and @type='checkbox']")
        sel.click("submit")
        sel.wait_for_page_to_load("30000")
        
        self.failUnless(sel.is_text_present("exact:Duration: 16 hours"))
        self.failUnless(sel.is_text_present("exact:Address: Convention center"))
        self.failUnless(sel.is_text_present(desc))
        self.failUnless(sel.is_text_present(special_instr))    

class TestEditEvent__NonOwner(BaseTestCase):
    test_env = TestEnv(
     organization = False,
     create_new_user = False,
     login_email = 'george_washington@volunteer.org',
     login_name = 'George Washington'
     )
        
    ### TODO: what should be the proper behavior here? (Issue 57)
#    def test_edit_past_event(self):
#        pass
    
    def test_edit_upcoming_event(self):
        sel = self.selenium
        
        navigate_to_event(sel = sel, 
                          future = True,
                          test_object_index = self.test_object_index)
        
        self.failIf(sel.is_element_present("//input[@id='s_edit_event']"))
        self.failIf(sel.is_element_present("//input[@id='s_cancel_event']"))

    
if __name__ == "__main__":
    unittest.main()
