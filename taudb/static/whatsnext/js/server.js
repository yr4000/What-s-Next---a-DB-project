/**
 * Created by Alonmeytal on 02/01/2017.
 */

function getHotels() {
    var url = "/hotels/";

    $.getJSON(url,
        "",
        function(response)
        {
            console.log(response);
            for (var key in response) {
                hotel = response[key];
                console.log(hotel);
                addMarker(new google.maps.LatLng(hotel.latitude, hotel.longitude), hotel["name"]);
            }
        },
        'json')
    .fail(function(jgXHR, textStatus, errorThrown) {
         console.log("Failed to fetch Hotels");
    });
}

/**
 * Created by DrorBrunman on 04/01/2017.
 */
function full_text_search() {
    var url = "/textSearch/";

    $.getJSON(url,
        "",
        function(response)
        {
            console.log(response);
            for (var key in response) {
                place = response[key];
                console.log(place);
                addMarker(new google.maps.LatLng(place.latitude, place.longitude), place["name"]);
            }
        },
        'json')
    .fail(function(jgXHR, textStatus, errorThrown) {
         console.log("Failed to run full text search");
    });
}