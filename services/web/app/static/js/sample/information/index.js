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

function get_samples(query) {
    var current_url = encodeURI(window.location);
    var split_url = current_url.split("/");
    split_url.pop()
    var api_url = split_url.join("/") + "/query"
    
    var json = (function () {
        var json = null;
        $.post({
            'async': false,
            'global': false,
            'url': api_url,
            'contentType': 'application/json',
            'data': JSON.stringify(query),
            'success': function (data) {
                json = data;
            }
        });
        return json;
    })();
    
    

    return json["content"];
}


function render_table(query) {
    var d = get_samples(query);
    $("#table_view").delay(300).fadeOut();
    $("#loading").fadeIn();

    render_sample_table(d, "sampleTable")


    $("#loading").fadeOut();
    $("#table_view").delay(300).fadeIn();


}


function get_filters() {
    var filters = {

    }

    //var f = ["barcode", "type", "colour", "source", "status"];
    var f = ["barcode", "biohazard_level", "base_type", "colour", "source", "status", "protocol_id"];

    $.each(f, function(_, filter) {
        var value = $("#"+filter).val();
        if (value && value != "None") {
            filters[filter] = value;
        }
    });

    return filters;


}


$(document).ready(function() {

    render_table({});
    
    $("#reset").click(function() {

        $('#sampleTable').DataTable().destroy()
        render_table({});
    });

    $("#filter").click(function() {
        $("#table_view").fadeOut();
        $('#sampleTable').DataTable().destroy()
        var filters = get_filters();
        render_table(filters);
    });

    // $("#export").click(function() {
    //     //$("#table_view").fadeOut();
    //     //$('#sampleTable').DataTable().destroy()
    //     var filters = get_filters();
    //     render_table(filters);
    //
    // });


});