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

function check_status() {
    if ($("#status").val() == "DE") {
        $("#death_date_div").show();
    } 
    else {
        $("#death_date_div").hide();
        // $('#death_date').val('');
    }
}   




function assign_age() {
    var month = $("#month").val();
    var year = $("#year").val();
    $("#years").html(calculate_age(month, year));
}


$(document).ready(function(){
    check_status();

    assign_age();

    $("#month").change(function() {
        assign_age();
    });

    $("#year").change(function() {
        assign_age();
    });

    $("#status").change(function() {
        //assign_age();
        check_status();
      });

});
  