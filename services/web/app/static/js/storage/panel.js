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

function get_panel_information() {
    var api_url = encodeURI(window.location+'/endpoint');
    
    var json = (function () {
        var json = null;
        $.ajax({
            'async': false,
            'global': false,
            'url': api_url,
            'dataType': "json",
            'success': function (data) {
                json = data;
            }
        });
        return json;
    })();

    return json["content"];
}


function render_counts(basic_statistics) {
    $("#site_count").html(basic_statistics["site_count"]);
    $("#room_count").html(basic_statistics["room_count"]);
    $("#building_count").html(basic_statistics["building_count"]);
    $("#cold_storage_count").html(basic_statistics["cold_storage_count"]);


}

function render_cold_storage_statistics(cold_storage_statistics) {
    make_pie("cold_storage_type", cold_storage_statistics["cold_storage_type"]["data"], cold_storage_statistics["cold_storage_type"]["labels"])
    make_pie("cold_storage_temp", cold_storage_statistics["cold_storage_temp"]["data"], cold_storage_statistics["cold_storage_temp"]["labels"])


}

$(document).ready(function() {
    $("body").css({"backgroundColor":"#eeeeee"});

    var panel_information = get_panel_information();
    render_counts(panel_information["basic_statistics"]);
    render_cold_storage_statistics(panel_information["cold_storage_statistics"]);
    $("#loading-screen").fadeOut();
    $("#content").delay(500).fadeIn();
});