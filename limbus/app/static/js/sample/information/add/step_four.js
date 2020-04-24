Date.prototype.toDateInputValue = (function() {
    var local = new Date(this);
    local.setMinutes(this.getMinutes() - this.getTimezoneOffset());
    return local.toJSON().slice(0,10);
});


function hide_all() {
    $("#processing_date_div").hide();
    $("#processing_time_div").hide();
}

function show_all() {
    $("#processing_date_div").show();
    $("#processing_time_div").show();
}

function logic() {
    if ($("#sample_status option:selected").text() != "Not Processed") {
        $("#processing_date").val("");
        $("#processing_time").val("")
        $("#processing_date").prop("required", true);
        $("#processing_time").prop("required", true);

        show_all();
    }

    else {
        $("#processing_date").val(new Date().toDateInputValue());
        $("#processing_time").val("01:10");
        $("#processing_date").prop("required", false);
        $("#processing_time").prop("required", false);
        hide_all();
    }
}

$(document).ready(function() {
    logic();
    $("#sample_status").change(function () {
        logic();
    });
});