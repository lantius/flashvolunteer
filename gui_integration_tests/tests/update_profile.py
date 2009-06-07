from gui_integration_tests.test_cases import BaseTestCase, TestEnv
from gui_integration_tests.datastore_interface import delete_user

from selenium import selenium
import unittest

class UpdateProfileTest(BaseTestCase):
    test_env = TestEnv()

    def test_new(self):
        
        sel = self.selenium
        sel.wait_for_page_to_load("30000")
        sel.click("//a[@id='l_profile']")
        sel.wait_for_page_to_load("30000")
        sel.type("quote", "selenium has arrived!")
        sel.click("//input[@id='s_update_profile']")
        sel.wait_for_page_to_load("30000")
        sel.click("//a[@id='l_home']")
        #sel.click("//a[@id='link_home']")
        sel.wait_for_page_to_load("30000")
        self.failUnless(sel.is_text_present("selenium has arrived!"))
        self.failUnless(sel.is_text_present(self.test_env.login_email))
        sel.click("//a[@id='l_profile']")
        sel.wait_for_page_to_load("30000")
        try:
            sel.type("name", "selenium test")
            sel.type('email', 'mypreferredemail@testtest.com')
            sel.click("//input[@id='s_update_profile']")
            
            sel.wait_for_page_to_load("30000")
            self.failUnless(sel.is_text_present("Welcome, selenium test"))
            self.assertEqual('mypreferredemail@testtest.com', sel.get_value("email"))
            
            sel.click("//a[@id='l_home']")
            
            self.failUnless(sel.is_text_present("selenium test"))
            self.failUnless(sel.is_text_present("Capitol Hill"))
    
            sel.click("//a[@id='l_profile']")
            sel.wait_for_page_to_load("30000")
            sel.select("home_neighborhood", "label=West Seattle")
            sel.select("work_neighborhood", "label=University District")
            sel.click("//input[@id='s_update_profile']")
            sel.wait_for_page_to_load("30000")
            
            sel.click("//a[@id='l_home']")
            sel.wait_for_page_to_load("30000")
            
            self.failUnless(sel.is_text_present("West Seattle"))
            self.failUnless(sel.is_text_present("University District"))
                        
            sel.click("//a[@id='l_profile']")
            sel.wait_for_page_to_load("30000")

            self.assertEqual('mypreferredemail@testtest.com', sel.get_value("email"))
            
            interests = ['Animals', 'Hunger', 'Senior Citizens']
            for interest in interests:
                self._click_interestcategory(name = interest, checked = True)
            
            sel.click("//input[@id='s_update_profile']")

            for interest in interests:
                self._verify_interestcategory(name = interest, checked = True)   
                             
        finally:
            
            delete_user(name = 'selenium test')
            
if __name__ == "__main__":
    unittest.main()

