# Introduction #

CSS is notoriously difficult to manage -- it quickly grows into an unorganized jumble without being explicitly maintained.

This page describes how the FV CSS is organized (and how you should maintain it when changing it).

# Details #

At a high level, the CSS is broken down in an aspect-oriented fashion (e.g. everything changing a color goes together, everything dealing with layout goes in another place). The css can be found at /stylesheets/css, and is split across a few files.

The CSS sections are:
  * ` [colors_backgrounds_borders.css] ` Everything having to do with colors, backgrounds, and borders
  * ` [layout.css] ` Site structure. All of the ID'd container elements, indented to reflect the current layout
  * ` [main.css] ` Basic site styles (e.g. html/body, .fl {float:left})
  * ` [main.css] ` Navigation (navigation tabs, footer navigation)
  * ` [main.css] ` Headers (e.g. h3)
  * ` [main.css] ` Lists (e.g. ul, li)
  * ` [main.css] ` Links (e.g. a)
  * ` [main.css] ` Images (img)
  * ` [main.css] ` Forms (e.g. input)
  * ` [main.css] ` Tables (e.g. th)
  * ` [main.css] ` Misc. (whatever doesn't fit anywhere else)
  * ` [main.css] ` Unorganized (sometimes it gets late and you don't want to organize some new css, or you are experimented. Put all such CSS here and it can be integrated into the scheme later)

There are a couple of exceptions to this aspect oriented scheme. There are a couple of instances where very particular CSS is needed for small parts of the site. The CSS related to these have been put into separate files. They include:
  * ` [create_event.css] ` The css relating to the create event form
  * ` [event_photos.css] ` The css relating to adding/viewing event photos