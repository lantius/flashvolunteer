# Introduction #

Using V3 to stay away from keys


# Details #

Here's an example of sticking a bit of HTML on a rendered point:


` <script src="http://maps.google.com/maps?file=api&amp;v=2.73&amp;key=ABQIAAAA-O3cOm9OcvXMOJXreXHAxSsTL4WIgxhMZ0ZK_kHjwHeQuOD4xSbZqVZW2U_OWOxMp3YPfZl2GavQ" type="text/javascript"></script>  `
> `     <script type="text/javascript"><!-- `
> `     jQuery(function() { `
> > `      if (GBrowserIsCompatible()) { `
> > > `       var map = new GMap2(document.getElementById('map_canvas')); `
> > > > `      var marker = new GMarker(new GLatLng(37.4228, -122.085)); `

> > `        var html = '<div style="width:210px; padding-right:10px;">'+ `
> > `           '<a href="signup.html">Sign up</a> for a Google Maps API key'+ `
> > `           ', or <a href="documentation/index.html">read more about the'+ `
> > `           ' V2 API</a>.<br /><br /> Looking for the new '+ `
> > `           '<a href="/apis/maps/documentation/v3/">V3 API</a>?</div>'; `
`   `
`          map.setCenter(new GLatLng(37.4328, -122.077), 13); `

> `         map.addControl(new GSmallMapControl()); `
> `         map.addOverlay(marker); `
> `         marker.openInfoWindowHtml(html); `
> `       } `
`     }); `
`     //--></script>  `