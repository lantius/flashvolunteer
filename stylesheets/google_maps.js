function showAddress(address) {
  if (GBrowserIsCompatible()) {
    var geocoder = new GClientGeocoder();

    var map = new GMap2(document.getElementById("map_canvas"));
    map.setUIToDefault();    
    geocoder.getLatLng(
      address,
      function(point) {
//        if (!point) {
//          alert(address + " not found");
//        } else {
        if (point) {
          map.setCenter(point, 13);
          var marker = new GMarker(point);
          map.addOverlay(marker);
        }
      }
    );
  }
}
