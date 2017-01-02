/**
 * Created by Alonmeytal on 24/12/2016.
 */
$(document).ready(function () {
    openNav();
});

function openNav() {
    document.getElementById("myNav").style.height = "100%";
}

function closeNav() {
    document.getElementById("myNav").style.height = "0%";
}

function addLocationRow(location) {

}

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
