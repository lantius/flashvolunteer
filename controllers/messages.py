import os, string

from google.appengine.ext.webapp import template
from google.appengine.api import users
from google.appengine.ext import webapp

from controllers._auth import Authorize

from models.event import *
from models.message import *

################################################################################
# Messages page
################################################################################
class MessagesPage(webapp.RequestHandler):

  ################################################################################
  # GET
  def get(self, url_data):
    if url_data:
      self.show(url_data[1:])
    else:
      self.list()

  ################################################################################
  # POST
  def post(self, url_data):
    try:
      (user, volunteer) = Authorize.login(self, requireUser=True, requireVolunteer=True, redirectTo='settings')
    except:
      return

    params = Parameters.parameterize(self.request)
    
    if 'is_delete' in params and params['is_delete'] == 'true':
      self.delete(url_data[1:], volunteer)
      self.redirect("/messages")
      return

    self.create(params, volunteer)
    self.redirect("/messages")
    return
    
  ################################################################################
  # CREATE
  def create(self, params, volunteer):
    message = Message()
    message.title = params['title']
    message.sender = volunteer
    message.content = params['content']
    message.recipient = params['recipient']
    
    message.put()
    
    return message.key().id()
    
  ################################################################################
  # DELETE
  def delete(self, message_id, volunteer):
    message = Message.get_by_id(int(message_id))
    message.delete()