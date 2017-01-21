/**
 * Created by Alonmeytal on 24/12/2016.
 */
$(document).ready(function () {
    changeSearchCategory(DEFAULT_SEARCH_CATEGORY);
    
    document.addEventListener("keyup", function(e) {
        var keyPressed = (e.keyCode ? e.keyCode : e.which);
        if ((keyPressed == 27) && $("#myNav").is(":visible")) {
            closeNav();
            document.removeEventListener("keyup", this);
        }
    });

    $("#overlay-place-name").on("keyup", function(e) {
        var keyPressed = (e.keyCode ? e.keyCode : e.which);
        if(keyPressed == 13) {
            var searchValue = $("#overlay-place-name").val();
            if (searchValue.length < 4) {
                alert("Search word must contain at least 4 letters");
                return;
            }
            searchByFullText(searchValue);
            closeNav();
        }
    });

    $("#overlay-search-category").on("change", function() {
        changeSearchCategory($("#overlay-search-category").find(":selected").text())
    });

    $("#search-radius")[0].placeholder = DEFAULT_SEARCH_DISTANCE;

    $("#search-radius").on("input",function() {
        var searchRadius = $(this).val();
        if (isNaN(parseInt(searchRadius))) {
            alert("Search radius should consist of numbers only!");
        }
        else {
            searchDistance = parseInt(searchRadius);
        }
    });

    $("#place-name").on("keyup", function(e) {
        var keyPressed = (e.keyCode ? e.keyCode : e.which);
        if(keyPressed == 13) {
            var searchValue = $("#place-name").val();
            if (searchValue.length < 4) {
                alert("Search word must contain at least 4 letters");
                return;
            }
            searchByFullText(searchValue);
            $("#search-div").show();
        }
    });

    $(".tab-option").on("click", function(e) {
        $(".tab-option").removeClass("selected-tab");
        $(this).addClass("selected-tab");

        switch(this.id) {
            case "search-results":
                showResultTab();
                break;
            case "popular-searches":
                getTopChoices();
                break;
            case "lucky-search":
                tryAndGetLucky();
                break;
            case "my-results":
                showPastResults();
                break;
        }
    });

    $("#prev-page").on("click", function(e) {
        if (requestPage <= 1)
            return;
        else {
            requestPage -= 2;
        }
        if (lastSearch == enumSearchTypes.Marker) {
            searchAroundMarker(lastMarkerSearched.latitude, lastMarkerSearched.longitude);
        }
        else if (lastSearch == enumSearchTypes.FullText) {
            searchByFullText(lastWordSearched);
        }
    });
    
    $("#next-page").on("click", function(e) {
        // Happens in Yair's use case of user who changed the category and then immidiately after
        // decided to click next.
        if (requestPage == 0)
            return;
        if (lastSearch == enumSearchTypes.Marker) {
            searchAroundMarker(lastMarkerSearched.latitude, lastMarkerSearched.longitude);
        }
        else if (lastSearch == enumSearchTypes.FullText) {
            searchByFullText(lastWordSearched);
        }
    });

    $("#current-accept").on("click", function(e) {
        // Remembering choice.
        addToChoices();

        // Asking what's next
        $("#light-overlay").show();

        $("#current-accept").hide();
        $("#current-remove").show();
    });

    $("#current-remove").on("click",function(e) {
        currentSearch.splice(currentSearch.map(function(a) { return a.id; }).indexOf(currentPlace.id), 1);
        $("#current-remove").hide();
        $("#current-accept").show();
    });

    $("#end-here").on("click", function(e) {
        endSearch();
    });

    $("#end-next").on("click", function(e) {
        endSearch();
    });
});

function changeSearchCategory(newCategory) {
    if (newCategory != searchCategory) {
        searchCategory = newCategory;
        requestPage = 0;
    }
    $(".selected").removeClass("selected");
    $("#search-" + newCategory).addClass("selected");
    $(".started").removeClass("started");
    $("#start-" + newCategory).addClass("started");
    
    $("#category-name")[0].innerText = searchCategory;
    clearTable("results");
    getMostPopular();
}

function closeNav() {
    $("#overlay").hide();
    $(".nav").show();
}

function showTab(tabName) {
    $(".tab").hide();
    $("#" + tabName).show();
}

function searchBarShow() {
    if ($("#input-around").is(":visible") || $("#input-fulltext").is(":visible"))
        return;

    $("#search-div").show();
}

function showMarkerInput() {
    $("#search-div").hide();
    $("#input-around").show();
}

function showFullTextInput() {
    $("#search-div").hide();
    $("#input-fulltext").show();
}

function selectForSearch(categoryDiv) {
    var newCategory = $(categoryDiv).text();
    changeSearchCategory(newCategory);
    searchBarShow();
}

function setFirstCategory(categorySpan) {
    var newCategory = $(categorySpan).text();

    var placeholderText = "Search for a " + newCategory.toLowerCase() + " called...";
    $("#overlay-place-name").attr("placeholder", placeholderText);

    changeSearchCategory(newCategory);
}

