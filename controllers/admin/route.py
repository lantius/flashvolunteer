import os, logging

from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app


from components.sessions import Session

import wsgiref.handlers

from controllers.admin.migrate_datastore import MigrateDatastore
from controllers.admin.message_dispatcher import MessageDispatcher
from controllers.admin.event_message_factory import EventMessageFactory

application = webapp.WSGIApplication([
    ('/admin/migrate', MigrateDatastore),
    ('/admin/message_dispatch', MessageDispatcher),
    ('/admin/event_message_factory', EventMessageFactory)

], debug=True)

def main():
    run_wsgi_app(application)                                    

if __name__ == '__main__':
    main()