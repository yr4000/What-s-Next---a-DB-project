/**
 * Created by Alonmeytal on 24/12/2016.
 */
$(document).ready(function () {
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
            searchByFullText($("#overlay-place-name").val(), searchCategory);
            closeNav();
        }
    });

    $("#overlay-search-category").on("change", function() {
        changeSearchCategory($("#overlay-search-category").find(":selected").text())
    });

    $("#place-name").on("keyup", function(e) {
        var keyPressed = (e.keyCode ? e.keyCode : e.which);
        if(keyPressed == 13) {
            var searchValue = $("#place-name").val();
            searchByFullText(searchValue);
        }
    });

    changeSearchCategory(DEFAULT_SEARCH_CATEGORY);
});

function changeSearchCategory(newCategory) {
    if (newCategory != searchCategory) {
        searchCategory = newCategory;
        requestPage = 0;
        $(".selected").removeClass("selected");
        $("#search-" + newCategory).addClass("selected");
    }
}

function closeNav() {
    $("#myNav").hide();
    $(".nav").show();
}

function markForSearch() {
    markForSearch = true;
    closeNav();
}

function showResults() {
    $("#place-div").hide();
    $("#results-div").show();
    map.setZoom(enumZoomLevels.Districts);
}

function searchBarShow() {
    $("#search-div").css('display','table');
};

function searchBarHide() {
    $("#search-div").css('display','none');
};

function selectForSearch(categoryDiv) {
    var newCategory = $(categoryDiv).text();
    changeSearchCategory(newCategory);
    searchBarShow();
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
