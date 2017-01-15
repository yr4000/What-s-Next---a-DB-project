/**
 * Created by Alonmeytal on 24/12/2016.
 */
var enumZoomLevels = {
    City : 11,
    Districts : 13,
    Streets : 15,
    Buildings : 20
};

var enumMarkerColors = {
    Restaurant : "red/red_Marker",
    Hotel : "blue/blue_Marker",
    Bar : "purple/purple_Marker",
    Museum : "orange/orange_Marker",
    Current : "darkgreen/darkgreen_Marker"
};

var enumSearchTypes = {
    Marker : "Marker",
    FullText : "FullText"
};

var DEFAULT_MAP_CENTER = {lat: 51.509865, lng: -0.118092};

var DEFAULT_SEARCH_DISTANCE = 5000;
var DEFAULT_SEARCH_CATEGORY = "Hotel";
var RESOLUTION = 10000;
var DEFAULT_RESULTS_AMOUNT = 20;
