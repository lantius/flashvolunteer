######################################################################
#
# Assembled message text that is generated in the communication system.
#
######################################################################


class msg(object):
    def __init__(self, subject, body):
        self.body = body
        self.subject = subject


###############################################################
# Type 1: Message to event host when someone signs up for event 
###############################################################

type1_vol = msg(

    subject = 'A volunteer has signed up for %(event_name)s',
    body = """
Hi %(owner_name)s,

%(vol_name)s has signed up for \"%(event_name)s\". You now have %(vol_count)s volunteer(s) signed up. 
"""
)

type1_unvol = msg(
    subject = 'Someone unvolunteered for %(event_name)s',
    body="""
Hi %(owner_name)s,

%(vol_name)s is no longer able to attend your event \"%(event_name)s\". You now have %(vol_count)s volunteer(s) signed up. 
"""
)

for type1 in (type1_vol, type1_unvol):
    type1.body += """
To manage your event, visit %(event_url)s. 
    
Please let us know if you have any questions.
"""


###############################################################
# Type 2: Message to volunteer when they are added to team
###############################################################

type2 = msg(

    subject = '%(adder_name)s has%(reciprocation)s added you to their Flash Team',
    body = """
Hi %(vol_name)s,

%(adder_name)s has%(reciprocation)s added you to their Flash Team. 

You can do the same by visiting %(adder_url)s.
"""
)


###############################################################
# Type 3: When someone signs up for Flash Volunteer
###############################################################

type3 = msg(

    subject = 'Welcome to Flash Volunteer!',
    body = """Hello %(name)s, 

We hope that you will be able to use this site to easily find and coordinate volunteer opportunities in the most timely and convenient fashion as possible.

Get started by filling out your profile and checking out the listed events!

If you have any questions, send an email to info@flashvolunteer.org.
"""
)

###############################################################
# When someone has lost their account info
###############################################################

login_info_text = msg(

    subject = 'Your account information for Flash Volunteer',
    body = """Hello, 

Someone has requested account information for this email address (we hope it was you, but if not, please report abuse to info@flashvolunteer.org). 

We have determined that your account provider is %(provider)s. %(hint)s
"""
)

###############################################################
# Type 5: Event rsvp for volunteer
###############################################################

type5 = msg(

    subject = 'RSVP for "%(event_name)s"',
    body = """Hello, 

"%(event_name)s" is happening at %(event_start_time)s on %(event_start_date)s! You have signed up to volunteer there. 

Please visit the event page at %(event_url)s and send one of the event organizers a message in order to RSVP.   
"""
)

###############################################################
# Type 6: Event rsvp for organizer
###############################################################

type6 = msg(

    subject = 'You are organizing "%(event_name)s"',
    body = """Hello, 

You are organizing "%(event_name)s", scheduled to occur on %(event_start_date)s at %(event_start_time)s! 

%(participation_statement)s

Please visit the event page at %(event_url)s to edit the event or contact volunteers.     
"""
)

###############################################################
# Type 7: Post event for volunteer
###############################################################

type7 = msg(

    subject = 'You participated in "%(event_name)s"',
    body = """Hello, 

You participated in "%(event_name)s"! We hope that you enjoyed it. 

Visit the event page at %(event_url)s to upload photos, send the event organizers feedback, and connect with other volunteers you may have met. 

If you did not participate, please visit the event site and remove yourself from the participants list.
"""
)

###############################################################
# Type 8: Post event for organizer
###############################################################

type8 = msg(

    subject = 'You organized "%(event_name)s"',
    body = """Hello, 

You organized "%(event_name)s". We hope that it went well! 

%(participation_statement)s 

We hope that you will continue organizing events on Flash Volunteer!  
"""
)

###############################################################
# Type 9: recommended events
###############################################################

type9 = msg(

    subject = 'Your weekly volunteer recommendations',
    body = """Hello %(vol_name)s, 

Here are the events we think you might be interested in, based on the neighborhoods you work and live in and your selected interest categories. We hope that you find them useful!

%(recommendation_text)s 
"""
)


###############################################################
# post to forum
###############################################################

event_forum_txt = msg(

    subject = '%(sender_name)s posted a message to event "%(event_name)s"',
    body = """Hello, 

%(sender_name)s sent a message to event "%(event_name)s". 

Subject: "%(message_subject)s"
Body: "%(message_body)s"

To see this event's message forum, follow the link below: 
%(event_url)s 
"""
)

neighborhood_forum_txt = msg(

    subject = '%(sender_name)s posted a message to "%(neighborhood_name)s"',
    body = """Hello, 

%(sender_name)s sent a message to "%(neighborhood_name)s". 

Subject: "%(message_subject)s"
Body: "%(message_body)s"

To see this event's message forum, follow the link below: 
%(neighborhood_url)s 
"""
)

