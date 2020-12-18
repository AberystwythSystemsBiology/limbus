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

Date.prototype.toDateInputValue = (function() {
    var local = new Date(this);
    local.setMinutes(this.getMinutes() - this.getTimezoneOffset());
    return local.toJSON().slice(0,10);
});


function hide_disposal_information() {
    $("#disposal_date_div").hide();
    console.log(new Date().toDateInputValue());
    $("#disposal_date").val(new Date().toDateInputValue());
}

function show_disposal_information() {
    $("#disposal_date_div").show();
    $("#disposal_date").val("");
}

function logic() {
    if ($("#disposal_instruction option:selected").text() == "No Disposal") {
            hide_disposal_information();
        }

        else {
            show_disposal_information();
        }
}

$(document).ready(function() {
    logic();

    $("#disposal_instruction").change(function () {
        logic();
    });

});