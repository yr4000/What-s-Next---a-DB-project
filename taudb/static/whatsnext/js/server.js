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

//    url(r'^place/get_around_marker/', views.search_places_by_point)
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
            lastSearch = enumSearchTypes.Marker;
            lastMarkerSearched = {latitude: latitude, longitude: longitude};
            showSearchResults("results-div", "results", response);
        },
        'json')
    .fail(function(jgXHR, textStatus, errorThrown) {
         console.log("Failed to Search around Marker");
    });
}

//    url(r'^searchByFullText', views.search_by_name)
function searchByFullText(word) {
    var url = "/searchByFullText/";

    var search_values = {
        word: word,
        category: searchCategory,
        page: requestPage
    };

    $.post(url,
        JSON.stringify(search_values),
        function(response)
        {
            lastSearch = enumSearchTypes.FullText;
            lastWordSearched = word;
            showSearchResults("results-div", "results", response);
        },
        'json')
    .fail(function(jgXHR, textStatus, errorThrown) {
         console.log("Failed to preform Full Text Search");
    });
}

//    url(r'^stats/top_places', views.calc_top_places_for_category)
function getMostPopular() {
    var url = "/stats/top_places?category=" + searchCategory;

    $.getJSON(url,
        "",
        function(response){
            clearTable("popular-results");

            var resultsTable = document.getElementById("popular-results");
            var resultNum = 0;
            for (key in response) {
                var result = response[key];
                var resultRow = resultsTable.insertRow(-1);
                var iconCell = resultRow.insertCell(0);
                iconCell.innerHTML = '<img src="' + iconFolderPath + enumMarkerColors[result.category] +
                                     String.fromCharCode((resultNum % 26) + 65) + '.png">';
                var nameCell = resultRow.insertCell(1);
                nameCell.innerText = result.name;
                var popularityCell = resultRow.insertCell(2);
                popularityCell.innerText = result.popularity;
                $(resultRow).data("place", {id:result.id, icon:resultNum});
                resultRow.onclick = function(e) {
                    getPlaceDetails($(this).data("place").id, $(this).data("place").icon);
                };
                resultNum++;
            }
        },
        'json')
    .fail(function(jgXHR, textStatus, errorThrown) {
         console.log("Failed to get Most Popular Places.");
    });
}

//    url(r'^searchCombinationByPoint', views.find_suggestion_by_point)
function searchCombinationByPoint(latitude, longitude) {
    var url = "/searchCombinationByPoint/";
    //isSearchByText = false; // TODO Alon add to enumSearchTypes if needed.

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

            showResultTab("place-div");

            var i = 0;
            for (var key in response) {
                var sugg = response[key]; // the current 4 places combo suggestion from query

                addMarker(new google.maps.LatLng(sugg[0].latitude, sugg[0].longitude),
                          sugg[0]["name"], sugg[0]["id"], false, enumMarkerColors["Hotel"], i);
                addLocationRow(sugg[0], "Hotel", i);

                addMarker(new google.maps.LatLng(sugg[1].latitude, sugg[1].longitude),
                          sugg[1]["name"], sugg[1]["id"], false, enumMarkerColors["Restaurant"], i+1);
                addLocationRow(sugg[1], "Restaurant", i+1);

                addMarker(new google.maps.LatLng(sugg[2].latitude, sugg[2].longitude),
                          sugg[2]["name"], sugg[2]["id"], false, enumMarkerColors["Bar"], i+2);
                addLocationRow(sugg[2], "Bar", i+2);

                addMarker(new google.maps.LatLng(sugg[3].latitude, sugg[3].longitude),
                          sugg[3]["name"], sugg[3]["id"], false, enumMarkerColors["Museum"], i+3);
                addLocationRow(sugg[3], "Museum", i+3);

                i = i + 4;
            }
        },
        'json')
    .fail(function(jgXHR, textStatus, errorThrown) {
         console.log("Failed to preform search combination by point");
    });
}

//    url(r'^stats/top_places', views.calc_top_places_for_category)
function getPlaceDetails(place_id, index) {
    var url="/place/" + place_id + "/details/";

    $.getJSON(url,
    "",
    function(response) {
        currentPlace = response.place;

        showResultTab("place-div");

        $("#current-icon")[0].src = iconFolderPath + enumMarkerColors[currentPlace.category] +
                                    String.fromCharCode((index % 26) + 65) + ".png";
        $("#current-name")[0].innerHTML = currentPlace.name;
        $("#current-id")[0].innerText = "Internal: " + currentPlace.id + "| Google: " + currentPlace.google_id;
        $("#current-id").data("place-id", currentPlace.id);
        $("#current-address")[0].innerText = currentPlace.vicinity;

        clearTable("current-reviews"); // Clear Old Reviews before inserting new ones.

        if (response.reviews.length == 0) {
            var apologyDiv = document.createElement("div");
            apologyDiv.innerText = "We're sorry but there are no reviews available for this place. =\\";
            apologyDiv.className = "apology";
            $("#current-reviews")[0].appendChild(apologyDiv);
        }
        else {
            for (var key in response.reviews) {
                var review = response.reviews[key];
                var reviewDiv = document.createElement("div");
                reviewDiv.className = "review";
                reviewDiv.innerHTML = "<b>Rating: " + review.rating + "</b></br>" + review.text +
                                      "</br><b>By " + review.author + " on " + review.date + "</b>";
                $("#current-reviews")[0].appendChild(reviewDiv);
            }
        }

        getPlaceStatistics();
    },
        'json')
    .fail(function(jgXHR, textStatus, errorThrown) {
         console.log("Failed to fetch Place Details");
    });
}

//    url(r'^stats/categories', views.calc_categories_statistics)
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

//    url(r'^updatePopularSearches', views.update_popular_search)
function updatePopularSearches() {
    console.log("started update popular search");
    var url = "/updatePopularSearches/";

    if(currentSearch.length == 0){
        console.log("Search is empty, no update was made");
        return;
    }

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

            while (currentSearch.length!=0){
                currentSearch.pop();
            }
        },
        'json')
    .fail(function(jgXHR, textStatus, errorThrown) {
         console.log("Failed to update popular searches :(");
    });
    console.log("finished updated popular search");
}

//    url(r'^ImFeelingLucky', views.im_feeling_lucky)
function ImFeelingLucky(latitude, longitude) {
    var url = "/ImFeelingLucky/";

    var search_values = {
        latitude: latitude,
        longitude: longitude,
        distance: searchDistance
    };

    $.post(url,
        JSON.stringify(search_values),
        function(response)
        {
            console.log(response);
            lastSearch = enumSearchTypes.FeelingLucky;
            lastMarkerSearched = {latitude: latitude, longitude: longitude};
            showSearchResults("lucky-tab", "lucky-results", response);
        },
        'json')
    .fail(function(jgXHR, textStatus, errorThrown) {
         console.log("Failed to find luck");
    });
}

//    url(r'^stats/top_choices', views.calc_top_choices)
