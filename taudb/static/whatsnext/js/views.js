function showSearchResults(results) {
    if (!Object.keys(results).length)
        return; // If no results were returned do nothing.

    cleanPastResults();
    showTab("results-div");

    var i = 0;
    for (var key in results) {
        var place = results[key];
        addMarker(new google.maps.LatLng(place.latitude, place.longitude),
                  place["name"], place["id"], false, enumMarkerColors[place.category], i);
        addLocationRow(place, place.category, i);
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
    if ((resultsDiv != undefined) && (resultsOrPlace != resultsDiv)) {
        resultsOrPlace = resultsDiv;
    }
    showTab(resultsOrPlace);
}
