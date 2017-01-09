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

function searchAroundMarker(latitude, longitude) {
    var url = "/place/get_around_marker/";

    var search_values = {
        latitude: latitude,
        longitude: longitude,
        distance: searchDistance,
        category: searchCategory,
        limit: DEFAULT_RESULTS_AMOUNT,
        page: 0
    };

    $.post(url,
        JSON.stringify(search_values),
        function(response)
        {
            console.log(response);
            var i = 0;
            for (var key in response) {
                var place = response[key];
                addMarker(new google.maps.LatLng(place.latitude, place.longitude),
                          place["name"], place["id"], true, enumMarkerColors[searchCategory], i);
                addLocationRow(place, searchCategory, i);
                i++;
            }
        },
        'json')
    .fail(function(jgXHR, textStatus, errorThrown) {
         console.log("Failed to search by marker");
    });
}

/**
 * Created by DrorBrunman on 04/01/2017.
 */
function searchByFullText(word,category) {
    var url = "/searchByFullText/";

    var search_values = {
        word: word,
        category: category,
        limit: DEFAULT_RESULTS_AMOUNT,
        page:0
    };

    $.post(url,
        JSON.stringify(search_values),
        function(response)
        {
            var i = 0;
            for (var key in response) {
                var place = response[key];
                addMarker(new google.maps.LatLng(place.latitude, place.longitude),
                          place["name"], place["id"], false, enumMarkerColors[category], i);
                addLocationRow(place, category, i);
                i++;
            }
        },
        'json')
    .fail(function(jgXHR, textStatus, errorThrown) {
         console.log("Failed to run full text search");
    });
}

function getPlaceDetails(place_id) {
    var url="/place/" + place_id + "/details/";

    $.getJSON(url,
    "",
    function(response) {
        console.log(response);
    },
        'json')
    .fail(function(jgXHR, textStatus, errorThrown) {
         console.log("Failed to fetch Hotels");
    });
}
