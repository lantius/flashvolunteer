from gui_integration_tests.test_cases import LoginFirst_Volunteer

from selenium import selenium
import unittest

class UpdateProfileTest(LoginFirst_Volunteer):
    
    def test_new(self):
        sel = self.selenium
        sel.wait_for_page_to_load("30000")
        sel.click("link=PROFILE")
        sel.wait_for_page_to_load("30000")
        sel.type("quote", "selenium has arrived!")
        sel.click("//input[@value='Update']")
        sel.wait_for_page_to_load("30000")
        sel.click("link=HOME")
        sel.wait_for_page_to_load("30000")
        try: self.failUnless(sel.is_text_present("selenium has arrived!"))
        except AssertionError, e: self.verificationErrors.append(str(e))
        try: self.failUnless(sel.is_text_present("volunteer0@test.org"))
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.click("link=PROFILE")
        sel.wait_for_page_to_load("30000")
        sel.type("name", "selenium test")
        sel.click("//input[@value='Update']")
        sel.wait_for_page_to_load("30000")
        try: self.failUnless(sel.is_text_present("Welcome, selenium test"))
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.click("link=HOME")
        try: self.failUnless(sel.is_text_present("selenium test"))
        except AssertionError, e: self.verificationErrors.append(str(e))
        try: self.failUnless(sel.is_text_present("Capitol Hill"))
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.click("link=PROFILE")
        sel.wait_for_page_to_load("30000")
        sel.select("home_neighborhood", "label=West Seattle")
        sel.select("work_neighborhood", "label=University District")
        sel.click("//input[@value='Update']")
        sel.wait_for_page_to_load("30000")
        sel.click("link=HOME")
        sel.wait_for_page_to_load("30000")
        try: self.failUnless(sel.is_text_present("West Seattle"))
        except AssertionError, e: self.verificationErrors.append(str(e))
        try: self.failUnless(sel.is_text_present("University District"))
        except AssertionError, e: self.verificationErrors.append(str(e))
        sel.click("link=PROFILE")
        sel.wait_for_page_to_load("30000")
        sel.click("//input[@name='interestcategory[5]' and @value='1' and @type='checkbox']")
        sel.click("//input[@name='interestcategory[9]' and @value='1' and @type='checkbox']")
        sel.click("//input[@name='interestcategory[12]' and @value='1' and @type='checkbox']")
        sel.click("//input[@name='interestcategory[14]' and @value='1' and @type='checkbox']")
        sel.click("//input[@value='Update']")
        try: self.failUnless(sel.is_checked("//input[@name='interestcategory[5]' and @value='1' and @type='checkbox']"))
        except AssertionError, e: self.verificationErrors.append(str(e))
        try: self.failUnless(sel.is_checked("//input[@name='interestcategory[9]' and @value='1' and @type='checkbox']"))
        except AssertionError, e: self.verificationErrors.append(str(e))
        try: self.failUnless(sel.is_checked("//input[@name='interestcategory[12]' and @value='1' and @type='checkbox']"))
        except AssertionError, e: self.verificationErrors.append(str(e))
        try: self.failUnless(sel.is_checked("//input[@name='interestcategory[14]' and @value='1' and @type='checkbox']"))
        except AssertionError, e: self.verificationErrors.append(str(e))

if __name__ == "__main__":
    unittest.main()

