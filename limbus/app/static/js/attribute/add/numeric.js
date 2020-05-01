function measurement() {
    if ($("#requires_measurement").is(":checked")) {
        $("#measurement_div").show();
    }

    else {
        $("#measurement_div").hide();
    }
}

function prefix() {
    if ($("#requires_prefix").is(":checked")) {
        $("#prefix_div").show();
    }

    else {
        $("#prefix_div").hide();
    }
}

$(document).ready(function () {
    measurement();
    prefix();

    $("#requires_prefix, #requires_measurement").change(function () {
        measurement();
        prefix();
    });
});