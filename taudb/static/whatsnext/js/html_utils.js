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
            var searchValue = $("#overlay-place-name").val()
            if (searchValue.length <= 4) {
                alert("Word length should be more then 4 letters!")
                return;
            }
            searchByFullText(searchValue);
            closeNav();
        }
    });

    $("#overlay-search-category").on("change", function() {
        changeSearchCategory($("#overlay-search-category").find(":selected").text())
    });

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
            if (searchValue.length <= 4) {
                alert("Word length should be more then 4 letters!")
                return;
            }
            searchByFullText(searchValue);
            $("#search-div").css('display','none');
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
                break;
            case "lucky-results":
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
        if (lastSearch == enumSearchTypes.Marker) {
            searchAroundMarker(lastMarkerSearched.latitude, lastMarkerSearched.longitude);
        }
        else if (lastSearch == enumSearchTypes.FullText) {
            searchByFullText(lastWordSearched);
        }
    });

    $("#current-accept").on("click", function(e) {
        // Remembering choice.
        if (currentSearch.length == MAXIMUM_DESTINATIONS_LIST_LENGTH) {
            // TODO: can this be a proper div rather than an alert?
            alert("You cannot choose more than " + MAXIMUM_DESTINATIONS_LIST_LENGTH + " destinations");
            showTab("past-search");
            return;
        }
        
        currentSearch.push(currentPlace);
        // Asking what's next
        $(".next-nav").show();
    });

    $("#end-here").on("click", function(e) {
        updatePopularSearches();
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
    getMostPopular();
}

function closeNav() {
    $("#myNav").hide();
    $(".nav").show();
}

function showTab(tabName) {
    $(".tab").hide();
    $("#" + tabName).show();
}

function searchBarShow() {
    if ($("#input-around").is(":visible") || $("#input-fulltext").is(":visible"))
        return;

    $("#search-div").css('display','table');
}

function searchBarHide() {
    $("#search-div").css('display','none');
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
    changeSearchCategory(newCategory);
}

function nextCategory(category) {
    $(".next-nav").hide();
    changeSearchCategory(category);
    searchAroundMarker(currentPlace.latitude, currentPlace.longitude);
}

function addLocationRow(location, type, index) {
    var resultsTable = document.getElementById("results");

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
    markerCell.innerHTML = '<img src="' + iconFolderPath + enumMarkerColors[capitalizeFirstLetter(place.category)] +
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

function capitalizeFirstLetter(string)
{
    if (!string || 0 == string.length)
        return '';

    return string.charAt(0).toUpperCase() + string.slice(1).toLowerCase();
}

function cleanPastResults() {
    if ($("#explanation-div").is(":visible"))
        $("#explanation-div").hide();

    $("#search-div").hide();
    $("#input-around").hide();
    $("#input-fulltext").hide();

    clearArray(markersArray);
    clearTable("results");
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