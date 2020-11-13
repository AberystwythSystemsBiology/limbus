function measurement() {
    if ($("#requires_measurement").is(":checked")) {
        $("#measurement_div").show();
    }

    else {
        $("#measurement_div").hide();
    }
}

function symbol() {
    if ($("#requires_symbol").is(":checked")) {
        $("#symbol_div").show();
    }

    else {
        $("#symbol_div").hide();
    }
}

$(document).ready(function () {
    measurement();
    symbol();

    $("#requires_symbol, #requires_measurement").change(function () {
        measurement();
        symbol();
    });
});