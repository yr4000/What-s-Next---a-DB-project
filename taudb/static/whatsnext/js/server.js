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
            if(markersArray.length !=0){
                clearMarkers();
                clearResultsTable();
            }

            $("#place-div").hide();
            $("#results-div").show();

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
         console.log("Failed to Search around Marker");
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
            if(markersArray.length !=0){
                clearMarkers();
                clearResultsTable();
            }

            $("#place-div").hide();
            $("#results-div").show();

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
         console.log("Failed to preform Full Text Search");
    });
}

function getPlaceDetails(place_id, index) {
    var url="/place/" + place_id + "/details/";

    $.getJSON(url,
    "",
    function(response) {
        console.log(response);

        $("#results-div").hide();
        $("#place-div").show();

        $("#current-icon")[0].src = iconFolderPath + enumMarkerColors[capitalizeFirstLetter(response.place.category)] +
                                    String.fromCharCode((index % 26) + 65) + ".png";
        $("#current-name")[0].innerHTML = response.place.name;
        $("#current-id")[0].innerText = "Internal: " + place_id + "| Google: " + response.place.google_id;
        $("#current-address")[0].innerText = response.place.vicinity;

        for (var key in response.reviews) {
            var review = response.reviews[key];
            var reviewDiv = document.createElement("div");
            reviewDiv.className = "review";
            reviewDiv.innerHTML = "<b>Rating: " + review.rating + "</b></br>" + review.text +
                                  "</br><b>By " + review.author + " on " + review.date + "</b>";
            $("#current-reviews")[0].appendChild(reviewDiv);
        }
    },
        'json')
    .fail(function(jgXHR, textStatus, errorThrown) {
         console.log("Failed to fetch Place Details");
    });
}

function getPlaceStatistics(place) {
    var url="/stats/categories?latitude=" + place.latitude + "&longitude=" + place.longitude + "&distance=" + DEFAULT_SEARCH_DISTANCE;
    $.getJSON(url,
    "",
    function(response) {
        console.log(response);
    },
        'json')
    .fail(function(jgXHR, textStatus, errorThrown) {
         console.log("Failed to fetch Place Statistics");
    });

    
}