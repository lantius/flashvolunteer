from components.twitter import Api

class Twitter():
  
  def toot(text, twitter):
    api = Api(username='flashvolunteer', password='ps2mouse')
    followers = api.GetFollowers()
    for f in followers:
      if f.screen_name == twitter:
        api.PostUpdate("@" + twitter + " " + text)
  
  toot = staticmethod(toot)
  