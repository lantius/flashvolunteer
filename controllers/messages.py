import os, string

from google.appengine.ext.webapp import template
from google.appengine.ext import webapp

from controllers._auth import Authorize

from models.event import Event
from models.message import Message

from controllers.abstract_handler import AbstractHandler
from controllers._utils import is_debugging

################################################################################
# Messages page
################################################################################
class Mailbox(AbstractHandler):

    ################################################################################
    # GET
    def get(self, url_data):
      if url_data:
        self.show(url_data[1:])
      else:
        self.list()
    
    ################################################################################
    # POST
    #  def post(self, url_data):
    #    try:
    #      volunteer = Authorize.login(self, requireVolunteer=True, redirectTo='/settings')
    #    except:
    #      return
    #
    #    params = Parameters.parameterize(self.request)
    #    
    #    if 'is_delete' in params and params['is_delete'] == 'true':
    #      self.delete(url_data[1:], volunteer)
    #      self.redirect("/messages")
    #      return
    #
    #    self.create(params, volunteer)
    #    self.redirect("/messages")
    #    return
      
    def show(self, id):
        try:
            volunteer = Authorize.login(self, requireVolunteer=True)
        except:
            return
        
        message = Message.get_by_id(int(id))
        if not message or not volunteer.key().id() in message.recipients:
            self.redirect(self.request.referral)
        
        template_values = {
            'volunteer': volunteer,
            'message': message
          }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__),'..', 'views', 'messages', 'message.html')
        self.response.out.write(template.render(path, template_values, debug=is_debugging()))        
        
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
        
    ################################################################################
    # LIST
    def list(self):
        try:
            volunteer = Authorize.login(self, requireVolunteer=True)
        except:
            return
        
        template_values = {
            'volunteer': volunteer,
          }
        self._add_base_template_values(vals = template_values)
        
        path = os.path.join(os.path.dirname(__file__),'..', 'views', 'messages', 'mailbox.html')
        self.response.out.write(template.render(path, template_values, debug=is_debugging()))