function nextCategory(category) {
    $("#light-overlay").hide();
    changeSearchCategory(category);
    searchAroundMarker(currentPlace.latitude, currentPlace.longitude);
}

function addLocationRow(tableName, location, type, index) {
    var resultsTable = document.getElementById(tableName);

    var placeRow = resultsTable.insertRow(-1);
    var i = 0;
    var markerCell = placeRow.insertCell(i++);
    markerCell.className = "marker-cell";
    markerCell.rowSpan = 2;
    markerCell.innerHTML = '<img src="' + iconFolderPath + enumMarkerColors[type] +
        String.fromCharCode((index % 26) + 65) + '.png">';
    var titleCell = placeRow.insertCell(i++);
    titleCell.innerText = location.name;
    titleCell.className = "place-title";
    placeRow.onclick = function() {
      getPlaceDetails(location.id, index);
    };

    placeRow = resultsTable.insertRow(-1);
    i = 0;
    var addressCell = placeRow.insertCell(i++);
    addressCell.innerText = location.vicinity;
    addressCell.className = "place-address";
    var ratingCell = placeRow.insertCell(i++);
    ratingCell.innerText = (location.rating > 0) ? location.rating : "-";
    ratingCell.className = "place-rating";
    placeRow.onclick = function() {
      getPlaceDetails(location.id, index);
    };
}

function addSearchLocationRow(place, step) {
    var resultsTable = document.getElementById("past-results");

    var placeRow = resultsTable.insertRow(-1);
    var i = 0;
    var markerCell = placeRow.insertCell(i++);
    markerCell.className = "marker-cell";
    markerCell.rowSpan = 2;
    markerCell.innerHTML = '<img src="' + iconFolderPath + enumMarkerColors[place.category] +
        String.fromCharCode((step % 26) + 65) + '.png">';
    var titleCell = placeRow.insertCell(i++);
    titleCell.innerText = place.name;
    titleCell.className = "place-title";
    var deleteCell = placeRow.insertCell(i++);
    deleteCell.innerHTML = "&times;";
    deleteCell.onclick = function(e) {
        currentSearch.splice(step, 1);
        showPastResults();
        e.stopPropagation();
    };
    placeRow.onclick = function() {
      getPlaceDetails(place.id, step);
    };

    placeRow = resultsTable.insertRow(-1);
    i = 0;
    var addressCell = placeRow.insertCell(i++);
    addressCell.innerText = place.vicinity;
    addressCell.className = "place-address";
    var ratingCell = placeRow.insertCell(i++);
    ratingCell.innerText = (place.rating > 0) ? place.rating : "-";
    ratingCell.className = "place-rating";
}

function clearTable(table_name) {
    var table = document.getElementById(table_name);

    while (table.hasChildNodes()) {
        table.removeChild(table.lastChild);
    }
}

function cleanPastResults(table) {
    if ($("#explanation-div").is(":visible"))
        $("#explanation-div").hide();

    $("#search-div").show();
    $("#input-around").hide();
    $("#input-fulltext").hide();

    clearArray(markersArray);
    clearTable(table);
}

function modifyCurrentSearchForServer(){
    var modifiedSearchArr = [];
    var tempArr = [];
    currentSearch.reverse();
    while(currentSearch.length != 0){
        var objectHolder = currentSearch.pop();
        modifiedSearchArr.push(objectHolder["id"]);
        tempArr.push(objectHolder);
    }
    currentSearch = tempArr;
    return modifiedSearchArr;
}

function addToChoices() {
    if (currentSearch.length == MAXIMUM_DESTINATIONS_LIST_LENGTH) {
        // TODO: can this be a proper div rather than an alert? I'd rather not.
        alert("You cannot choose more than " + MAXIMUM_DESTINATIONS_LIST_LENGTH + " destinations");
        showTab("past-search");
        return;
    }

    currentSearch.push(currentPlace);
}

function endSearch() {
    if ($("#light-overlay").is(":visible"))
        $("#light-overlay").hide();

    // Prevents : If you click End here from the next-nav div you'll add the same place twice.
    if ((currentSearch.length > 0) && (currentPlace.id != currentSearch[currentSearch.length-1].id))
        addToChoices();

    if (!$("#my-results").hasClass("selected-tab")) {
        $(".tab-option").removeClass("selected-tab");
        $("#my-results").addClass("selected-tab");
    }

    var locationsArr = new Array();

    clearArray(markersArray);

    for (var place_key in currentSearch) {
        var place = currentSearch[place_key];
        var placeLatLng = new google.maps.LatLng(place.latitude, place.longitude);
        addMarker(placeLatLng, place.name, place.id, (place_key == 0), enumMarkerColors[place.category], place_key);
        locationsArr.push(placeLatLng);
    }

    if (locationsArr.length > 1)
        showRouteOnMap(locationsArr);

    showPastResults();
    updatePopularSearches();
}