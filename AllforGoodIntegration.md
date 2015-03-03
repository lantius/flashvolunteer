

Goal: Pull down and list relevant volunteer opportunities on Flash Volunteer that are aggregated on [All for Good](http://www.allforgood.org/) (AfG).

All for Good aggregates events listed on a number of provider sites such as Volunteer Match, United Way, and Meetup (for example, it lists [this event](http://www.volunteersolutions.org/uwkc/org/opp/10336400933.html#610e94a6dd48e11a4ef88cf8408b45ff)). The quality and relevance of the listed opportunities vary widely. We want to pull down and list relevant volunteer opportunities on FV to increase our event supply.

I have created a first implementation of this project that can be extended in a number of directions.

The approach is as follows:
  1. Access and publish AfG opportunities as FV events. We have an administrator All for Good interface defined as a controller in 'controllers.admin.afg\_interface' and can be accessed at '/admin/afg\_interface'.
    1. The AfG API is accessed at '/admin/afg\_interface/rebuild, and is controlled by 'controllers.admin.afg\_interface.rebuild'. It is also linked to at '/admin/afg\_interface'. In this process, a query for 50 seattle-area volunteer opportunities is issued. Each of these opportunities is then scored based on some criteria for their suitability to be listed. Every opportunity is then saved to the datastore as a 'models.afg\_opportunity'.
    1. The opportunities can now be manually culled through the admin interface at '/admin/afg\_interface'. Every 'afg\_opportunity' which has not previously been evaluated is listed. Each opportunity has the option to "publish to FV" or "dismiss". If you click "dismiss", the afg\_opportunity is marked as unsuitable for FV and will be removed from the list. If you click "publish to FV", a familiar create event form will be populated with the information from the opportunity. When you go to "create" or "publish", the event will now be listed on FV.
  1. Display and user interaction with posted AfG opportunities.
    1. A number of things need to change for users interacting with AfG opportunities...

# Using the All for Good API #

Our AfG API key is **flashvolunteer**. There are a number of different queries with various options available through the [AfG API](http://www.allforgood.org/docs/api.html).

Here are some sample queries:
  * http://www.allforgood.org/api/volopps?vol_loc=Seattle,WA&output=json&key=flashvolunteer
  * http://www.allforgood.org/api/volopps?q=park&vol_loc=47.625021,-122.3139948&output=json&num=50&key=flashvolunteer

This is an example returned volunteer opportunity:
```
  {
   "startDate": "2010-01-16 10:00:00", 
   "minAge": "", 
   "endDate": "2010-01-16 14:00:00", 
   "contactPhone": "", 
   "quality_score": 0.1, 
   "detailUrl": "", 
   "sponsoringOrganizationName": "King Conservation District", 
   "latlong": "47.6062095,-122.3320708", 
   "contactName": "", 
   "addr1": "", 
   "impressions": 0, 
   "id": "b9b153dff144978addb65b8c0339832f", 
   "city": "", 
   "location_name": "Seattle, WA", 
   "openEnded": "", 
   "pubDate": "", 
   "title": "Urban Forest & Salmon Restoration - Longfellow Creek, Jan 16", 
   "base_url": "b9b153dff144978addb65b8c0339832f", 
   "virtual": "", 
   "provider": "volunteermatch", 
   "postalCode": "", 
   "groupid": "Mfd116a26f4f9243fe8d33a31722cbde8", 
   "audienceAge": "", 
   "audienceAll": "", 
   "description": "Join the King Conservation District and Green Seattle Partnership to help restore riparian habitat on Longfellow Creek in West Seattle. Longfellow Creek is one of only four salmon streams in Seattle. Come join our ongoing environmental reststoration efforts to replace invasive ivy and blackberry wit", 
   "street1": "", 
   "street2": "", 
   "interest_count": 0, 
   "xml_url": "http:\/\/www.volunteermatch.org\/search\/opp618502.jsp#b9b153dff144978addb65b8c0339832f", 
   "audienceSexRestricted": "", 
   "startTime": 1000, 
   "contactNoneNeeded": "", 
   "categories": [
    "Poverty"
   ], 
   "contactEmail": "volunteer@kingcd.org", 
   "skills": "", 
   "country": "", 
   "region": "", 
   "url_short": "www.volunteermatch.org", 
   "addrname1": "", 
   "endTime": 1400
  }
```


# Mapping an AfG opportunity into an FV event #



## Task: Getting candidate All for Good opportunities ##

**Task**: Build a list of candidate All for Good opportunities for the Seattle region and store them in the datastore.

**Who?**: Travis (its done)

Create a method that accesses the All for Good API. A good query would be: http://www.allforgood.org/api/volopps?vol_loc=Seattle,WA&output=json&key=flashvolunteer&num=50. That pulls down 50 (or fewer) seattle-area opportunities.

The method will iterate over each opportunity and store the opportunity in the datastore.

Note that it must check to see if the opportunity has already been pulled down before. The "id" field of the returned AfG opportunity should be used to perform this check.

We will store ALL AfG opportunities that come through the system. They will be stored in the datastore in a table called **AFGOpportunity**. I have created the draft of models.afg\_opportunity. It has the following schema:
  * id : internal unique ID
  * fv\_event: ReferenceProperty on Event; defaults to None, but set to a published Event later on
  * status: Boolean; defaults to None; set to True or False later on when someone/something determines if the opportunity should be published on FV
  * score: Integer; set later as an indicator of how suitable for FV this opportunity is
  * afg\_id: String; the ID returned by AfG
  * title: String; title returned by AfG
  * startDate: DateTime; startDate returned by AfG
  * endDate: DateTime; startDate returned by AfG
  * provider: String; provider returned by AfG
  * description: String; description returned by AfG
  * contactEmail: String; contactEmail returned by AfG
  * skills: String; skills returned by AfG
  * xml\_url: STring; xml\_url returned by AfG

The code is at controllers.admin.afg\_interface, it has been added to controllers.admin.route, and it can be accessed at /admin/access\_all\_for\_good


### Future work ###
  * this method should be run as a daily chron job.
  * A method should query the AfG API for each AfG-harvested event that is published on FV and make sure that all of the information is up-to-date. This should be run as a daily chron job.

## Task: Score the opportunities ##

**Task**: Score an All for Good opportunity to help evaluate which if it is suitable for being listed on FV.

**Who?**: Travis (its done).

My recommendation for approaching this task is to return a score indicating an opportunities's suitability based on some straightforward heuristics.

Here is a sample scoring rubric for each opportunity:

+1 for coming from a high-quality provider (i.e United Way (Volunteer Solutions portal), Seattle Works (Hands On Network)

+2 for a complete, valid address

+2 for date range < 1 day; +1 for date range < 1 week

+1 for non-empty description

+1 for contact email

Some notes
  * the "location\_name" field is the address field
  * the "startDate" and "endDate" each have the date and time

## Task: Identifying a neighborhood given an address ##

**Task**: Given an address, return an Application and a Neighborhood (or return False for unfound)

**Steps**: To accomplish this task, the address needs to be geocoded, mapped to an FV Application, and then mapped to a Neighborhood. These steps are described below.

**Who?**: Travis has done the first parts. Who wants to do the advanced Zillow or GeoAPI coupling?

### Geocode the address ###

The first step to any solution is to map an address into a lat/lon coordinate (geocode it). The code for doing this is in 'controllers._utils.geocode'._

### Determine the application region of the opportunity ###

We have multiple application regions (e.g. Seattle, Pierce County, Los Angeles). Given an address, we need to identify which of these regions an opportunity falls into (and discard those that do not fall into any. (right now, we are hardcoded to SEattle area events)

Every application has a record in the Applications table. Each record contains a lat/lon that represents its lower left corner ('application.sw\_coord') and a lat/lon that represents its upper right corner ('application.ne\_coord'). This effectively defines bounding box for the region and can be used to determine whether an opportunity is within a region or not (in fact, that should just be made a method on an Application object).

If the address does not fall into any Application, return False to indicate that the opportunity does not fall into any FV application region.

### Map geocode to neighborhood ###

The second step is to take the lat/lon and map it to a neighborhood. Because neighborhoods are ill-defined and oddly shaped, it is difficult to get the right information for this mapping.

Right now, every Neighborhood record in the datastore has a centroid lat/lon ('neighborhood.centroid'). The centroid is the approximate middle of the neighborhood. We can use this value to make a straightforward calculation of the nearest-neighborhood for a given geocoded address. However, it will not be correct all the time, because of the strange shapes and varying sizes of neighborhoods.

This is done in 'controllers._utils.get\_neighborhood'._

#### Getting better neighborhood mapping ####

Though our first iteration doesn't require it, in the future, we can tie into [GeoAPI](http://docs.geoapi.com/Demos) which offers a place-based API for identifying neighborhoods and other geographic features. Our apikey for GeoAPI is **FsSr8pSlwp** and an example query is http://api.geoapi.com/v1/parents?lat=47.625021&lon=-122.313994&apikey=FsSr8pSlwp&pretty=1. One thing I'm concerned about is their terms of use, which includes a close association of their logo with any use of their API (see [here](http://docs.geoapi.com/Terms-Of-Use)).

Another option is to use the downloadable Zillow neighborhoods and just add those to our database. See [here](http://www.zillow.com/howto/api/neighborhood-boundaries.htm).

Both of these options will require mapping our existing neighborhoods into their neighborhoods, as they are not the same.

#### To do ####

  * application checking -- we don't check to make sure that an address falls within the current application's bounding region.
  * more advanced neighborhood mapping (probably lower priority given the shitiness of AfG opportunities)

## Publish an AfG opportunity as an FV event ##

**Task**: Create an admin page that shows each candidate AfG opportunity which has not yet been evaluated (i.e. 'afg\_opportunity.status==None'). For each candidate opportunity, link to the AfG event, show the opportunity's score, and have a "publish" and "dismiss" button. The publish button creates the FV event.

**Who?**: Travis has more or less done this. Its all in 'controllers.admin.afg\_interface'


### Creating the FV event ###

First, we need to modify the event model so that we can keep track of events which have been pulled from AfG:
  * add a source field, defaults to None, which is a reference property on AFGOpportunity
  * add an event\_url field (with target=_none in the view)
  * add a contact email field (in view, defaults to owner if its true)_

Second, we need to map fields from AFGOpportunity into an FV event:
  * AFGOpportunity.title => Event.name
  * AFGOpportunity.description => Event.description
  * AFGOpportunity.enddate => Event.enddate
  * AFGOpportunity.startdate => Event.date
  * AFGOpportunity.skills => Event.special\_instructions
  * AFGOpportunity.contact\_email => Event.contact\_email

Third, make sure to:
  * set Event.verified to True
  * set Event.source to the AFGOpportunity
  * make sure to get the full description
  * set Event.neighborhood based on a call to the method defined in the previous task

# Interacting with AfG events on the site #

  * modify event to show its source
  * what should the interaction be for AfG signup? "sign me up" is somewhat disingenuous now

# Problems to address #

  * a changing event
  * an event host might want to "claim" ownership of an event

# To do #
  * modify event to not require FV coordinator
  * modify event form to include an optional "event url" field