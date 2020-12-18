

$(document).ready(function () {
    $("#diagnosis-nav").on("click", function() {
        $("#basic-info-nav").removeClass("active");
        $(this).addClass("active");
        alert("ass");
    })
});