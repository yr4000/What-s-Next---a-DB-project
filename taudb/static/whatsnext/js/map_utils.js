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
        if (lastSearch == enumSearchTypes.FullText)
            lastSearch = enumSearchTypes.Marker;
        markForSearch = true;

        var position = new google.maps.LatLng(event.latLng.lat(), event.latLng.lng());
        if (lastMapClickLocation)
            removeMarker(lastMapClickLocation);

        lastMapClickLocation = createMarker(position, "Clicked here", "-1", true, enumMarkerColors.current, 0);
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
    if (markForSearch) {
        if (lastSearch == enumSearchTypes.Marker) {
            map.panTo(LatLong); // Center around marker.
            requestPage = 0;
            resultsPage = 0;
            searchAroundMarker(LatLong.lat(),LatLong.lng());
            markForSearch = false;
        } else if (lastSearch == enumSearchTypes.FeelingLucky) {
            map.panTo(LatLong);
            requestPage = 0;
            resultsPage = 0;
            ImFeelingLucky(LatLong.lat(),LatLong.lng());
            markForSearch = false;
        }
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
    
    // Clear directions rendering if available.
    if (directionsDisplay)
        directionsDisplay.setMap(null);
}

function showRouteOnMap(locationsArr) {
     // TODO: Alon M, this is a temporary arr just for POC, so just pass an array of LatLng objects to the function
    /*
    locationsArr = [new google.maps.LatLng(51.668403, -0.176567),
        new google.maps.LatLng(51.398291, -0.049449),
        new google.maps.LatLng(51.566181, 0.111744)];
    */
    // function requires at least 2 locations (otherwise can't show a route on the map)
    if (locationsArr.length < 2) {
        return;
    }

    directionsService = new google.maps.DirectionsService();
    directionsDisplay = new google.maps.DirectionsRenderer({suppressMarkers:true});
    directionsDisplay.setMap(map);

    removeMarker(lastMapClickLocation);

    // set the waypoints for the route only if there are any (at least 3 locations)
    var waypoints = [];
    if (locationsArr.length >= 3) {
        for (var i = 1; i < locationsArr.length - 1; i++) {
            waypoints.push({
                location: locationsArr[i],
                stopover: true
            });
        }
    }

    //  the Google Directions API request
    var request = {
        origin: locationsArr[0],
        destination: locationsArr[locationsArr.length - 1],
        waypoints: waypoints,
        travelMode: google.maps.DirectionsTravelMode.DRIVING // TODO: if we have time, ask user input for travel mode
    };

    // send the request and handle the response - show the route on map
    directionsService.route(request, function (response, status) {
        if (status == google.maps.DirectionsStatus.OK) {
            directionsDisplay.setDirections(response);
        }
    });
}