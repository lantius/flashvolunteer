from gui_integration_tests.test_cases import LoginFirst_Volunteer

from selenium import selenium
import unittest

class NewTest(LoginFirst_Volunteer):
    
    def test_new(self):
        sel = self.selenium
        sel.wait_for_page_to_load("30000")
        sel.click("//a[@id='l_events']")
        sel.wait_for_page_to_load("30000")
        sel.click("//a[@id='l_neighborhoods']")
        sel.wait_for_page_to_load("30000")
        sel.click("//a[@id='l_friends']")
        sel.wait_for_page_to_load("30000")
        sel.click("//a[@id='l_profile']")
        sel.wait_for_page_to_load("30000")
        sel.click("//a[@id='l_help']")

if __name__ == "__main__":
    unittest.main()
