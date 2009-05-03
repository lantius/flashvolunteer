from selenium import selenium
import unittest, time, re, os


class NewTest(unittest.TestCase):
    def setUp(self):
        self.verificationErrors = []
        self.selenium = selenium("localhost", 4444, "*chrome", "http://localhost:9999/")
        self.selenium.start()
    
    def test_new(self):
        sel = self.selenium
        sel.open("/")
        sel.click("//div[@id='buttons']/a[1]/span[2]")
        sel.wait_for_page_to_load("30000")
        sel.type("email", "org@example.com")
        sel.click("submit-login")
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
        sel.wait_for_page_to_load("30000")
        sel.click("link=Log Out")
        sel.wait_for_page_to_load("30000")
    
    def tearDown(self):
        self.selenium.stop()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    unittest.main()
