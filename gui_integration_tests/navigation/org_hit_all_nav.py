from selenium import selenium
import unittest, time, re, os
from gui_integration_tests.test_cases import LoginFirst_Organization


class NewTest(LoginFirst_Organization):

    def test_new(self):
        sel = self.selenium
        sel.wait_for_page_to_load("30000")
        sel.click("link=EVENTS")
        sel.wait_for_page_to_load("30000")
        sel.click("link=NEIGHBORHOODS")
        sel.wait_for_page_to_load("30000")
        sel.click("link=FRIENDS")
        sel.wait_for_page_to_load("30000")
        sel.click("link=PROFILE")
        sel.wait_for_page_to_load("30000")
        sel.click("link=HELP")
        sel.wait_for_page_to_load("30000")
        sel.click("link=CREATE EVENT")
    

if __name__ == "__main__":
    unittest.main()
