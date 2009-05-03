from gui_integration_tests.test_cases import LoginFirst_Volunteer

from gui_integration_tests.datastore_interface import check_if_user_exists

from selenium import selenium
import unittest

class DeleteAccount(LoginFirst_Volunteer):

    def test_new(self):
        sel = self.selenium
        sel.wait_for_page_to_load("30000")
        sel.click("link=PROFILE")
        sel.wait_for_page_to_load("30000")
        sel.click("//input[@value='Delete your account']")
        sel.wait_for_page_to_load("30000")
        
        self.assertFalse(check_if_user_exists(name = self.name))
        
if __name__ == "__main__":
    unittest.main()
