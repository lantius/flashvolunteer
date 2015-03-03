

# Implementation of full-text search #

## Introduction ##

The simple module provided by [Bill Katz](http://www.billkatz.com/2009/6/Simple-Full-Text-Search-for-App-Engine) was used, and adapted for usage in flashvolunteer.org.
The following classes are notable:
  * **` StemmedIndex `** is the model that contains the index. Rows consist of key that points back to what was indexed (Event), and ` ListProperty ` that contains phrases.
  * **` StemmedIndexEvent `** is derived from ` StemmedIndex ` - it contains the index for events
  * Event is now derived from **` SearchableEvent `** which is derived from **` Searchable `**.  This provides the index() and search() methods.

Instead of containing the search phrases property in the original model (Event), the approach uses a different model (see Relation Index). The reason is to avoid exploding indexes.
An exploding index will occur when a composite index is necessary.
A composite index would have to contain the ListProperties multiple times when searching for multiple words.
A composite index can be avoided by avoiding filtering for other properties, and avoiding search order.

## Search methodology ##


Please refer to comments in ` search_katz\search.py `

Currently, we have to run 2 separate queries - one for search terms ('search term query'), the other that filters for event properties ('filter query').
Since we cannot even order the search query without necessitating a composite (exploding) index, the 'search query' has to return all possible results.
We then manually intersect this query with results from the 'filter query'. We limit the filter query to 10 results at a time, intersect, check if we have enough results, rerun the query etc.

## Problems ##


Queries for Event properties combined with phrases are difficult, because they refer to different tables and GAE does not provide JOINs.
Even if we limit our query to a specific neighborhood, application etc., we still have to process all results returned from the search term query.

## Possible solutions ##


Make the StemmedIndexEvent finer grained, especially create different tables for different applications. This can be done easily now with namespaces.

## Administration UI ##


Before using full-text search, a search index must be created.
The main search administration page ` /admin/searchadmin ` can be accessed from ` /admin `.
Pressing the button will create an indexing task in the task queue (must be executed manually when running in debug server).

Creation of search index
` Event.put() ` also creates the search index entry

## Full-Text Search UI ##

The event page now contains a text box into which search terms can be entered. It is also possible to set the neighborhood, and perform all other filters.

## Code location ##

```
/search_katz	full-text search provided by Bill Katz, adapted
	Searchable calls the following functions
	Event.searchindex_getprop_func() provides data that should be indexed for full-text search

/controllers/events.py
	EventsPage.create()		trigger search index update
	EventsPage.update()		trigger search index update
	EventsPage.search()		perform search
	EventsPage.do_search()
/controllers/admin/route.py
					/admin/searchadmin routes into SearchAdmin
/models/event.py
					Event now derived from SearchableEvent

/stylesheets/css/main.css and fv.min.css
/stylesheets/css/

/stylesheets/javascript/fv.js and fv.min.js
					get_search_params() amended to include string from input box
	
/views/admin/index.html
/views/events/_find_event.html	
/views/events/events_search.html
```
