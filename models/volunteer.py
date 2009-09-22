from google.appengine.ext import db
from models.neighborhood import Neighborhood
from models.abstractuser import AbstractUser

#For verifying volunteer creation
from controllers._twitter import Twitter 


################################################################################
# Volunteer
class Volunteer(AbstractUser):

  home_neighborhood = db.ReferenceProperty(Neighborhood, collection_name = 'home_neighborhood')
  work_neighborhood = db.ReferenceProperty(Neighborhood, collection_name = 'work_neighborhood')

  privacy__event_attendance = db.StringProperty(default='friends')

  def validate(self, params):
    
    # Not verifying these updates
    if 'home_neighborhood' in params:
      if params['home_neighborhood'] == 'None':
        self.home_neighborhood = None;
      else:
        self.home_neighborhood = Neighborhood.get_by_id(int(params['home_neighborhood']))

    if 'work_neighborhood' in params:
      if params['work_neighborhood'] == 'None':
        self.work_neighborhood = None;
      else:
        self.work_neighborhood = Neighborhood.get_by_id(int(params['work_neighborhood']))
   
      #Interest Categories updates happen in the controller

    if 'privacy__event_attendance' in params and self.privacy__event_attendance != params['privacy__event_attendance']:
        self.privacy__event_attendance = params['privacy__event_attendance']
        
    return AbstractUser.validate(self, params)
    

  def get_first_name(self):
      if self.get_name().find('@') > -1:
          return '@'.join(self.get_name().split('@')[:-1])
      else:
          return ' '.join(self.get_name().split(' ')[:-1])
  
  def get_last_name(self):
      if self.get_name().find('@') > -1:
          return '@' + self.get_name().split('@')[-1]
      else:
          return self.get_name().split(' ')[-1]

  def url(self):
    return '/volunteers/' + str(self.key().id())

  def interestcategories(self):
    return (vic.interestcategory for vic in self.volunteerinterestcategories)

  def following(self):
    return (f.volunteer for f in self.volunteerfollowing)

  def following_len(self):
    return len(self.following())

  def followers(self):
    return (f.follower for f in self.volunteerfollowers)

  def followers_len(self):
    return len(self.followers())

  def teammates_ids(self):
      return dict([(v.key().id(),1) for v in self.following() ])

  # both following and follower
  def friends(self):
    fr = []
    
    following = dict([(f.key().id(),1) for f in self.following()])
    for follower in self.followers():
        if follower.key().id() in following:            
          fr.append(follower)
    return [f for f in fr]

  def friends_len(self):
    return len(self.friends())

  def followers_only(self):
      friends = dict([(f.key().id(),1) for f in self.friends()])
      return (f for f in self.followers() if f.key().id() not in friends)

  def following_only(self):
      friends = dict([(f.key().id(),1) for f in self.friends()])
      return (f for f in self.following() if f.key().id() not in friends)

  def event_access(self, volunteer):
      friends = [f.key().id() for f in self.friends()]
      return self.privacy__event_attendance == 'everyone' or (self.privacy__event_attendance == 'friends' and volunteer.key().id() in friends)
      
  
