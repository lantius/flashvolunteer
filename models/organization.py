from google.appengine.ext import db
from models.abstractuser import AbstractUser

#For verifying volunteer creation
from controllers._twitter import Twitter 

from models.auth.account import Account

################################################################################
# Organization
class Organization(AbstractUser):
  
    account = db.ReferenceProperty(Account, collection_name = 'org_user')
    
    def validate(self, params):
        AbstractUser.validate(self, params)
    
    def url(self):
        return '/organizations/' + str(self.key().id())
    
    
    def fans(self):
        return (f.follower for f in self.organizationfollowers)
    
    def fans_len(self):
        return len(self.followers())
  
