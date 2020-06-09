Date.prototype.toDateInputValue = (function() {
    var local = new Date(this);
    local.setMinutes(this.getMinutes() - this.getTimezoneOffset());
    return local.toJSON().slice(0,10);
});

function disposal_logic() {
    if ($("#disposal_instruction option:selected").val() == "NAP") {
        $("#disposal_date_div").hide();
        $("#disposal_date").prop("required", false);
        $("#disposal_date").val(new Date().toDateInputValue());
    }
    else {
        $("#disposal_date").val("");
        $("#disposal_date").prop("required", true);
        $("#disposal_date_div").show();

    }
}

function donor_logic() {
    if ($("#has_donor:checkbox:checked").length >= 1) {
        $("#donor_select_div").show();
    }
    else {
        $("#donor_select_div").hide();
    }
}

$(document).ready(function() {
    disposal_logic();
    donor_logic();

    $("#disposal_instruction").on("change", function() {
        disposal_logic();
    });

    $("#has_donor").on("change", function() {
        donor_logic();
    })
});
