/**
 * Created by Alonmeytal on 24/12/2016.
 */
$(document).ready(function () {
    $("#start-hotel").click(function(event) {
        console.log("h");
        $("#start-restaruant").show();
        $("#search-restaurant").hide();
        $("#start-hotel").hide();
        $("#search-hotel").show();
    });
    $("#start-restaruant").click(function(event) {
        console.log("r");
        $("#start-hotel").show();
        $("#search-hotel").hide();
        $("#start-restaruant").hide();
        $("#search-restaurant").show();
    });
});

function addLocationRow(location) {

}