#v1.9 testing

# Introduction #

We're trying to test the current release candidate.

First, **please sign your name below** in the testers section, along with the browser (or browsers) that you are using to help test. You can edit this page by clicking the "edit this page" blue link in the upper right part of this webpage.

Second, please test out the site. Try as many tasks as you can on http://www.development.flashvolunteer.org. Do obscure things. Try to break it. Example tasks include (but not limited to):
  * create a new user
  * create an event
  * sign up for an event
  * edit your profile
  * send a message to someone
  * click "view all" on some of the lists (e.g. "recommended events")
  * look at your mailbox
  * search for events
  * add someone to your team
  * send a message to a neighborhood

# Testers #

Please sign your name here, with the browsers that you tested the development site on.
  * Travis (Firefox 3.5/OSX10.6, IE6/WinXP, IE7/WinXP, IE8/WinXP, Chrome/WinXP)
  * Hayden (Chrome 4.0.249.30/Safari 4.0.4/OSX 10.6.2)

# Issues #

Please log any strange behavior you see here. Click the "EDIT THIS PAGE" link in the blue bar up top. Make sure to add your browser and operating system.

If you don't know where to put it, just choose one. Other people can decide whether they're critical or not.

Add problems here that need to be fixed, based on your experience with the release candidate. **please make sure to state the web browser and operating system you are using!!**


## general problems ##
  * ~~event photos do not work (Travis, FF, osx10.6)~~
  * ~~delete account not working (Travis, FF, osx10.6)~~
  * ~~openid login not working (Travis, FF, osx10.6)~~

## IE 6 ##

  * page title border not appearing (Travis, IE6, winxp)
  * on homepage, tips for getting started section is misaligned (Travis, IE6, winxp)
  * zindex for paginated dialog box not high enough (or not being respected) (Travis, IE6, winxp)


## IE7 ##
  * ?

## IE 8 ##

  * ?

## Safari ##

  * ?

## Chrome ##
  * ?

## Opera ##
  * ?


## stuff to be fixed later ##

This is just the stuff I've determined to be put off to later.

  * Content suggestion -- On the Help page, the title of a FAQ response should be the question itself. For example, if I click on the second question, the title for the response (set in large type) shouldn't be "Upcoming Events", it should be the question word-for-word. A slightly smaller text size like 14pt or 16pt may be required to make this look good. (Justin, Safari 4.0.4, Mac OS X 10.6.2)
  * on an event page, I clicked on "Your text to link" link in "Special Instructions" area, and was signed out and taken to the splash page. (Eva, Firefox 3.5.5 MacOS 10.6.2)
    * actually it took you to www.flashvolunteer.org. Links in rich text editor should open in a separate window.
  * subject line on direct messages does not say "[name](name.md) sent you a message"
  * when you send a message to a neighborhood or event, and then go to your sent mail, the message shows a random person in the "to" field. This is not expected.
  * profile page "Find a Volunteer" section drop-down menu for "Any neighborhood..." is too long and cut off on the screen. (Eva, Firefox 3.5.5 MacOS 10.6.2)
  * UI bug -- Actual: On the Profile, Events and People pages, the "Any neighborhood..." drop-down menu under the Browse Volunteers section is getting clipped on the right side. Expected: It should render exactly like the drop-down menus under the Find an Event section. (Justin, Safari 4.0.4 and FF 3.0.11, Mac OS X 10.6.2)
  * "Find a Volunteer" drop down menu bar on Profile page is cut off (Brad, Firefox 3.5.5 MacOS 10.6.2)
  * On Create Event page: would be more intuitive if the start date/end date are on the same row, then start/end times are on the same row. (Eva)
  * On Create Event: in box where I'm writing descriptions, it's not respecting the markup. For example, the 'strike-through' (S with a line through it) doesn't work like it should. (Eva, FF3.5.5. MacOS10.6.2)
    * the reset css actually just messes up the markup. we need to revamp that css to accomodate the rich text editing
  * hitting "reply" should fill in the subject line with "re:subject"
  * Would be nice to have a way to organize msgs in the mailbox (delete, mark as read, etc.) (Brad)
  * Add the option to delete message in mailbox (Sara FF3.0.5, Mac OS X 10.5.8)
  * Clicked on "Why am I not coordinating any events?" It took me to Help/FAQ page, but loaded the answer to the question about being in Beta. Would be nice if it automatically displayed the answer to the appropriate question. (Eva, FF3.5.5 MacOS10.6.2)
  * If I'm one someone else's profile page and want to return to my own page, I thought it was intuitive to click "Home" on the menu bar. But that took me to the FV splash page. It wasn't intuitive that if I was already in the Profile Tab (b/c I am looking at someone else's profile) that I can click "Profile" again and will be returned to my own profile page. (Eva)
  * For the host view of an event site: "Cancel event" button NEEDS a confirmation prompt. "Are you sure?" (Eva)
  * add a "keep me in the loop" button on upcoming event pages
  * ajax message window + submit
  * Might be worthwhile to show "Hours Volunteered" on your personal profile page. I would even consider eliminating the colored boxes for "Upcoming Events" and "Upcoming Events I am Coordinating" (since that info is readily apparent in the main column) and adding a box for total number of hours volunteered. (Brad, FF, MacOS)
  * add "settings" link to login status area in site header

