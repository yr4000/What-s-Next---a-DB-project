/**
 * Created by Alonmeytal on 24/12/2016.
 */
// Holds the map object.
var map = null;

// Holds all the markers currently on displayed on the map.
var markersArray = new Array();

// Holds the marker placed where the user last clicked on the map.
var lastMapClickLocation = null;

// If the setting a Marker should "find places"
var markForSearch = false;

//If the use wants to search by string
var isSearchByText = false;

// Search Category (Holds first default search value
var searchCategory = null;

// Default Distance for search
var searchDistance = DEFAULT_SEARCH_DISTANCE;

// this will contain the place_id's of the current search
var currentSearch = [];

// Next page to ask in request.
var requestPage = 0;
