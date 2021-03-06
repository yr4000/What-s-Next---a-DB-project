function showSearchResults(tab, table) {
    cleanPastResults(table);
    showTab(tab);

    if (!Object.keys(searchResults[table]).length) {
        var tableDOM = document.getElementById(table);
        var row = tableDOM.insertRow(-1);
        var apologyCell = row.insertCell(0);
        apologyCell.innerText = "We're sorry but there are no results available for this search. =\\";
        apologyCell.className = "apology";
    }

    var i = 0;
    var resultsKeys = Object.keys(searchResults[table]);
    for (var j = 10 * resultsPage; j < Math.min(10 * (resultsPage + 1), Object.keys(searchResults[table]).length); j++)
    {
        var place = searchResults[table][resultsKeys[j]];
        addMarker(new google.maps.LatLng(place.latitude, place.longitude),
                  place["name"], place["id"], false, enumMarkerColors[place.category], i);
        addLocationRow(table, place, place.category, i);
        i++;
    }

    resultsOrPlace = "results-div";
}

function showPastResults() {
    showTab("past-search");
    clearTable("past-results");

    if (currentSearch.length == 0)
        $("#end-choices").hide();
    else
        $("#end-choices").show();
    
    for (var i = 0; i < currentSearch.length; i++) {
        var place = currentSearch[i];
        addChoiceRow(place, i);
    }
}

function showResultTab(resultsDiv) {
    lastSearch = enumSearchTypes.Marker;

    if ((resultsDiv != undefined) && (resultsOrPlace != resultsDiv)) {
        resultsOrPlace = resultsDiv;
    }

    if (resultsOrPlace == "results-div")
        showSearchResults("results-div","results");
    showTab(resultsOrPlace);
}

function tryAndGetLucky() {
    lastSearch = enumSearchTypes.FeelingLucky;

    if (!!lastMapClickLocation)
        ImFeelingLucky(lastMapClickLocation.position.lat(), lastMapClickLocation.position.lng());

    showTab("lucky-tab");
}
    