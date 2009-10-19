from google.appengine.api import users
from google.appengine.ext import db
from models.abstractuser import AbstractUser

#For verifying volunteer creation
from controllers._twitter import Twitter 


################################################################################
# Organization
class Organization(AbstractUser):
  

  def validate(self, params):
    AbstractUser.validate(self, params)

  def url(self):
    return '/organizations/' + str(self.key().id())


  def fans(self):
    return (f.follower for f in self.organizationfollowers)

  def fans_len(self):
    return len(self.followers())
  
