/**
 * Created by Alonmeytal on 24/12/2016.
 */

function initMap() {
    // Create a map object and specify the DOM element for display.
    map = new google.maps.Map(document.getElementById('map'), {
        center: DEFAULT_MAP_CENTER,
        scrollwheel: false,
        draggable: false,
        zoom: enumZoomLevels.City,
        styles: {
            featureType: "poi",
            stylers: [{ visibility: "off" }]
        }
    });
    // Place a green marker on the last place click by the user.
    google.maps.event.addListener(map, "click", function (event) {
        var position = new google.maps.LatLng(event.latLng.lat(), event.latLng.lng());
        //console.log( latitude + ', ' + longitude );
        if (lastMapClickLocation) {
            removeMarker(lastMapClickLocation);
        }
        lastMapClickLocation = createMarker(position, "Clicked here", false, enumMarkerColors.Current);
    });
}

function createMarker(LatLang, title, center, color) {
    if (center) {
        map.setCenter(LatLang);
    }
    var m = new google.maps.Marker({
        position: LatLang,
        map: map,
        title:title
    });

    return m;
}

function addMarker(LatLang, title, center, color) {
    markersArray.push(createMarker(LatLang, title, center, color));
}

function removeMarker(marker) {
    marker.setMap(null);
}

function clearMarkers() {
    for (var i = 0; i <= markersArray.length; i++) {
        removeMarker(markersArray.pop());
    }
}