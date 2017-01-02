/**
 * Created by Alonmeytal on 24/12/2016.
 */
$(document).ready(function () {
    $("#start-hotel").click(function(event) {
        console.log("h");
        $("#start-restaruant").show();
        $("#search-restaurant").hide();
        $("#start-hotel").hide();
        $("#search-hotel").show();
    });
    $("#start-restaruant").click(function(event) {
        console.log("r");
        $("#start-hotel").show();
        $("#search-hotel").hide();
        $("#start-restaruant").hide();
        $("#search-restaurant").show();
    });
});

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