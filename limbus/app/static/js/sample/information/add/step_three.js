function molecular_sample(){
    $(".quantity-text").html("&mu;g/mL");
    $("#molecular_sample_type_div").show();
    $("#fluid_container_div").show();
}

function cellular_sample(){
    $(".quantity-text").html("Cells");
    $("#cell_sample_type_div").show();
    $("#cell_container_div").show();
    $("#fixation_type_div").show();

}

function fluid_sample(){
    $(".quantity-text").html("mL");
    $("#fluid_sample_type_div").show();
    $("#fluid_container_div").show();

}

function hide_all(){
    $("#molecular_sample_type_div").hide();
    $("#cell_sample_type_div").hide();
    $("#fluid_sample_type_div").hide();
    $("#cell_container_div").hide();
    $("#fluid_container_div").hide();
    $("#fixation_type_div").hide();

}

function check_and_apply() {
    var v = $("#sample_type").val();
    hide_all();
        if (v == "CEL") {
            cellular_sample();
        }
        else if (v == "MOL") {
            molecular_sample();
        }
        else {
            fluid_sample();
        }
}

$(document).ready(function() {
    hide_all();
    fluid_sample();

    check_and_apply();

    $("#sample_type").change(function() {
        check_and_apply();
    });

});