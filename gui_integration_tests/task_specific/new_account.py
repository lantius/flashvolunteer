from selenium import selenium
import unittest, time, re

from gui_integration_tests.test_cases import BaseTestCase

from gui_integration_tests.datastore_interface import check_if_user_exists, delete_user

class NewAccount(BaseTestCase):
    name = "volunteer0@test.org"
    def test_new(self):
        sel = self.selenium
        sel.open("/")
        sel.click("//div[@id='buttons']/a[2]/span[2]")
        sel.wait_for_page_to_load("30000")
        sel.type("email", self.name)
        sel.click("submit-login")
        sel.wait_for_page_to_load("30000")
        sel.click("tosagree")
        sel.click("//input[@value='Create my account']")
        sel.wait_for_page_to_load("30000")
        try: self.failUnless(sel.is_text_present("Welcome, %s"%self.name))
        except AssertionError, e: self.verificationErrors.append(str(e))
        self.assertEqual("Flash Volunteer", sel.get_title())
    
        self.assertTrue(check_if_user_exists(name = self.name))

    def tearDown(self):
        BaseTestCase.tearDown(self)
        delete_user(name=self.name)
        self.assertFalse(check_if_user_exists(name = self.name))

if __name__ == "__main__":
    unittest.main()