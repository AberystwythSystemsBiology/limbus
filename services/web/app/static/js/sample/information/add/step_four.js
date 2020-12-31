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


function hide_all() {
    $("#processing_date_div").hide();
    $("#processing_time_div").hide();
}

function show_all() {
    $("#processing_date_div").show();
    $("#processing_time_div").show();
}

function logic() {
    if ($("#sample_status option:selected").text() != "Not Processed") {
        $("#processing_date").val("");
        $("#processing_time").val("")
        $("#processing_date").prop("required", true);
        $("#processing_time").prop("required", true);

        show_all();
    }

    else {
        $("#processing_date").val(new Date().toDateInputValue());
        $("#processing_time").val("01:10");
        $("#processing_date").prop("required", false);
        $("#processing_time").prop("required", false);
        hide_all();
    }
}

$(document).ready(function() {
    view_form_helper("processing_protocol_id");
    $("#processing_protocol_id").on("change", function() {
        view_form_helper("processing_protocol_id");
    });



});

