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

function get_shipments() {
    var current_url = encodeURI(window.location);
    var split_url = current_url.split("/");
    var api_url = split_url.join("/") + "/data"
    
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

function fill_shipments_table(shipments) {
    $("#shipment-table").DataTable( {
        data: shipments,
        dom: 'Bfrtip',
        buttons: [ 'print', 'csv', 'colvis' ],
        order: [[ 6, 'desc' ]],
        columnDefs: [
            {targets: '_all', defaultContent: ''},
        ],
        columns: [
            {
                "mData": {},
                "mRender": function (data, type, row) {
                    data = data["shipment"]
                    var uuid = "";
                    uuid += '<a href="' + data["_links"]["self"] + '">'
                    uuid += '<i class="fa fa-shipping-fast"></i> ';
                    uuid += data["uuid"];
                    uuid += '</a>'
                    return uuid
                }
            },

            {//To site Column
                "mData": {},
                "mRender": function (data, type, row) {
                    data = data["shipment"]
                    var col_data = '';
                    col_data += "<a href='" + data["new_site"]["_links"]["view_site"] + "'>";
                    col_data += "<i class='fa fa-hospital'></i>";
                    col_data += data["new_site"]["name"];
                    col_data += "</a>";
                    return col_data;
                }
            },
            {
                "mData" : {},
                "mRender": function (data, type, row) {
                    data = data["shipment"]
                    return data["involved_samples"].length
                }
            },

            {
                "mData" : {},
                "mRender": function (data, type, row) {
                    data = data["shipment"]
                    return data["comments"]
                }
            },
            {
                "mData" : {},
                "mRender": function (data, type, row) {
                    return data["status"]
                }
            },
            {
                "mData" : {},
                "mRender": function (data, type, row) {
                    return data["tracking_number"]
                }
            },

            {
                "mData" : {},
                "mRender": function (data, type, row) {
                    data = data["shipment"]
                    return data["created_on"]
                }
            },
            {
                "mData": {},
                "mRender": function (data, type, row) {
                    data = data["shipment"]
                    return render_author(data["author"])
                }
        }
        
        ],

    });
}

$(document).ready(function() {
    var shipments = get_shipments();
    fill_shipments_table(shipments);
});