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
    //TODO: Alon M, please use this code or something else to check update popular searches function
    for(i = 1; i<4; i++){
        currentSearch.push(i);
    }
    //updatePopularSearches();
    var search_values = {
        latitude: latitude,
        longitude: longitude,
        distance: searchDistance,
        category: searchCategory,
        limit: DEFAULT_RESULTS_AMOUNT,
        page: requestPage
    };

    $.post(url,
        JSON.stringify(search_values),
        function(response)
        {
            if(markersArray.length !=0){
                clearMarkers();
                clearTable("results");
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
            requestPage++;
        },
        'json')
    .fail(function(jgXHR, textStatus, errorThrown) {
         console.log("Failed to Search around Marker");
    });
}

/**
 * Created by DrorBrunman on 04/01/2017.
 */
function searchByFullText(word) {
    var url = "/searchByFullText/";
    isSearchByText = true;

    var search_values = {
        word: word,
        category: searchCategory,
        page_offset: requestPage
    };

    $.post(url,
        JSON.stringify(search_values),
        function(response)
        {
            if(markersArray.length !=0){
                clearMarkers();
                clearTable("results");
            }

            $("#place-div").hide();
            $("#results-div").show();

            var i = 0;
            for (var key in response) {
                var place = response[key];
                addMarker(new google.maps.LatLng(place.latitude, place.longitude),
                          place["name"], place["id"], false, enumMarkerColors[searchCategory], i);
                addLocationRow(place, searchCategory, i);
                i++;
            }
            requestPage++;
        },
        'json')
    .fail(function(jgXHR, textStatus, errorThrown) {
         console.log("Failed to preform Full Text Search");
    });
}

function searchCombinationByPoint(latitude, longitude, page_offset) {
    var url = "/searchCombinationByPoint/";
    isSearchByText = false;

    var search_values = {
        latitude: latitude,
        longitude: longitude,
        page_offset: page_offset
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
                          place["name"], place["id"], false, enumMarkerColors[place["category"]], i);
                addLocationRow(place, place["category"], i);
                i++;
            }
        },
        'json')
    .fail(function(jgXHR, textStatus, errorThrown) {
         console.log("Failed to preform search combination by point");
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
        getPlaceStatistics({latitude:response.place.latitude, longitude:response.place.longitude});
    },
        'json')
    .fail(function(jgXHR, textStatus, errorThrown) {
         console.log("Failed to fetch Place Details");
    });
}

function getPlaceStatistics(place) {
    var url="/stats/categories?latitude=" + place.latitude + "&longitude=" + place.longitude +
        "&distance=" + DEFAULT_SEARCH_DISTANCE + "&except_category=" + place.category;
    $.getJSON(url,
    "",
    function(response) {
        console.log(response);
        clearTable("statistics");
        var statistics = document.getElementById("statistics");
        var cells = 0;
        for (var key in response) {
            var category = response[key];
            if (cells % 4 == 0) {
                var row = statistics.insertRow(-1);
                cells = 0;
            }
            var iconCell = row.insertCell(cells++);
            var catIcon = document.createElement("img");
            $(iconCell).data("category",key);
            catIcon.src = iconFolderPath + enumMarkerColors[key] + "A.png";
            iconCell.appendChild(catIcon);
            iconCell.onclick = function() {
                changeSearchCategory($(this).data("category"));
                searchAroundMarker(place.latitude, place.longitude);
            };
            var catCell = row.insertCell(cells++);
            $(catCell).data("category",key);
            catCell.innerHTML = "<b>" + category.places_amount + " " + key + "s </b>" +
                "<br> [Avg. Rating : " + category.rating_average + "]";
            catCell.onclick = function() {
                changeSearchCategory($(this).data("category"));
                searchAroundMarker(place.latitude, place.longitude);
            };
        }
    },
        'json')
    .fail(function(jgXHR, textStatus, errorThrown) {
         console.log("Failed to fetch Place Statistics");
    });
}

function updatePopularSearches() {
    console.log("started update popular search");
    var url = "/updatePopularSearches/";
    var search = {
        places_id_list: currentSearch
    };
    console.log(currentSearch);

    $.post(url,
        JSON.stringify(search),
        function(response)
        {
            console.log(response);
            console.log("updated successfuly :)");
            while(currentSearch.length!=0){
                currentSearch.pop();
            }
        },
        'json')
    .fail(function(jgXHR, textStatus, errorThrown) {
         console.log("Failed to update popular searches :(");
    });
    console.log("finished");
}

//after each "what's next" we should use this function to update the currentSearch Array
function addPlaceIDToCurrentSearch(place_id) {
    currentSearch.push(place_id);
}
