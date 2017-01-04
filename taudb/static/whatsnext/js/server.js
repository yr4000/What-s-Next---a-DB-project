/**
 * Created by Alonmeytal on 02/01/2017.
 */

// Send CSRF cookie with every non-safe method
function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
    		var csrftoken = $.cookie('csrftoken');
            xhr.setRequestHeader("X-CSRFToken", csrftoken);
        }
    }
});

function getHotels() {
    var url = "/hotels/";

    $.getJSON(url,
        "",
        function(response)
        {
            console.log(response);
            for (var key in response) {
                var hotel = response[key];
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
function searchByFullText(word,category) {
    var url = "/fullTextSearch/";

    var search_values = {
        word: word,
        category: category
    };

    $.post(url,
        JSON.stringify(search_values),
        function(response)
        {
            console.log(response);
            for (var key in response) {
                var place = response[key];
                console.log(place);
                addMarker(new google.maps.LatLng(place.latitude, place.longitude), place["name"]);
            }
        },
        'json')
    .fail(function(jgXHR, textStatus, errorThrown) {
         console.log("Failed to run full text search");
    });
}