## Problems from last phase of testing ##

### critical ###

These are problems that absolutely need to be fixed before deploying this version of the site.
  * ~~"remove from team" not working (seen by Travis on MacOS 1.6, Firefox 3.5)~~
  * ~~event photos messed up on event page (misalignment) (seen by Travis, Eva on MacOS 1.6, Firefox 3.5)~~
  * ~~when you try to create an account from a email that already exists, it will fail (seen by Travis on MacOS 1.6, Firefox 3.5) (**Travis knows why this happens**)~~
  * ~~for FV accounts, typing in bad login info will cause a problem (seen by Travis on MacOS 1.6, Firefox 3.5) (**Travis knows why this happens**)~~
  * ~~mailbox is not resized properly (Travis, 10.6, FF)~~
  * ~~after logging in, profile page "My Upcoming Events" has a blank event listed. (Eva, Firefox 3.5.5 MacOS 10.6.2)~~
  * ~~On event page, I click "View all" volunteers. The screen dims, but no ajax-type window pops up to show all of the volunteers. Then it goes back to normal. (Eva, FF3.5.5 MacOS10.6.2)~~
  * ~~After I signed up for an event, it appears on my profile page under Upcoming Events as two apostrophes and the word "Organizers:"(Brad, Firefox 3.5.5 MacOS 10.6.2)~~
  * ~~When I send msg inviting friends (or post to calendar, etc.), Gmail opens on top of Flash Volunteer, so that after I send the msg, I'm no longer on the FV site. (Brad, Firefox 3.5.5 MacOS 10.6.2)~~
  * ~~On the FV mailbox page, About, Privacy Policy, etc. are all jammed into the right-hand corner instead of appearing at the bottom of the page (Brad, Firefox 3.5.5 MacOS 10.6.2)~~
  * ~~Message Forum on Event page should list messages with the most recent one at the bottom. The way it is now, the response precedes the question.~~
  * ~~When I click "Add to Team", I get sent to homepage. Should send me back to "People" tab. (Brad, Firefox 3.5.5 MacOS 10.6.2)~~
  * ~~I UNvolunteered from an event. The pop-up confirmation window told me that I am now SIGNED UP for the event. (Eva, FF3.5.5 MacOS10.6.2).~~
  * ~~Created an event that should start today in 10 minutes (at 2:30pm on 12/4). It tells me that my event needs to happen in the future. Is the system running on a different time zone? It only let me create it beginning tomorrow (on 12/5). (Eva)~~
  * ~~When I created an event for 6pm this evening, I received an error msg telling me the event must occur in the future (even though it was) (Brad, Firefox 3.5.5 MacOS 10.6.2)~~
  * ~~Created an event. Then clicked "Add another coordinator," but it took me to a blank screen and never loaded. (Eva, FF3.5.5, MacOS10.6.2)~~
  * ~~When I click "Add another event coordinator", it opens a blank page over the original FV page. This blocks me from adding another coordinator. (Brad, FF3.5.5 Mac 10.6.2)~~
  * ~~Is there any way to get off-site windows (email, calendars, etc?) to pop up separately, rather than on top of FV? (Brad)~~
  * ~~scrolling through pagination team, with many people in list, does not work (Travis, FF)~~
  * ~~Was on Brad's page. In the list of Brad's Team, I clicked my own name (hoping to return to my Profile/main page). Instead, it took me to the splash page (but left me signed in at least). Did the same think when I clicked another person (TravisKriplean) in Brad's team. (Eva, FF3.5.5, MacOS10.6.2)~~
  * ~~Two completed events show up on my profile page. However, all they say is "organizer" and "!". There is no information about the events at all. When I clicked "show all completed events," the information was there. (Mellicia, MacOS1010.6.1)~~
  * ~~When I search for someone on the People page, it pulls up everyone.  For example, I searched "TKrip" and it gave me results for everyone signed up on the site. (Sara FF3.0.5, Mac OS X 10.5.8)~~
  * ~~On my profile page, tried to click on members of my Team. Was taken to the splash page each time. If I clicked on someone's name (e.g. in my Upcoming Events section, clicking on the event coordinator name), it worked and took me to that person's page. (Eva)~~
  * ~~According to my profile, I am not coordinating any events. Although, I have coordinated two past events and one upcoming event. (Mellicia, MacOS1010.6.1)~~
  * ~~Profile page says I have 4 upcoming events (under the Information bar). Under the Upcoming Events bar, I can view 2 of them as usual, but it includes an event from the past. Then I click on "View all" upcoming events, and it only shows one event. I know for a fact that I am signed up for 3 future events and am coordinating 1 additional event in the future. (Eva, FF3.5.5, Mac0S 10.6.2)~~
  * ~~I went to a past event. Clicked button that "I attended this event." Did this for 2 past events. Went back to profile page, and my profile still says "Volunteered at  0 event(s)." However, my Upcoming Events on profile page lists one of the past events from 8/22/2009 as an upcoming event. (Eva, FF3.5.5, Mac0S 10.6.2)~~
  * ~~I organized an event, it passed, and I got a receipt to verify volunteer hours. I clicked the link in the email to do so on the event page. I entered hours, but when I clicked "submit," the next screen never loaded (got a white page). (Eva, FF3.5.5.)~~
    * ~~Went back to a past event I coordinated. It lets me enter the # of hours that my volunteers (Brad, me) attended. If I enter whole numbers (2, 7), it works. If I enter by the half hour (1.5, 2.5), it goes to a white screen that doesn't load, instead of loading/submitting the change and returning to the Event page. (Eva, FF 3.5.5, Mac OS 10.6.2)~~
  * ~~on an event page, the RSS link sentences and drop-down run into the right-hand column and are cut off. A red box appeared that says "Checking input..." (Eva, FF3.5.5 MacOS10.6.2)~~
  * ~~bad redirects, no page-level reload on session timeout~~
  * ~~are past events updated as past?~~
  * ~~reporting hours as coordinator is broke wrt redirects; need to implement ajax post~~
  * ~~event searches do not filter by neighborhood/IC~~
  * ~~person search not returning everyone (or at least not paginating, or maybe just returning friends)~~


