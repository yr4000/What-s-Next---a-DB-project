/**
 * Created by Alonmeytal on 24/12/2016.
 */
// Google Maps API objects.
var map = null;
var directionsService = null;
var directionsDisplay = null;

// Holds all the markers currently on displayed on the map.
var markersArray = new Array();

// Holds the marker placed where the user last clicked on the map.
var lastMapClickLocation = null;

// If the setting a Marker should "find places"
var markForSearch = true;

//If the use wants to search by string
//var isSearchByText = false; // TODO Alon delete if found unnecessary

// Search Category (Holds first default search value
var searchCategory = null;

// Default Distance for search
var searchDistance = DEFAULT_SEARCH_DISTANCE;

// this will contain the place_id's of the current search
var currentSearch = [];

// Next page to ask in request.
var requestPage = 0;

// Current Place object holder.
var currentPlace = null;

// Last search type
var lastSearch = enumSearchTypes.Marker;

// Holds the latitude and longitude of the last marker search in searchByMarker.
var lastMarkerSearched = null;

// Hold the last word search in searchByFullWord.
var lastWordSearched = null;

// Did the user last see a single place or a list of results.
var resultsOrPlace = null;