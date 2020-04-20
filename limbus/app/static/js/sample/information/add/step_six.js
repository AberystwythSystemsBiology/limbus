Date.prototype.toDateInputValue = (function() {
    var local = new Date(this);
    local.setMinutes(this.getMinutes() - this.getTimezoneOffset());
    return local.toJSON().slice(0,10);
});


function hide_disposal_information() {
    $("#disposal_date_div").hide();
    console.log(new Date().toDateInputValue());
    $("#disposal_date").val(new Date().toDateInputValue());
}

function show_disposal_information() {
    $("#disposal_date_div").show();
    $("#disposal_date").val("");
}

function logic() {
    if ($("#disposal_instruction option:selected").text() == "No Disposal") {
            hide_disposal_information();
        }

        else {
            show_disposal_information();
        }
}

$(document).ready(function() {
    logic();

    $("#disposal_instruction").change(function () {
        logic();
    });

});