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
    restaurant : "red/red_Marker",
    hotel : "blue/blue_Marker",
    bar : "purple/purple_Marker",
    museum : "orange/orange_Marker",
    current : "darkgreen/darkgreen_Marker"
};

var enumSearchTypes = {
    Marker : "Marker",
    FullText : "FullText",
    FeelingLucky : "FeelingLucky"
};

var DEFAULT_MAP_CENTER = {lat: 51.509865, lng: -0.118092};

var DEFAULT_SEARCH_DISTANCE = 1500;
var DEFAULT_SEARCH_CATEGORY = "Hotel";
var RESOLUTION = 10000;
var DEFAULT_RESULTS_AMOUNT = 20;

var MAXIMUM_DESTINATIONS_LIST_LENGTH = 10;