Date.prototype.toDateInputValue = (function() {
    var local = new Date(this);
    local.setMinutes(this.getMinutes() - this.getTimezoneOffset());
    return local.toJSON().slice(0,10);
});

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

function view_form_helper(id_ref) {
    var protocol_id = $("#"+id_ref+"_select option:selected").val();
    var url = $("#"+id_ref+"_select_href").attr("href");
    var url_without_id = url.substr(0, url.lastIndexOf("-") + 1)
    $("#"+id_ref+"_select_href").attr("href", url_without_id + protocol_id);
}

$(document).ready(function() {
    disposal_logic();
    donor_logic();
    view_consent_form();
    view_form_helper("collection");

    $("#consent_select").on("change", function() {
        view_form_helper("consent");
    });

    $("#collection_select ").on("change", function() {
        view_form_helper("collection");
    });


    $("#disposal_instruction").on("change", function() {
        disposal_logic();
    });

    $("#has_donor").on("change", function() {
        donor_logic();
    })
});
