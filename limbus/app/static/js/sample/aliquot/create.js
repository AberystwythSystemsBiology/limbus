function manual_sample_per_aliquot() {
    $("#size").prop("readonly", false);
    update_proposed();
}

function automatic_sample_per_aliquot() {
    $("#size").prop("readonly", true);
    var current_quantity = parseFloat($("#available_quantity").text());
    var number_aliquot = $("#count").val()

    var aliquoted_amount = current_quantity / number_aliquot
    $("#size").val(aliquoted_amount);

    $("#proposed_quantity").text("0.0");
}

function update_proposed() {
    var current_quantity = parseFloat($("#available_quantity").text());
    var number_aliquot = $("#count").val();
    var size = $("#size").val()

    var total = number_aliquot * size;

    var proposed_quantity = current_quantity - total;

    $("#proposed_quantity").text(proposed_quantity);

    if (proposed_quantity < 0) {
        $("#nes_warning").show();
        $("#submit").prop("disabled", true);
        $("form").submit(function(e){
            e.preventDefault();
        });
    }

    else {
        $("#nes_warning").hide();
        $("#submit").prop("disabled", false);

    }

}

$(document).ready(function() {
    $("#use_entire").change(function() {
        if(this.checked) {
            automatic_sample_per_aliquot();
        }
        else {
            manual_sample_per_aliquot();
        }
    });

    $("#count").change(function () {
        if ($("#use_entire").is(":checked")) {
            automatic_sample_per_aliquot();
        }
        else {
            manual_sample_per_aliquot();
        }

    })

    $("#size").change(function () {
        update_proposed();
    })
});