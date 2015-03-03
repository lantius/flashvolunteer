

# Introduction #

**Note** the messaging subsystem is not quite implemented like this anymore, but the same architecture is generally in place.



# When might a message need to be sent #

People will need to send messages or have messages sent to them at various points. Here are some cases:
  * event management
    * before event **(done)**
      * messages to event hosts
        * when a volunteer signs up **(done)**
        * when a volunteer rsvps
        * direct message from attendee to host **(done)**
      * messages to event attendee
        * day-of-event cron job asking for RSVP **(done)**
        * when a message is posted in the event forum
        * direct message from host to attendee(s) **(done)**
  * when someone is added as event coordinator they need to get a message
    * post event
      * messages to event hosts -- ask to verify attendees, post pictures **(done)**
      * messages to event attendees -- ask to rate event, post pictures, how the event went **(done)**
    * event, anytime
      * when someone makes a post to the event forum
  * social networking
    * when someone adds you to their team **(done)**
    * send a message to anyone **(done)**
    * share event photos with friends (low priority)
  * weekly newsletter of general info + recommended upcoming events (lower priority for now; use twitter newsfeed for now)
  * social media integration
    * twitter/FB propagation **(done)**
    * google calendar integration (rudimentary) **(done)**
    * twitter news feed on front page **(done)**

# The message system #

To provide the backbone of the various messages, we need to have a message creation and dispatching service. As implemented, this service is datastore-driven.

Everyone/organization has a mailbox. All of the message cases above can be seen as the construction of a message. Everyone gets internal FV messages delivered to their mailboxes. But people control HOW (e.g. email, RSS) and WHEN (e.g. individual, digest) those messages are propagated outside the internal message dispatcher.

Currently the HOW is implemented, but not the WHEN. Below, I sketch out the communication system, starting with the model structure, moving through the message dispatcher and other cron jobs, and finally how messages are manifested in views.


## Model Structure ##

There are four message models.

### Message ###

` Message ` stores the subject/body of a message, recipients (as a list of volunteer ids), who sent it (or None if it will be on behalf of FlashVolunteer), who has read the message, whether it has been sent, when it is meant to be sent (` trigger `), its ` MessageType ` (see next), etc etc.

### MessageType ###

` MessageType ` there will be a limited number of types of messages that propagate through FV. These types must be stored as a ` MessageType `. Each ` MessageType ` has a unique name, a prompt (displayed in the Message Settings section of a volunteer's profile), and an 'order' which serves as a unique identifier across different datastores.

Every MessageType. MessageTypes need to be defined in ` components.applications.operations ` in the ` add_messaging ` section. You can synchronize the current app by visiting ` /admin/migrate ` while logged in as an admin.

Every MessageType has a default propagation method (e.g. by default, this type of message will be sent as an email and SMS, but not stored in my mailbox). This is manifested as a list of ` MessagePropagationType ` ids.

### MessagePropagationType ###

` MessagePropagationType `s are the places to which a ` Message ` may be sent, and for which a ` Volunteer ` may have an opinion about. There are currently only two enabled, email and Flash mailbox.

Like ` MessageType `, ` MessagePropagationType `s need to be registered in the system through the datastore. Follow the same directions above for ` MessageType ` to incorporate a new ` MessagePropagationType `.

### MessagePreference ###

Volunteers will have opinions about how they want to be contacted. ` MessagePreference `s store the ` MessagePropagationType `s for a given ` MessageType ` by which a ` Volunteer ` wishes to be notified. A ` MessagePreference ` will only be created if a Volunteer modifies their default settings. By default, the default propagation method defined in ` MessageType ` will be used. This is intended to cut down on the size of the ` MessagePreference ` table (most people won't change defaults).


## Dispatch and cron ##

These controllers send or manufacture messages. A couple of them are invoked by cron jobs defined in ` cron.yaml `

### Message Dispatcher ###

The Message Dispatcher is located at ` controllers.admin.message_dispatcher `. It can be accessed/triggered at ` /admin/message_dispatch ` if you are logged in as an admin.

This service is simple. It just looks at all the stored messages which have yet to be sent but whose trigger time has past. For each of these messages, it calls the messages' send method.

The message\_dispatch is currently invoked every minute as a cron job.

### Message Factories ###

Message Factories generate messages according to specific criteria. They are not so formalized in the code, and there is only one example: generating event messages just ahead of the event (RSVP) and post event (verify attendance, post pics). This factory lives at ` controllers.admin.event_message_factory ` and can be access/triggered at ` /admin/event_message_factory ` if you are logged in as an admin.

This service is currently invoked every five minutes as a cron job.

### send\_message ###

This is a method placed arbitrarily in ` controllers._utils `. It will create a method given a bunch of parameters. A number of controllers use this method to create messages based on certain events (e.g. someone adds someone else to their team). The method just creates a Message model instance and puts it to the datastore. The dispatcher will send it when appropriate. There is also an optional argument to ` send_message ` which will trigger the dispatcher immediately. This is useful for, e.g., welcome messages to new users.

## Views ##

Obviously the messages need to be seen. This section has info about how/where this is done, and how volunteers can control their notifications.

### Mailbox ###

A new tab in the nav bar. Will have a (n) to show when you have messages. The view code is in ` views.messages.mailbox `.

It is a reverse-chronologically ordered list of messages sent to the volunteer.

The system keeps track of read/unread messages.

Clicking on a message takes you to a detail page (` views.messages.message `) that has the full message, reply options, etc. (nb: more stuff needs to be added here, like delete and flag as inappropriate).

These views are controlled by ` controllers.messages `.

### Message settings ###

The settings page for every volunteer now has a message settings section that determines how a message is propagated. Currently, the only two options are "email" and "mailbox". Later we can have RSS, SMS, etc.

### Message creation form and controller ###

There is a generalized message creator at ` views.messages.create_message `. It is controlled by subclasses of a ` AbstractSendMessage `, found in ` controllers.message_writer `. There is currently one subclass, ` SendMessage_Personal `, which implements individual to individual messages.

This is probably part of the solution for event and neighborhood forum implementation.

## Message text ##

In order to centralize the text for messages, it is all located in ` components.message_text `. The body and subject for each MessageType is given, labeled by the MessageType's ` order ` property. Specific parameters can be added to the defined strings by the controllers as necessary.

# Event and Neighborhood forum #

Implement this using the messaging system. Don't do threaded conversation, just use basic reverse-temporal blog model.

When someone posts to a forum, a message is created to notify relevant parties that a forum post was made.

# Other info #

  * in budget: 3000/email _recipients_ per day free on app engine