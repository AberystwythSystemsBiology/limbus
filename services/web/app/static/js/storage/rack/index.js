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

function get_rack_information() {
    var api_url = encodeURI(window.location.origin + '/storage/rack/endpoint');
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


function render_rack_table(racks) {
    if (racks.length > 0) {

        $('#rack-table').DataTable( {
            data: racks,
            dom: 'Blfrtip',
            buttons: [ 'print', 'csv', 'colvis' ],
            lengthMenu: [ [10, 25, 50, -1], [10, 25, 50, "All"] ],
            columnDefs: [
                {targets: '_all', defaultContent: ''},
                {targets: [0, 3], visible:false},
            ],
            order: [[0, "desc"]],
            columns: [
                {data: "id", width: "1%" },
                { //rack
                    "mData": {},
                    "mRender": function(data, type,row) {
                        var render_html = "";
                        render_html += "<a href='" + data["_links"]["self"] + "'>"
                        render_html += render_colour(data["colour"]) + '<i class="fa fa-grip-vertical"></i>'
                        render_html += "LIMBRACK-" + data["id"];
                        render_html += "</a>"
                        return render_html
                    }
                },
                // {data: "description"},
                { //serial
                    "mData": {},
                    "mRender": function(data, type,row) {
                        return data["serial_number"];
                    }
                },
                {data: "uuid"},

                { // dimension
                    "mData": {},
                    "mRender": function(data, type,row) {
                        return data["num_rows"] + " x " + data["num_cols"];
                    }
                },

                { // occupancy
                    "mData": {},
                    "mRender": function(data, type,row) {
                        return data["sample_count"] + " / " + data["num_rows"]*data["num_cols"];
                    }
                },
             {
                    "mData": {},
                    "mRender": function (data, type, row) {
                        var render_html = "";
                        if (data["shelf"]!=null) {
                            render_html += "<a href='" + data["shelf"]["_links"]["self"] + "'>"
                            render_html += '<i class="fa fa-bars"></i>'
                            render_html += "LIMBSHF-" + data["shelf"]["id"];
                            render_html += "</a>";
                            render_html += "  " + data["shelf"]["name"];
                        }
                        return render_html;
                    }
                },

                { // compartment
                    "mData": {},
                    "mRender": function(data, type,row) {
                        var compartment = "";
                        if (data["rack_to_shelf"]!=null) {
                            try {
                                if (data["rack_to_shelf"]["row"] != null) {
                                    compartment = data["rack_to_shelf"]["row"];
                                    compartment = num2alpha(parseInt(compartment));
                                }
                            } catch (err) {
                                console.log(err);
                            }

                            try {
                                if (data["rack_to_shelf"]["col"] != null) {
/*                                    if (compartment != "") {
                                        compartment += ".";
                                    }*/
                                    compartment += data["rack_to_shelf"]["col"].toString();
                                }
                            } catch (err) {
                                console.log(err);
                            }
                        }
                        return compartment;
                    }
                },

                {
                    "mData" : {},
                    "mRender": function (data, type, row) {
                        return data["author"]["first_name"] + " " + data["author"]["last_name"];
                    }
                },
                {
                    "mData": {},
                    "mRender": function (data, type, row) {
                        return data["created_on"]
                    }
                },

            ],

        });
    }
    else {
        $("#sample-rack-div").hide();
    }
}

$(document).ready(function () {
    var rack_information = get_rack_information();
    render_rack_table(rack_information);
    $("#loading-screen").fadeOut();
    $("#content").delay(500).fadeIn();

});