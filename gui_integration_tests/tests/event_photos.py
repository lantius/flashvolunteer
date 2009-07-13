from gui_integration_tests.test_cases import BaseTestCase, TestEnv
from gui_integration_tests.datastore_interface import *
from models.eventvolunteer import *

from selenium import selenium
import unittest
import time

class EventPhotosTestCase(BaseTestCase):
  test_env = TestEnv(
     organization = False,
     create_new_user = False,
     login_email = 'john_hancock@volunteer.org',
     login_name = 'John Hancock'
     )
  attendee_env = TestEnv(
     organization = False,
     create_new_user = False,
     login_email = 'thomas_jefferson@volunteer.org',
     login_name = 'Thomas Jefferson'
     )
  event_name = 'Sign the Declaration of Independence'
  rss_name01 = 'http://picasaweb.google.com/data/feed/base/user/acwanka/albumid/5347718167296403601?alt=rss&kind=photo&hl=en_US'
  album_name01 = 'India'
  pic_url01_01 = 'http://lh6.ggpht.com/_ieb_vmBkw-w/SjbpWYUWvaI/AAAAAAAAAWM/GRdzvyW6r5c/s288/DSCF0085.jpg'
  pic_url01_05 = 'http://lh5.ggpht.com/_ieb_vmBkw-w/SjbpYCJ2dVI/AAAAAAAAAWc/8wyChoyIo_w/s288/DSCF0103.jpg'
  rss_name02 = 'http://api.flickr.com/services/feeds/photoset.gne?set=72157619755097601&nsid=21238699@N00&lang=en-us'

  def setUp(self):
    "unittest override"
    BaseTestCase.setUp(self)
    

  def test_add_view_photos(self):
    """testing adding albums to past event, 
    then test viewing photos"""
    sel = self.selenium
    sel.open('/events/%i' % self.test_object_index[self.event_name].key().id())
    sel.wait_for_page_to_load("30000")

    #add 1st album
    sel.select("eventphotos_addalbum", "label=Add External Album...")
    sel.type("addexternalbum_dialog_content", self.rss_name01)
    sel.click("s_addexternalalbum")
    sel.wait_for_page_to_load("30000")
    
    eventphotos = get_eventphotos(self.event_name)
    first_album = eventphotos[0]
    
    self.failUnless(sel.is_text_present(self.album_name01))
    #test for up/down/remove buttons
    self.failUnless(sel.is_element_present("//input[@id='rss_album_%d_up']" % first_album.key().id()))  
    self.failUnless(sel.is_element_present("//input[@id='rss_album_%d_down']" % first_album.key().id()))  
    self.failUnless(sel.is_element_present("//input[@id='rss_album_%d_remove']" % first_album.key().id()))  
    
    #test for presence of picture
    #not sure that this url is always the same
    self.failUnless(sel.is_element_present("//img[@src='%s']" % self.pic_url01_01))
    #should only show 4 photos  
    self.failIf(sel.is_element_present("//img[@src='%s']" % self.pic_url01_05))  

    #add 2nd album
    sel.select("eventphotos_addalbum", "label=Add External Album...")
    sel.type("addexternalbum_dialog_content", self.rss_name02)
    sel.click("s_addexternalalbum")
    sel.wait_for_page_to_load("30000")
    
    #show more
    sel.click("more_%d" % first_album.key().id())
    #don't know how to wait for ajax in selenium
    time.sleep(10)
    #5th picture should be shown (less only shows 4)
    self.failUnless(sel.is_element_present("//img[@src='%s']" % self.pic_url01_05))  
    
    #todo: test up/down button

    #now remove
    sel.click("rss_album_%d_remove" % first_album.key().id())
    sel.wait_for_page_to_load("30000")
    
    #removed, name should be gone
    self.failIf(sel.is_text_present(self.album_name01))
    
    #todo: test that add and up/down/remove are not showing if not owner
    self.logout()
    self.login_as_existing_user(self.attendee_env)

    #test for absence of add, up/down/remove
    self.failIf(sel.is_element_present("//select[@id='eventphotos_addalbum']"))
    self.failIf(sel.is_element_present("//input[@id='rss_album_%d_up']" % first_album.key().id()))  
    self.failIf(sel.is_element_present("//input[@id='rss_album_%d_down']" % first_album.key().id()))  
    self.failIf(sel.is_element_present("//input[@id='rss_album_%d_remove']" % first_album.key().id()))  
    
    
  def tearDown(self):
    "unittest override"
    sel = self.selenium
    BaseTestCase.tearDown(self)
    
if __name__ == "__main__":
    unittest.main()
