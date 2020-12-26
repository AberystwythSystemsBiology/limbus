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

function measurement() {
    if ($("#requires_measurement").is(":checked")) {
        $("#measurement_div").show();
    }

    else {
        $("#measurement_div").hide();
    }
}

function symbol() {
    if ($("#requires_symbol").is(":checked")) {
        $("#symbol_div").show();
    }

    else {
        $("#symbol_div").hide();
    }
}

$(document).ready(function () {
    measurement();
    symbol();

    $("#requires_symbol, #requires_measurement").change(function () {
        measurement();
        symbol();
    });
});