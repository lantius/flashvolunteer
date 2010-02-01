from google.appengine.ext import db

from models.event import Event
from models.auth.account import Account

################################################################################
class EventPhoto(db.Model):
    event = db.ReferenceProperty(Event,
                                 required = True,
                                 collection_name = 'eventphotos')
    
    #person who posted photo or created album
    account = db.ReferenceProperty(Account,
                                   required = True,
                                   collection_name = 'eventphotos')  
    
    #link, or title for INTERNAL_ALBUM)
    content = db.StringProperty(required = True)
    
    type = db.IntegerProperty(required = True)
    #type values
    RSS_ALBUM=1
    INTERNAL_ALBUM=2
    #FACEBOOK_ALBUM=3
    PHOTO=4
    
    status = db.IntegerProperty(required = True)
    #status values
    UNPUBLISHED=1
    PUBLISHED=2
    
    #determines order of display, smaller numbers first
    display_weight = db.IntegerProperty(default = 0)
    
    #None for root; parent should only be INTERNAL_ALBUM
    display_parent = db.SelfReferenceProperty(default = None,
                                              collection_name = 'eventphotoparents') 
    
    def can_edit(self, requester):
        #want to know if requester can edit; 
        if not self.account or not requester: return False
        
        #can edit if the original poster
        if (requester.key() == self.account.key()):
            return True
        
        #can edit if event owner 
        eventvolunteers_owners = self.event.hosts()
        owner_keys = [ev.volunteer.account.key() for ev in eventvolunteers_owners]
        
        if (requester.key() in owner_keys):
            return True
        return False
