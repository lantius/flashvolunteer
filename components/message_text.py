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

Someone decided they could not help out at \"%(event_name)s\". You now have %(vol_count)s volunteer(s) signed up. 
"""
)

for type1 in (type1_vol, type1_unvol):
    type1.body += """
To manage your event, visit %(event_url)s. 
    
Please let us know if you have any questions or if you would prefer not to get emails like this.
    
Thanks,
The Flash Volunteer Team
"""


###############################################################
# Type 2: Message to volunteer when they are added to team
###############################################################

type2 = msg(

    subject = '%(adder_name) has added you to their Flash Team',
    body = """
Hi %(vol_name)s,

%(adder_name)s has added you to their Flash Team. 

You can do the same (if you haven't already) by visiting %(adder_url)s or by clicking the (+) button under their name in your %(vol_team_url)s.
    
Please let us know if you have any questions or if you would prefer not to get emails like this.

Thanks,
The Flash Volunteer Team
"""
)