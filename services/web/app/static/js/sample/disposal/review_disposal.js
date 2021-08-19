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

function disposal_logic() {
    var disposal = new Set(["DES","TRA"]);
    if (disposal.has($("#disposal_instruction option:selected").val())) {
        $("#disposal_date_div").show();
    } else {
        $("#disposal_date").val("");
        $("#disposal_date_div").hide();
    }
}


function disposal_edit_switch() {
    var disposal_edit_on = $('#disposal_edit_on').prop('checked');
    if (disposal_edit_on) {
        $("#disposal_edit_fields").show();
        disposal_logic();
    } else {
        $("#disposal_edit_fields").hide();
    }
}


$(document).ready(function() {
    disposal_logic();
    disposal_edit_switch();
    $("#disposal_edit_on").on("change", function() {
        disposal_edit_switch();
    });

    $("#disposal_instruction").on("change", function() {
        disposal_logic();
    });

});