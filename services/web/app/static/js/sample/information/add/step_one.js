
function disposal_logic() {
    if ($("#disposal_instruction option:selected").val() == "NAP") {
        $("#disposal_date_div").hide();
    }
    else {
        $("#disposal_date").val("");
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

function view_consent_form() {
    var consent_id = $("#consent_select option:selected").val();
    var url = $("#consent_select_href").attr("href");
    $("#consent_select_href").attr("href", url.replace("%20", consent_id));
}


$(document).ready(function() {
    disposal_logic();
    donor_logic();
    view_consent_form();
    view_form_helper("consent_select");
    view_form_helper("collection_select");

    $("#consent_select").on("change", function() {
        view_form_helper("consent_select");
    });

    $("#collection_select ").on("change", function() {
        view_form_helper("collection_select");
    });


    $("#disposal_instruction").on("change", function() {
        disposal_logic();
    });

    $("#has_donor").on("change", function() {
        donor_logic();
    })
});
