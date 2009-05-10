#!/usr/bin/python
import sys,os
from gui_integration_tests.test_settings import PYTHON_LIB, app_id, host, auth_user, auth_psswd, auth_domain

sys.path.append(PYTHON_LIB)
sys.path.append("%s/lib/yaml/lib"%PYTHON_LIB)

os.environ['AUTH_DOMAIN'] = auth_domain
os.environ['USER_EMAIL'] = '' 
   
from google.appengine.ext.remote_api import remote_api_stub
from google.appengine.ext import db
from google.appengine.api.users import User

from models.neighborhood import Neighborhood
from models.volunteer import Volunteer
from models.event import Event
from models.eventvolunteer import EventVolunteer


def auth_func():
    return auth_user, auth_psswd  
    #raw_input('Username:'), getpass.getpass('Password:')

remote_api_stub.ConfigureRemoteDatastore(app_id, '/remote_api', auth_func, host)

# populates the FV datastore with some elements for use in the testing environment    
def populate(sessionid):
    print 'Populating FV...'
    
    neighborhoods = dict([(n.name, n) for n in db.GqlQuery('SELECT * from Neighborhood')])
    
    for i in range(3):
        email = 'volunteer%i@test.org'%i
        u = User(email)

        v = Volunteer(
          name = email,
          user = u,
          #avatar = None,
          #quote = 'test quote',
          #twitter = None,
          home_neighborhood = neighborhoods['Capitol Hill'],
          #work_neighborhood = None,
          session_id = sessionid,
          create_rights = False)
        
        v.put()      

    for i in range(3):
        email = 'organization%i@test.org'%i
        u = User(email)

        v = Volunteer(
          name = email,
          user = u,
          #avatar = None,
          #quote = 'test quote',
          #twitter = None,
          home_neighborhood = neighborhoods['Capitol Hill'],
          #work_neighborhood = None,
          session_id = sessionid,
          create_rights = True)
        
        v.put()      


#    for i in range(5):
#        e = Event(
#                  
#        )
            
# eliminates all datastore items with the given sessionid
def armageddon(sessionid):
    print 'De-populating FV...'

    vols = db.GqlQuery('SELECT * from Volunteer WHERE session_id = :session_id',
                session_id = sessionid)
    for v in vols:
        v.delete()

def check_if_user_exists(name):
    vols = db.GqlQuery('SELECT * from Volunteer WHERE name = :name',
                name = name)
    v = [v.name for v in vols]
    return v != []            

def delete_user(name):
    vols = db.GqlQuery('SELECT * from Volunteer WHERE name = :name',
                name = name)
    for v in vols:
        v.delete()
        
def get_events(name):
    events = db.GqlQuery('SELECT * from Event WHERE name = :name',
                name = name)
    return events
    
def delete_event(name):
    events = db.GqlQuery('SELECT * from Event WHERE name = :name',
                name = name)
    for e in events:
      if e.eventvolunteers:
        for ev in e.eventvolunteers:
          ev.delete()
      # TODO: Delete interest categories    
      #if e.eventinterestcategories:
      #  for ei in e.eventinterestcategories:
      #    ei.delete()
      e.delete()
        
if __name__ == '__main__':
    populate(sessionid = 'test')
    armageddon(sessionid = 'test')
        