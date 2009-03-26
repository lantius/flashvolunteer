import os, string

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp

from controllers._auth import Authorize

from models import Message

################################################################################
# Messages page
################################################################################
class MessagesPage(webapp.RequestHandler):

  ################################################################################
  # GET
  ################################################################################    
  def get(self, url_data):
    if url_data:
      self.show(url_data[1:])
    else:
      self.list()

  ################################################################################
  # POST
  ################################################################################
  def post(self, url_data):
    try:
      (user, volunteer) = Authorize.login(self, requireUser=True, requireVolunteer=True, redirectTo='settings')
    except:
      return

    params = Parameters.parameterize(self.request)
    
    if 'is_delete' in params and params['is_delete'] == 'true':
      self.delete(params, volunteer)
      self.redirect("/messages")
      return

    self.create(params, volunteer)
    self.redirect("/messages")
    return
    
  ################################################################################
  # CREATE
  ################################################################################
  def create(self, params, volunteer):
    message = Message()
    message.title = params['title']
    message.sender = volunteer
    message.content = params['content']
    message.put()
    
    return message.key().id()
    