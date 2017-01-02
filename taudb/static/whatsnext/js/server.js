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