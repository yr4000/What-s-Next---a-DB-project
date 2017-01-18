/**
 * Created by Alonmeytal on 24/12/2016.
 */

function initMap() {
    // Create a map object and specify the DOM element for display.
    map = new google.maps.Map(document.getElementById('map'), {
        center: DEFAULT_MAP_CENTER,
        scrollwheel: true,
        draggable: true,
        zoom: enumZoomLevels.Districts,
        minZoom: enumZoomLevels.City,
        maxZoom: enumZoomLevels.Buildings,
        scaleControl: true,
        streetViewControl: false,
        mapTypeControl: false,
        clickableIcons: false,
        backgroundColor: "#2B2B2B",
        styles: mapStyle
    });

    // Place a green marker on the last place click by the user.
    google.maps.event.addListener(map, "click", function (event) {
        lastSearch = enumSearchTypes.Marker;
        markForSearch = true;

        var position = new google.maps.LatLng(event.latLng.lat(), event.latLng.lng());
        if (lastMapClickLocation)
            removeMarker(lastMapClickLocation);

        lastMapClickLocation = createMarker(position, "Clicked here", "-1", true, enumMarkerColors.Current, 0);
    });

    // init bounds of the desired area
    var allowedBounds = new google.maps.LatLngBounds(
        // TODO: get the most accurate boundaries
        new google.maps.LatLng(51.2813, -0.6174), // bottom left boundary
        new google.maps.LatLng(51.7556, 0.3331) // top right boundary
    );
    // init last valid center in the map
    var lastValidCenter = map.getCenter();

    // listener that allows smooth panning, while constricting to London boundaries
    google.maps.event.addListener(map, 'center_changed', function() {
        if (allowedBounds.contains(map.getCenter())) {
            // still within valid bounds - save last valid position
            lastValidCenter = map.getCenter();
            return;
        }
        console.log("out of bounds: " +  map.getCenter());
        // not valid anymore - return to last valid position
        map.panTo(lastValidCenter);
    });

}

function createMarker(LatLong, title, place_id, center, color, index) {
    if (markForSearch && (lastSearch == enumSearchTypes.Marker)) {
        map.panTo(LatLong); // Center around marker.
        searchAroundMarker(LatLong.lat(),LatLong.lng());
        //TODO: for test, delete when done
        //ImFeelingLucky(LatLong.lat(),LatLong.lng());
        markForSearch = false;
    }
    if (center) {
        map.panTo(LatLong);
    }
    var m = new google.maps.Marker({
        position: LatLong,
        map: map,
        icon: iconFolderPath + color + String.fromCharCode((index % 26) + 65) + ".png",
        title:title,
        place_id: place_id
    });

    m.addListener("click", function() {
        map.panTo(LatLong);
        getPlaceDetails(place_id, index);
    });

    return m;
}

function addMarker(LatLong, title, place_id, center, color, index) {
    markersArray.push(createMarker(LatLong, title, place_id, center, color, index));
}

//TODO: got this error message once: Uncaught TypeError: marker.setMap is not a function
function removeMarker(marker) {
    marker.setMap(null);
}

function clearArray(arr) {
    while (arr.length != 0) {
        removeMarker(arr.pop());
    }
}

/*after a marker is chosen all the markers except him
  will be removed of the map using this function.
  #TODO: it doesn't work right now because i coudn't figure how to work with indexes....
 */
function removeAllMarkersExceptChosenOne(anakin) {
    console.log("start chosen one")
    for(i=0;i++;i<markersArray.length){
        if(anakin.place_id == markersArray[i]){
            continue;
        }
        console.log(markersArray[i].title);
        removeMarker(markersArray[i]);
    }
    console.log("end chosen one")
}