### browser specific ###

#### IE 6 ####

  * ~~logged in avatar/logout area of header is off~~
  * ~~transparent png logo is not rendered as transparent~~
  * ~~some sort of '/1' is floating around on the neighborhoods page~~
  * ~~bottom of button on event search is cut off~~
  * ~~layouts on some pages are not splitting properly~~
  * page title border not appearing
  * on homepage, tips for getting started section is misaligned
  * zindex for paginated dialog box not high enough (or not being respected)
  * ~~ie6 flat out crashes when navigate to the create event page~~


#### IE7 ####
  * Searched for events on my profile page, the search results came up, and the bottom of the search results window was below the bottom of my screen (this was on my laptop). I tried to move the window up by dragging from the bar at the top of the window and it wouldn't move.
    * I cannot replicate this problem...
  * ~~Internet Explorer 7, Windows Vista. When I turned off Disable Script Debugging in IE, I got the error "Line 1. Error: Unexpected call to method or property access." for every page on the site.~~
    * ~~this is generally fixed except:~~
      * ~~"Expected identifier, string or number (http://www.development.flashvolunteer.org/,385955909)" on login page~~
  * ~~Search buttons work, tabs (i.e. "Profile", Neighborhoods", etc.) work, but all other clickable links (including event titles) don't take you anywhere (Brad, IE7, Windows XP)~~
  * ~~Mailbox doesn't show any messages and when you click on Inbox, it sends you back to the homepage (Brad, IE7, Windows XP)~~
  * ~~Internal messaging does not work (Brad, IE7, Windows XP)~~
  * ~~Create event link doesn't take you anywhere (Brad, IE7, Windows XP)~~
  * ~~event validation does not work (Travis, IE7)~~
  * ~~google maps iframe does not work (Travis, IE7)~~
  * ~~event photos unaligned on event page (Travis, IE7)~~
  * ~~radio buttons on log hours are checked for both "did not attend" and "?" for event coordinators (Travis, IE7)~~
  * ~~overflow on dialog boxes are not handled properly (IE7, Travis)~~

#### IE 8 ####

  * ~~the bug about button padding that justin noted with safari appears to also be a problem in IE8~~

#### Safari ####

  * ~~UI bug -- Actual: On the Profile page, there's no padding on the background of the Search button, so it is colliding with the text. Looks fine in FF 3.0.11 because the buttons are rectangular and larger than a standard button, but Safari is rendering a normal-sized button with the larger text. Expected: the Safari button should render with the same padding as in Firefox (Justin, Safari 4.0.4, Mac OS X 10.6.2)~~



### not critical ###

These are things that would be nice to fix, but could wait until next version.
  * ~~generated email still giving appspot address~~
  * ~~event name is not loaded as title on event page (seen by Travis on MacOS 1.6, Firefox 3.5)~~
  * ~~basic search for volunteers (without any names or neighborhoods specified) doesn't return any results (Brad, Firefox 3.5.5 MacOS 10.6.2)~~
  * ~~remove hyperlinks from partner logos on Partner page (Brad, Firefox 3.5.5 MacOS 10.6.2)~~
  * ~~On People page, I left the field blank to search for everyone. Page dimmed, but no results appeared w/ everyone. (Eva, FF3.5.5 MacOS10.6.2).~~
  * ~~Facebook button from an event page takes me to facebook, but to a page called "My friends Links." Doesn't prompt me to post any update.  (Eva, FF3.5.5 MacOS10.6.2)~~
  * ~~When creating an event, I don't know what H1, H2, H3, H4, etc. are. (Eva)~~
  * ~~Profile page, far right column has two different types of Search buttons~~large rectangle (Find an Event) and small round (Find a Volunteer).~~
  * ~~Went to "people" selected Brad. His profile has no photo. However, he has a photo as the event organizer. Perhaps this is a security precaution? Mellicia, (MacOS1010.6.1)~~
  * ~~Went to a past event. Clicked "I attended this event." Pop-up text says (something like) "You are now signed up for (the event)!" Would be nice if it says that "Thanks for volunteering at this event!" or "You attended XYZ event!" (Eva)~~
  * ~~Tried to upload a photo to my profile that was too big. There was nothing indicating it didn't upload. Perhaps an error message? (Mellicia, MacOS1010.6.1)~~
  * ~~google maps error seems to be back (seen by Travis on MacOS 1.6, Firefox 3.5)~~
  * ~~add a little space between "Accept ToS" and "Create Account" button  (Brad, Firefox 3.5.5 MacOS 10.6.2)~~
  * ~~On an event's page, the light gray boxes around the Forum messages extend too far to the right (they go past the dark gray Forum title bar.). (Eva, FF 3.5.5, MacOS 10.6.2)~~
  * ~~On others' profile pages, the ">>Remove from team" and ">>Send message" are not quite lined up. (Eva, FF3.5.5)~~
  * ~~On my Profile page at the bottom, the "Why am I not coordinating any upcoming events?" sentence is a little tooo close to the bottom gray line. (Eva, FF 3.5.5)~~
  * ~~On my profile page, I clicked "View all" under Recommended Events. It dimmed and then came back to the same page. I'm assuming it's because there aren't any, but was't sure. Maybe it could pop up that window but say "We don't see any events that match your interest categories. Try checking around in some other categories!") (Eva)~~
  * ~~UI bug -- Actual: On any Neigborhood Detail page, the text link ">>Post new message" under the Forum section has no space between the arrows and "Post". Expected: there should be a space between the arrows and "Post" to be consistent with other similar text links on the site (Justin, Safari 4.0.4, Mac OS X 10.6.2)~~
  * ~~UI suggestion -- On the Profile page, make the color of the first (leftmost) metrics box #e2e2e2, the second box #c0e7b3, the third box #b2dce0, and the fourth (rightmost) box #c4c4c4 (Justin, Safari 4.0.4, Mac OS X 10.6.2)~~
  * ~~UI suggestion -- On the Profile page, add tooltips or alt text on rollover that identifies each of the metrics boxes. As it is now, I don't really understand what those four zeroes mean (Justin, Safari 4.0.4, Mac OS X 10.6.2)~~
    * ~~they actually already have titles, and they're clickable; but the tooltip does need to show up immediately~~
  * ~~UI suggestion -- The black 1px horizontal line at the top of the green navigation bar in the header should be removed or set to #3b3b3b (Justin, Safari 4.0.4, Mac OS X 10.6.2)~~
  * ~~Would be nice if the time could be changed to standard vs. military time in the Forum. (Sara FF3.0.5, Mac OS X 10.5.8)~~
  * ~~login page not intuitive (cosmetic)~~
    * ~~simplify by splitting the create account & login pages (even though the content will be very similar)~~
  * ~~When I clicked to get a receipt for Eva's homework event, I got the following text on a new page: "Saturday, 05 December 2009 has not yet certified that you attended the event." No contact info, no name, just that. Either we should let me add my own hours or have an email link where I can prompt Eva to certify me. (Brad, Firefox 3.5.5 MacOS 10.6.2)~~
  * ~~On my profile page, I have 0 hours and 0 events attended with 3 events created (two past). Should the hours/attendance be automatically logged? It sounds like I should get an email to log them, but I haven't received anything. (Mellicia, MacOS1010.6.1)~~
  * ~~LOVE the log hours feature! I noticed it now rounds down to the nearest integer after I submit a decimal. Can the text say "round to the nearest hour" or something like that? (Eva)~~
  * ~~Also when logging hours, it would be nice to have a confirmation popup. It wasn't immediately clear to me that the hours I reported were entered, until I search around and saw that the text at the top of that box had changed. (Eva)~~
  * ~~I got an email after my event was completed asking me to log the hours of attendees. I entered the hours and hit submit. The page didn't noticably change. I hit submit again. Nothing. I clicked to view receipt and confirmed that the system recognized the hours. It would be great to see some response/change after submitting. (Mellicia, Windows XP)~~
  * ~~Team links (lower screen right) broken on Volunteer profile pages (Hayden, OSX)~~
  * I RSVP'd for a test event, as prompted by the email I received in advance of the event. When I clicked on the link in the email, it took me to the FV home page after logging in. Would be nice if it took me either (a) to the event page that I need to RSVP for, or (b) directly to a message window to send to the organizer. Option A is probably best, as I can see the overall event details (I might have forgotten). (Eva)