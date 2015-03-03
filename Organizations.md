#Design for adding organizations to flashvolunteer.

# Introduction #

Design and implementation notes for opening up event creation and adding organizations as entities into the system. Adding organizations to FlashVolunteer will allow organizations to host events. Volunteers will also be able to create events, but the events will be unverified by default until checked by a FV admin.

# Scenarios of use #

### Bright side ###

  1. Brad, who works for Denise Louie, has just arrived at FlashVolunteer & wants to create an account and an event on behalf of Denise Louie.
    1. Denise Louie is already an organization in FV
      1. none of the current FV members of Denise Louie are active **(Brad needs to contact info@fv to explain the situation that the organization username/password information for the Denise Louie FV account is lost)**
      1. there are FV members who coordinate for Denise Louie **(Brad needs to obtain the username/password info from them to login as Denise Louie)**
    1. Denise Louie does not yet exist in the system **(On the splash screen, Brad clicks "create organization account" and fills out the info for Denise Louie. When he visits the create event page, he can create unverified events, until Denise Louie is marked as a "verified" organization by FV admins)**
  1. Mark wants to host an event for cleaning up Ravenna Park. His neighbors, Sally & Vivek, also would like to help coordinate. **(Mark navigates to the create event page and fills out the information. If Sally and Vivek are on flash volunteer, he is able to click "add additional event hosts" and select them. They receive an email that they are now full co-owners of the event.)**
  1. Sandy & Brad are co-coordinating an event on behalf of Denise Louie and United Way. Sandy has created the event. Brad wants to be listed as event coordinator on FV, as well as having some control over the event. **(Sandy, logged in as Denise Louie, needs to go to the event page and click "add additional event hosts", selecting Denise Louie)**

### Dark side ###

  1. Andy is a member of Anonymous and wants to mess with the Church of Scientology by creating fake events on behalf of the Church of Scientology.
    1. The Church of Scientology already exists as an organization in the system **(Andy doesn't know the username/password, so he cannot accomplish his goal)**
    1. It is not an org in the system. Andy creates an organization for the Church of Scientology, with FV information indicating that he is Tom Cruise. **(the organization will be created, but when a FV admin tries to verify the account, the email address will not be on an organization's domain. With gmail-only account logins, this could be more difficult to defend against)**
  1. Larry is a predator looking to meet cute girls, and thinks that he can create appealing looking events to lure people out in hopes of getting a target **(we don't have any protection against this. We'll just have to use language suggesting that individuals volunteer in groups for events created by unknown individuals)**.
  1. Hal creates an offensive event (or changes the existing event to be offensive) **(the event is immediately added to the system as unverified. when an FV admin sees it, they will delete it. unverified events will also allow users to flag an event as offensive, quickening the attention to the matter)**


# Definitions #

  * Verified Organization - a verified organization is an organization who's existence has been verified by a FlashVolunteer admin.
  * Verfied OrganizationVolunteer - not relevant anymore!
  * Sponsored - a sponsored event is associated with one or more organizations (not necessarily verified). This distinction is less important now.
  * Verified Event - a verified event is one that has been cleared with a flash volunteer admin, **or** has been created on behalf of a verified organization


# Interaction design #

## nav changes ##

  * Add an Organizations navigation tab
  * Remove "Create Event" tab -- add create event button to the Events page

## new pages / views ##

  * Event: adding new coordinator to an event
    * select a coordinator (any FVer -- individual or organization)
    * fill out a message
    * "add as coordinator" sends email to that volunteer
    * that volunteer immediately gains full rights to change the event, including deletion
    * this can only be done for verified events, to prevent legitimate users from getting spam from pranksters creating fake events (v3)
  * Organization: organizations page
    * lists organizations
    * find an organization (v3)
    * competition stats -- similar (or exactly) to what will be on neighborhoods page (v3)
  * Organization: create / edit organization
    * fields: name, logo, url, description
    * orgs need to be verified, but can start hosting events immediately
  * Organization: organization page
    * people can become "fans" of organizations to receive events recommendations (v3)
    * people can request to become a coordinator of events for the organization
  * Organization: requesting to become a coordinator for an organization

## changes to existing views ##
  * Splash screen
    * create an account as an organization or as an individual
  * Events: create/edit event
    * add an event coordinators field. the event creator is automatically a coordinator. allow the creator to add another coordinator.
  * Events: event page
    * show hosted by fields
    * if an event is not yet verified:
      * set some text at top like (! This event has yet to be checked)
      * add flag event as offensive (mailto:)
    * Volunteers list should show the currently logged in user if they have volunteered
  * Events: events page
    * unverified events get a (?). mouseover the question mark explains that this event has yet to be checked by a FV admin
    * add an "events I'm hosting" section
    * add a drop down to the search interface for organizations (v3)
    * add the "create event" button prominently

# Backend #

## New Models ##

  * **organization** - an _organization_ models a real world organization.  It will have an id, name, logo, description, and a flag denoting if the organization has been verified.
  * **organizationvolunteer** - we do NOT need this anymore. whew!
  * **eventorganization** - a relational object for representing the many-to-many relationship between organizations and events, allowing for organizations to (stop) collaborate (and listen).  Each _eventorganization_ will hold a reference to one _event_ and one _organization_.

## Changes to existing models ##
  * add a verified flag to _event_, to denote that the event has been verified.
  * There is no flag for events being sponsored. Instead, the verified flag for an event will default to true if the event is hosted by at least one verified organization.

## Controller changes (not complete) ##

  * organization event hosts should NOT be automatically added as volunteers

## Migrating the datastore ##
We will need to migrate the data in the current datastore for the live site to accommodate the new information.  This design creates little need for migration, as only events are being modified.  The events can be all set to verified initially.

## things to figure out ##

  * creating/sending emails w/o mailto
  * datastore migration