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


function update_shelf_list(shelves, site_id){
    var choices = shelves[site_id];
    var options = "";
    //console.log("choices", choices);
    if (choices != undefined) {
        choices.forEach(function (value, index) {
            options += '<option value="' + parseInt(value[0]) + '">' + value[1] + '</option>';
        });
        //console.log("options", options);
        $("#shelf_id").empty().append(options);
        $("#shelf_id").val(choices[0][0]).change();

    } else {
        options += '<option value="' + 0 + '">' + "-- No shelf for the site --" + '</option>';
        $("#shelf_id").empty().append(options);
        $("#shelf_id").val(0).change();
    }
}


function site_shelf_selection_logic(shelves) {
        var site_id = $("#site_id").val();
            update_shelf_list(shelves, site_id);

    $("#site_id").change(function(){

            var site_id = $("#site_id").val();
            console.log("site_", site_id, shelves);
            update_shelf_list(shelves, site_id);
        }
    );

}


$(document).ready(function() {
    var shelves = JSON.parse(sessionStorage.getItem("shelves"));

    site_shelf_selection_logic(shelves);

});