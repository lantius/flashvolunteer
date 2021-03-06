import unittest

from models.messages.message import *
from models.event import *
from models.volunteer import *

from controllers.events import *
from controllers.messages import *


class MessagesTest(unittest.TestCase):
  def setUp(self):
    self.volunteer  = Volunteer()
    self.volunteer.create_rights = True
    self.volunteer.put()
    
    self.interestcategory1 = InterestCategory()
    self.interestcategory1.put()

    self.interestcategory2 = InterestCategory()
    self.interestcategory2.put()
    
  def tearDown(self):
    self.volunteer.delete()
    self.interestcategory1.delete()
    self.interestcategory2.delete()
  
  def test_message_create(self):
    m = MessagesPage()
    params = { 'title' : 'test message', 
               'content' : 'lorum ipsum\ndolor sit amet',
               'recipient' : None }
    message_id = m.create(params, self.volunteer)
    message = Message.get_by_id(int(message_id))
    
    self.assertTrue(message)
    self.assertEqual(params['title'], message.title)
    self.assertEqual(params['content'], message.content)
    self.assertEqual(self.volunteer.key().id(), message.sender.key().id())
    return message
  
  def test_message_delete(self):
    m = MessagesPage()
    n = Message.all().count()
    message = self.test_message_create()
    self.assertEqual(n+1, Message.all().count())
    m.delete( message.key().id() , self.volunteer)
    self.assertEqual(n, Message.all().count())
  
  def test_event_message_create(self):
    e = EventsPage()
    params = { 'name' : 'create unit test',
               'neighborhood' : 1,
               'date' : '01/01/2009',
               'startdate' : '01/01/2009',
               'starthour' : '3',
               'startminute' : '0',
               'time' : '03:00',
               'duration' : '120',
               'enddate' : '01/01/2009',
               'endhour' : '5',
               'endminute' : '0',
               'description' : 'test description\non the internet with two lines!',
               'special_instructions' : 'special instructions',
               'address' : '3334 NE Blakeley St.\nSeattle, WA 98105',
               'interestcategory[' + str(self.interestcategory1.key().id()) + ']' : ['1','1'],
               'interestcategory[' + str(self.interestcategory2.key().id()) + ']' : '1'  }
    event_id = e.create(params, self.volunteer)
    event = Event.get_by_id(int(event_id))

    self.assertEqual(self.volunteer.sent_messages.count(), 0)
    self.assertEqual(event.messages.count(), 0)
    
    m = MessagesPage()
    params = { 'title' : 'test message', 
               'content' : 'lorum ipsum\ndolor sit amet',
               'recipient' : event }
    message_id = m.create(params, self.volunteer)
    message = Message.get_by_id(int(message_id))
    
    self.assertEqual(message.url(), event.url() + '/messages/' + str(message_id))
    self.assertEqual(self.volunteer.sent_messages.count(), 1)
    self.assertEqual(event.messages.count(), 1)
    self.assertEqual(self.volunteer.messages.count(), 0)

  def test_message_sendemail(self):
    message = self.test_message_create()
    volunteer = Volunteer()
    volunteer.user = users.get_current_user()
    volunteer.name = "Test Volunteer"
    volunteer.put()
    message.recipient = volunteer
    message.put()
    
    message.sendemail()
    
    
    
    
  