function cleanScreen() {
    clearArray(markersArray);
    clearTable("results");
    //map.setZoom(enumZoomLevels.Districts);
}

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
        page: requestPage
    };

    $.post(url,
        JSON.stringify(search_values),
        function(response)
        {
            if(markersArray.length !=0){
                cleanScreen();
            }

            $("#place-div").hide();
            $("#results-div").show();

            console.log(response);

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
         console.log("Failed to Search around Marker");
    });
}

function searchByFullText(word) {
    var url = "/searchByFullText/";
    isSearchByText = true;

    var search_values = {
        word: word,
        category: searchCategory,
        page: requestPage
    };

    $.post(url,
        JSON.stringify(search_values),
        function(response)
        {
            if(markersArray.length !=0){
                cleanScreen();
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

function searchCombinationByPoint(latitude, longitude) {
    var url = "/searchCombinationByPoint/";
    isSearchByText = false;

    var search_values = {
        latitude: latitude,
        longitude: longitude,
        page: requestPage
    };

    $.post(url,
        JSON.stringify(search_values),
        function(response)
        {
            if(markersArray.length !=0){
                clearArray(markersArray);
                clearResultsTable();
            }

            $("#place-div").hide();
            $("#results-div").show();

            var i = 0;
            for (var key in response) {
                var sugg = response[key]; // the current 4 places combo suggestion from query

                addMarker(new google.maps.LatLng(sugg[0].latitude, sugg[0].longitude),
                          sugg[0]["name"], sugg[0]["id"], false, enumMarkerColors[sugg[0]["category"]], i);
                addLocationRow(sugg[0], sugg[0]["category"], i);

                addMarker(new google.maps.LatLng(sugg[1].latitude, sugg[1].longitude),
                          sugg[1]["name"], sugg[1]["id"], false, enumMarkerColors[sugg[1]["category"]], i+1);
                addLocationRow(sugg[1], sugg[1]["category"], i+1);

                addMarker(new google.maps.LatLng(sugg[2].latitude, sugg[2].longitude),
                          sugg[2]["name"], sugg[2]["id"], false, enumMarkerColors[sugg[2]["category"]], i+2);
                addLocationRow(sugg[2], sugg[2]["category"], i+2);

                addMarker(new google.maps.LatLng(sugg[3].latitude, sugg[3].longitude),
                          sugg[3]["name"], sugg[3]["id"], false, enumMarkerColors[sugg[3]["category"]], i+3);
                addLocationRow(sugg[3], sugg[3]["category"], i+3);

                i = i + 4;
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

        //map.setZoom(enumZoomLevels.Streets);
        currentPlace = response.place;

        $("#results-div").hide();
        $("#place-div").show();

        $("#current-icon")[0].src = iconFolderPath + enumMarkerColors[capitalizeFirstLetter(currentPlace.category)] +
                                    String.fromCharCode((index % 26) + 65) + ".png";
        $("#current-name")[0].innerHTML = currentPlace.name;
        $("#current-id")[0].innerText = "Internal: " + currentPlace.place_id + "| Google: " + currentPlace.google_id;
        $("#current-id").data("place-id", currentPlace.place_id);
        $("#current-address")[0].innerText = currentPlace.vicinity;

        for (var key in response.reviews) {
            var review = response.reviews[key];
            var reviewDiv = document.createElement("div");
            reviewDiv.className = "review";
            reviewDiv.innerHTML = "<b>Rating: " + review.rating + "</b></br>" + review.text +
                                  "</br><b>By " + review.author + " on " + review.date + "</b>";
            $("#current-reviews")[0].appendChild(reviewDiv);
        }
        getPlaceStatistics();
    },
        'json')
    .fail(function(jgXHR, textStatus, errorThrown) {
         console.log("Failed to fetch Place Details");
    });
}

function getPlaceStatistics() {
    var url="/stats/categories?latitude=" + currentPlace.latitude + "&longitude=" + currentPlace.longitude +
        "&distance=" + DEFAULT_SEARCH_DISTANCE + "&except_category=" + currentPlace.category;
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
            // Statistics shouldn't be clickable.
            //iconCell.onclick = function() {
            //changeSearchCategory($(this).data("category"));
            //searchAroundMarker(place.latitude, place.longitude);
            //};
            var catCell = row.insertCell(cells++);
            $(catCell).data("category",key);
            catCell.innerHTML = "<b>" + category.places_amount + " " + key + "s </b>" +
                "<br> [Avg. Rating : " + category.rating_average + "]";
            //catCell.onclick = function() {
            //    changeSearchCategory($(this).data("category"));
            //    searchAroundMarker(place.latitude, place.longitude);
            //};
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
    placeIDsCurrentSearch = modifyCurrentSearchForServer()
    var search = {
        places_id_list: placeIDsCurrentSearch
    };
    console.log(placeIDsCurrentSearch);
    console.log(currentSearch);

    $.post(url,
        JSON.stringify(search),
        function(response)
        {
            console.log(response);
            console.log("updated successfuly :)");
            clearArray(currentSearch);
        },
        'json')
    .fail(function(jgXHR, textStatus, errorThrown) {
         console.log("Failed to update popular searches :(");
    });
    console.log("finished updated popular search");
}


function modifyCurrentSearchForServer(){
    modifiedSearchArr = [];
    tempArr = [];
    currentSearch.reverse();
    while(currentSearch.length != 0){
        objectHolder = currentSearch.pop();
        modifiedSearchArr.push(objectHolder["id"]);
        tempArr.push(objectHolder);
    }
    currentSearch = tempArr;
    return modifiedSearchArr;
}
