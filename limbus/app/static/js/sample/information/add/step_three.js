function molecular_sample(){
    $(".quantity-text").html("&mu;g/mL");
    $("#molecular_sample_type_div").show();

}

function cellular_sample(){
    $(".quantity-text").html("Cells");
    $("#cell_sample_type_div").show();
}

function fluid_sample(){
    $(".quantity-text").html("mL");
    $("#fluid_sample_type_div").show();
}

function hide_all(){
    $("#molecular_sample_type_div").hide();
    $("#cell_sample_type_div").hide();
    $("#fluid_sample_type_div").hide();
}

$(document).ready(function() {
    hide_all();
    fluid_sample();

    $("#sample_type").change(function() {
        hide_all();
        if ($(this).val() == "CEL") {
            cellular_sample();
        }
        else if ($(this).val() == "MOL") {
            molecular_sample();
        }
        else {
            fluid_sample();
        }
    });

});