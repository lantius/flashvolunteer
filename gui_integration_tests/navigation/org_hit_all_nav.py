from selenium import selenium
import unittest, time, re, os
from gui_integration_tests.test_cases import LoginFirst_Organization


class NewTest(LoginFirst_Organization):


  def test_new(self):
    sel = self.selenium
    sel.wait_for_page_to_load("30000")
    sel.click("//a[@id='l_events']") # This takes you back to the profile page
    sel.wait_for_page_to_load("30000")
    sel.click("//a[@id='l_neighborhoods']")
    sel.wait_for_page_to_load("30000")
    sel.click("//a[@id='l_friends']")
    sel.wait_for_page_to_load("30000")
    sel.click("//a[@id='l_help']")
    sel.wait_for_page_to_load("30000")
    sel.click("//a[@id='l_profile']") # Go to the profile page last
    sel.wait_for_page_to_load("30000")
    # No Create Event link for a new user. Need permissions to create.
    # No Log Out link before you've logged in. Except on the create account/settings page.    

if __name__ == "__main__":
    unittest.main()
