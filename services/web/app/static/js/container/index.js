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

function get_containers(query) {
    var current_url = encodeURI(window.location);
    var split_url = current_url.split("/");
    split_url.pop()
    var api_url = split_url.join("/") + "/data"

    var json = (function () {
        var json = null;
        $.get({
            'async': false,
            'global': false,
            'url': api_url,
            'contentType': 'application/json',
            'success': function (data) {
                json = data;
            }
        });
        return json;
    })();



    return json["content"];
}


function fill_containers_table(containers) {
    $("#container-table").DataTable( {
        data: containers,
        dom: 'Bfrtip',
        buttons: [ 'print', 'csv', 'colvis' ],
        columnDefs: [
        ],
        columns: [
            {
                "mData": {},
                "mRender": function (data, type, row) {
                    var uuid = "";
                    uuid += '<a href="' + data["_links"]["self"] + '">'
                    uuid += '<i class="fa fa-dot-circle"></i> LIMBCT-';
                    uuid += data["id"];
                    uuid += ': '+ data["container"]["name"] +'</a>'
                    return uuid
                }
            },

            {
                "mData" : {},
                "mRender": function (data, type, row) {
                    return data["container"]["used_for"]
                }
            },
            {
                "mData" : {},
                "mRender": function (data, type, row) {
                    return data["created_on"]
                }
            },
            {
                "mData": {},
                "mRender": function (data, type, row) {
                    return render_author(data["author"])
                }
        }

        ],

    });
}


$(document).ready(function () {
    var containers = get_containers();
    fill_containers_table(containers);


});