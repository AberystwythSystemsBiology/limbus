/*
Copyright (C) 2021 Keiron O'Shea <keo7@aber.ac.uk>

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


function check_and_apply(sample_type) {
    if (sample_type == "CEL") {
        $(".quantity-text").html("Cells");
    }
    else if (sample_type == "MOL") {
        $(".quantity-text").html("&mu;g/mL");
    }
    else {
        $(".quantity-text").html("mL");
    }
}

$(document).ready(function() {
    var sample_type = $("#sample-type-hidden").text()
    check_and_apply(sample_type);

});