from gui_integration_tests.test_cases import LoginFirst_Organization

from gui_integration_tests.datastore_interface import get_events, delete_event

from selenium import selenium
import unittest

class CreateEvent(LoginFirst_Organization):

    def test_create_event_basic(self):
        name = 'test event'
        time = '7pm'
        maxattend = '1'
        minattend = '50'
        description = 'my test event'
        instructions = 'please show up'
        neighborhood = 'West Seattle'
        address = 'test center'
        
        
        sel = self.selenium

        sel.wait_for_page_to_load("30000")
        sel.click("link=CREATE EVENT")
        sel.wait_for_page_to_load("30000")
        sel.type("eventname", name)
        sel.click("link=Choose date")
        sel.click("//div[@id='dp-popup']/div[3]/table/tbody/tr[3]/td[3]")
        sel.select("time", "label=%s"%time)
        sel.select("neighborhood", "label=%s"%neighborhood)
        sel.type("address1", address)
        sel.type("maxattend", maxattend)
        sel.type("minattend", minattend)
        sel.type("description", description)
        sel.type("special_instructions", instructions)
        sel.click("//input[@name='interestcategory[5]' and @value='1' and @type='checkbox']")
        sel.click("//input[@name='interestcategory[10]' and @value='1' and @type='checkbox']")
        sel.click("//input[@name='interestcategory[8]' and @value='1' and @type='checkbox']")
        sel.click("//input[@name='interestcategory[6]' and @value='1' and @type='checkbox']")
        sel.click("submit")
        sel.wait_for_page_to_load("30000")
        try: self.failUnless(sel.is_text_present("Event: %s"%name))
        except AssertionError, e: self.verificationErrors.append(str(e))
        try: self.failUnless(sel.is_text_present("Neighborhood: %s"%neighborhood))
        except AssertionError, e: self.verificationErrors.append(str(e))
        try: self.failUnless(sel.is_text_present("Date: Wednesday, 13 May 2009"))
        except AssertionError, e: self.verificationErrors.append(str(e))
        
        events = [e for e in get_events(name = name)]
        try: self.assertTrue(len(events) == 1)
        except AssertionError, e: self.verificationErrors.append(str(e))
        
        e = events[0]
        
        try: self.assertEqual(e.name, name)
        except AssertionError, e: self.verificationErrors.append(str(e))
        
        try: self.assertEqual(e.description, description)
        except AssertionError, e: self.verificationErrors.append(str(e))
        
        try: self.assertEqual(e.special_instructions, instructions)
        except AssertionError, e: self.verificationErrors.append(str(e))
        
        try: self.assertEqual(e.address, address)
        except AssertionError, e: self.verificationErrors.append(str(e))
        
        delete_event(name = name)
        
if __name__ == "__main__":
    unittest.main()
