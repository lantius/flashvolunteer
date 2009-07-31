from selenium import selenium
import unittest, time, re

from gui_integration_tests.test_cases import BaseTestCase, TestEnv

from gui_integration_tests.datastore_interface import check_if_user_exists, delete_user

class NewAccount(BaseTestCase):
    name = "volunteer0@test.org"
    
    test_env = TestEnv(
         login_email = None,
         fv_environment = None #do not need to populate
         )
    
    def test_new(self):
        sel = self.selenium
        sel.open("/")
        sel.click("//span[@id='l_create_account']")
        sel.wait_for_page_to_load("30000")
        
        #try with empty name
        sel.type("email", "")
        sel.click("submit-login")
        sel.wait_for_page_to_load("30000")
        self.failUnless(sel.is_element_present("//input[@id='submit-login']"))

        #now the real name
        sel.type("email", self.name)
        sel.click("submit-login")
        sel.wait_for_page_to_load("30000")
        
        #test if TOS is not clicked
        sel.click("//input[@id='s_create_account']")
        sel.wait_for_page_to_load("30000")
        self.failUnless(sel.is_element_present("//strong[@class='error']"))

        #check that TOS page is present
        sel.click("//a[@href='/static/tos']")
        sel.wait_for_page_to_load("30000")
        self.failUnless(sel.is_element_present("//div[@id='TOS']"))

        #back to profile
        sel.click("//a[@id='l_profile']")
        sel.wait_for_page_to_load("30000")

        #now with TOS checked
        sel.click("tosagree")
        sel.click("//input[@id='s_create_account']")
        sel.wait_for_page_to_load("30000")
        self.failUnless(sel.is_text_present("Welcome, %s"%self.name))
        self.assertEqual("Flash Volunteer", sel.get_title())
    
        self.assertTrue(check_if_user_exists(name = self.name))

    def tearDown(self):
        BaseTestCase.tearDown(self)
        delete_user(name=self.name)
        self.assertFalse(check_if_user_exists(name = self.name))

if __name__ == "__main__":
    unittest.main()
