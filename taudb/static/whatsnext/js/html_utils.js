/**
 * Created by Alonmeytal on 24/12/2016.
 */
$(document).ready(function () {
    openNav();
    $("#place-name").on("keyup", function(e) {
        var keyPressed = (e.keyCode ? e.keyCode : e.which);
        if(keyPressed == 13)
            closeNavForSearch();
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
    var searchCategory = $("#nav-search-category")[0].selectedOptions[0].innerText;
    var searchValue = $("#place-name")[0].value;
    searchByFullText(searchValue, searchCategory);
    closeNav();
}


function addLocationRow(location) {

}


