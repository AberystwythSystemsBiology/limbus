/*
Copyright (C) 2020 Keiron O'Shea <keo7@aber.ac.uk>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
*/

function molecular_sample(){
    $(".quantity-text").html("&mu;g/mL");
    $("#molecular_sample_type_div").show();
    //$("#fluid_container_div").show();
}

function cellular_sample(){
    $(".quantity-text").html("Cells");
    $("#cell_sample_type_div").show();
    $("#tissue_sample_type_div").show();
    //$("#cell_container_div").show();
    $("#fixation_type_div").show();

}

function fluid_sample(){
    $(".quantity-text").html("mL");
    $("#fluid_sample_type_div").show();
    //$("#fluid_container_div").show();

}

function primary_container(){
    $("#cell_container_div").hide();
    $("#fluid_container_div").show();
}

function lts_container(){
    $("#fluid_container_div").hide();
    $("#cell_container_div").show();
}

function hide_all(){
    $("#tissue_sample_type_div").hide();

    $("#molecular_sample_type_div").hide();
    $("#cell_sample_type_div").hide();
    $("#fluid_sample_type_div").hide();
    //$("#cell_container_div").hide();
    //$("#fluid_container_div").hide();
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

function container_check_and_apply() {
    var v = $("#container_base_type").val();

        if (v == "PRM") {
            primary_container();
        }
        else {
            lts_container();
        }
}

$(document).ready(function() {
    hide_all();
    fluid_sample();
    primary_container();

    //check_and_apply();
    $("#sample_type").change(function() {
        check_and_apply();
    });
    $("#container_base_type").change(function() {
        container_check_and_apply();
    });

});