function showSearchResults(tab, table, results) {
    if (!Object.keys(results).length)
        return; // If no results were returned do nothing.

    cleanPastResults(table);
    showTab(tab);

    var i = 0;
    for (var key in results) {
        var place = results[key];
        addMarker(new google.maps.LatLng(place.latitude, place.longitude),
                  place["name"], place["id"], false, enumMarkerColors[place.category], i);
        addLocationRow(table, place, place.category, i);
        i++;
    }

    requestPage++;

    resultsOrPlace = "results-div";
}

function showPastResults() {
    showTab("past-search");
    // Clean Table.
    clearTable("past-results");
    // Insert new values.
    for (var i = 0; i < currentSearch.length; i++) {
        var place = currentSearch[i];
        addSearchLocationRow(place, i);
    }
}

function showResultTab(resultsDiv) {
    lastSearch = enumSearchTypes.Marker;

    if ((resultsDiv != undefined) && (resultsOrPlace != resultsDiv)) {
        resultsOrPlace = resultsDiv;
    }
    showTab(resultsOrPlace);
}

function tryAndGetLucky() {
    lastSearch = enumSearchTypes.FeelingLucky;

    if (!!lastMapClickLocation)
        ImFeelingLucky(lastMapClickLocation.position.lat(), lastMapClickLocation.position.lng());

    showTab("lucky-tab");
}
    