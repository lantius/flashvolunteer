from gui_integration_tests.test_cases import BaseTestCase, TestEnv

from gui_integration_tests.datastore_interface import check_if_user_exists

from selenium import selenium
import unittest

class DeleteAccount(BaseTestCase):
    test_env = TestEnv(create_new_user = True)
    
    def test_new(self):    
        sel = self.selenium
        sel.wait_for_page_to_load("30000")
        sel.click("//a[@id='l_profile']")
        sel.wait_for_page_to_load("30000")
        sel.click("//input[@id='s_delete_account']")
        sel.wait_for_page_to_load("30000")
        
        self.assertFalse(check_if_user_exists(name = self.test_env.login_name))
        
if __name__ == "__main__":
    unittest.main()