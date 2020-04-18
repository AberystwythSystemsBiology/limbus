function manual_sample_per_aliquot() {
    $("#size").prop("readonly", false);

}

function change_on_num_aliquot() {
    var current_quantity = parseFloat($("#available_quantity").text());
    var number_aliquot = $("#count").val()

    var aliquoted_amount = current_quantity / number_aliquot
    $("#size").val(aliquoted_amount);

}

function automatic_sample_per_aliquot() {
    $("#size").prop("readonly", true);
    change_on_num_aliquot();
    $("#proposed_quantity").text("0.0");
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
        automatic_sample_per_aliquot();
    })
});