/**
 * Created by Alonmeytal on 24/12/2016.
 */
$(document).ready(function () {
    openNav();
    $("#overlay-place-name").on("keyup", function(e) {
        var keyPressed = (e.keyCode ? e.keyCode : e.which);
        if(keyPressed == 13)
            closeNavForSearch();
    });
    $("#search-category").on("change", function(e) {
        searchCategory = $("#search-category")[0].selectedOptions[0].innerText;
    });
    $("#place-name").on("keyup", function(e) {
        var keyPressed = (e.keyCode ? e.keyCode : e.which);
        if(keyPressed == 13) {
            var searchValue = $("#place-name")[0].value;
            searchByFullText(searchValue, searchCategory);
        }
    });
});

function openNav() {
    $("#myNav").show();
}

function closeNav() {
    $("#myNav").hide();
    $(".nav").show();
}

function markForSearch() {
    markForSearch = true;
    closeNav();
}

function closeNavForSearch() {
    searchCategory = $("#overlay-search-category")[0].selectedOptions[0].innerText;
    if (searchCategory == $("#overlay-search-category")[0].options[0].innerText) {
        searchCategory = DEFAULT_SEARCH_CATEGORY;
    }
    var searchValue = $("#overlay-place-name")[0].value;
    searchByFullText(searchValue, searchCategory);
    closeNav();
}


function addLocationRow(location, type, index) {
    var resultsTable = document.getElementById("results");

    var placeRow = resultsTable.insertRow(0);
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
      getPlaceDetails(location.id);
    };

    placeRow = resultsTable.insertRow(1);
    i = 0;
    var addressCell = placeRow.insertCell(i++);
    addressCell.innerText = location.vicinity;
    addressCell.className = "place-address";
    var ratingCell = placeRow.insertCell(i++);
    ratingCell.innerText = (location.rating > 0) ? location.rating : "-";
    ratingCell.className = "place-rating";
}


