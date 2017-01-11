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
        styles: [
            {
                "elementType": "labels.icon",
                "stylers": [
                    {
                        "visibility": "off"
                    }
                ]
            },
            {
                "elementType": "geometry",
                "stylers": [
                    {
                        "color": "#ebe3cd"
                    }
                ]
            },
            {
                "elementType": "labels.text.fill",
                "stylers": [
                    {
                        "color": "#523735"
                    }
                ]
            },
            {
                "elementType": "labels.text.stroke",
                "stylers": [
                    {
                        "color": "#f5f1e6"
                    }
                ]
            },
            {
                "featureType": "administrative",
                "elementType": "geometry.stroke",
                "stylers": [
                    {
                        "color": "#c9b2a6"
                    }
                ]
            },
            {
                "featureType": "administrative.land_parcel",
                "elementType": "geometry.stroke",
                "stylers": [
                    {
                        "color": "#dcd2be"
                    }
                ]
            },
            {
                "featureType": "administrative.land_parcel",
                "elementType": "labels.text.fill",
                "stylers": [
                    {
                        "color": "#ae9e90"
                    }
                ]
            },
            {
                "featureType": "landscape.natural",
                "elementType": "geometry",
                "stylers": [
                    {
                        "color": "#dfd2ae"
                    }
                ]
            },
            {
                "featureType": "poi",
                "elementType": "geometry",
                "stylers": [
                    {
                        "color": "#dfd2ae"
                    }
                ]
            },
            {
                "featureType": "poi",
                "elementType": "labels.text.fill",
                "stylers": [
                    {
                        "color": "#93817c"
                    }
                ]
            },
            {
                "featureType": "poi.park",
                "elementType": "geometry.fill",
                "stylers": [
                    {
                        "color": "#a5b076"
                    }
                ]
            },
            {
                "featureType": "poi.park",
                "elementType": "labels.text.fill",
                "stylers": [
                    {
                        "color": "#447530"
                    }
                ]
            },
            {
                "featureType": "road",
                "elementType": "geometry",
                "stylers": [
                    {
                        "color": "#f5f1e6"
                    }
                ]
            },
            {
                "featureType": "road.arterial",
                "elementType": "geometry",
                "stylers": [
                    {
                        "color": "#fdfcf8"
                    }
                ]
            },
            {
                "featureType": "road.highway",
                "elementType": "geometry",
                "stylers": [
                    {
                        "color": "#f8c967"
                    }
                ]
            },
            {
                "featureType": "road.highway",
                "elementType": "geometry.stroke",
                "stylers": [
                    {
                        "color": "#e9bc62"
                    }
                ]
            },
            {
                "featureType": "road.highway.controlled_access",
                "elementType": "geometry",
                "stylers": [
                    {
                        "color": "#e98d58"
                    }
                ]
            },
            {
                "featureType": "road.highway.controlled_access",
                "elementType": "geometry.stroke",
                "stylers": [
                    {
                        "color": "#db8555"
                    }
                ]
            },
            {
                "featureType": "road.local",
                "elementType": "labels.text.fill",
                "stylers": [
                    {
                        "color": "#806b63"
                    }
                ]
            },
            {
                "featureType": "transit.line",
                "elementType": "geometry",
                "stylers": [
                    {
                        "color": "#dfd2ae"
                    }
                ]
            },
            {
                "featureType": "transit.line",
                "elementType": "labels.text.fill",
                "stylers": [
                    {
                        "color": "#8f7d77"
                    }
                ]
            },
            {
                "featureType": "transit.line",
                "elementType": "labels.text.stroke",
                "stylers": [
                    {
                        "color": "#ebe3cd"
                    }
                ]
            },
            {
                "featureType": "transit.station",
                "elementType": "geometry",
                "stylers": [
                    {
                        "color": "#dfd2ae"
                    }
                ]
            },
            {
                "featureType": "water",
                "elementType": "geometry.fill",
                "stylers": [
                    {
                        "color": "#b9d3c2"
                    }
                ]
            },
            {
                "featureType": "water",
                "elementType": "labels.text.fill",
                "stylers": [
                    {
                        "color": "#92998d"
                    }
                ]
            }
        ]
    });

    // Place a green marker on the last place click by the user.
    google.maps.event.addListener(map, "click", function (event) {
        var position = new google.maps.LatLng(event.latLng.lat(), event.latLng.lng());
        //console.log( latitude + ', ' + longitude );
        if (lastMapClickLocation) {
            removeMarker(lastMapClickLocation);
            markForSearch = true;
        }
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
    //console.log(markForSearch,isSearchByText); TODO: Alon, from some reason it doesnt recognize isSearchByText
    if ((markForSearch && !isSearchByText)) {
        map.panTo(LatLong); // Center around marker.
        //console.log((LatLong.lat()-51)*RESOLUTION,LatLong.lng()*RESOLUTION)
        searchAroundMarker(LatLong.lat(),LatLong.lng());
        markForSearch = false;
    }
    if (center) {
        map.panTo(LatLong);
    }
    var m = new google.maps.Marker({
        position: LatLong,
        map: map,
        icon: iconFolderPath + color + String.fromCharCode((index % 26) + 65) + ".png",
        title:title
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

function removeMarker(marker) {
    marker.setMap(null);
}

function clearMarkers() {
    while (markersArray.length != 0) {
        removeMarker(markersArray.pop());
    }
}
