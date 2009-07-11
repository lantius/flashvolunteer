from gui_integration_tests.test_cases import BaseTestCase, TestEnv
from gui_integration_tests.datastore_interface import check_if_user_exists
from gui_integration_tests.test_settings import host

from selenium import selenium
from Queue import Queue
import unittest, re

class CrawlAllLinks(BaseTestCase):
    #test_env = TestEnv(create_new_user = True)
    
    test_env = TestEnv(
         organization = False,
         create_new_user = False,
         login_email = 'thomas_jefferson@volunteer.org',
         login_name = 'Thomas Jefferson'
         )
    
    def test_crawl_all(self):
        base_url = 'http://%s/'%host
        sel = self.selenium

        urls = Queue()
        urls.put(base_url)
        added = {}
        
        regex = r'href="(/.*?)"'
        while not urls.empty():
            url = urls.get()
            sel.open(url)
            page = sel.get_html_source()
            
            links = re.findall(regex, page)
            self.failIfEqual(0, len(links), 'Suspicious absence of links at %s, with page content:\n\n%s'%(url, page))
            
            for rel_link in links:
                if rel_link not in added and rel_link.find('action=Logout') == -1 and \
                   rel_link.find('.css') == -1 and \
                   rel_link.find('.js') == -1:
                    urls.put(rel_link)            
                    added[rel_link] = True

    
if __name__ == "__main__":
    unittest.main()
