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

function get_shelf_information() {
    var api_url = encodeURI(window.location + '/endpoint');

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

function render_subtitle(shelf_information) {
    $("#created-on").html(shelf_information["created_on"]);
    $("#created-by").html(shelf_information["author"]["first_name"] + " " + shelf_information["author"]["last_name"]);
    $("#storage-id").html(shelf_information["storage_id"]);
    $("#edit-details-btn").click(function() {
        window.location.href = shelf_information["_links"]["edit"];
    });

    $("#add-sample-btn").click(function() {
        window.location.href = shelf_information["_links"]["assign_samples_to_shelf"];
    });

    $("#add-rack-btn").click(function() {
        //window.location.href = shelf_information["_links"]["assign_rack_to_shelf"];
        window.location.href = shelf_information["_links"]["assign_racks_to_shelf"];

    })

}

function render_information(shelf_information) {
    var html = render_content("UUID", shelf_information["uuid"]);
    html += render_content("Name", shelf_information["name"]);
    html += render_content("Description", shelf_information["description"]);
    html += render_content("Location", shelf_information["location"])
    $("#shelf-information").html(html);
}


function render_rack_table(racks) {
    if (racks.length > 0) {
        
        $('#rack-table').DataTable( {
            data: racks,
            dom: 'Bfrtip',
            buttons: [ 'print', 'csv', 'colvis' ],
            columnDefs: [
                { targets: -3,
                visible:false}, { targets: -2, visible: false}
            ],
            columns: [
                {
                    "mData": {},
                    "mRender": function(data, type,row) {
                        var render_html = "<a href='" + data["_links"]["self"] + "'>"
                        render_html += render_colour(data["colour"]) + "LIMBRACK-" + data["id"];
                        render_html += "</a>"
                        return render_html
                    }
                },
                {
                    "mData": {},
                    "mRender": function(data, type,row) {
                        return data["serial_number"];
                    }
                },
                {
                    "mData": {},
                    "mRender": function(data, type,row) {
                        return data["sample_count"] + " / " + data["num_rows"]*data["num_cols"]; 
                    }
                },
             {
                    "mData": {},
                    "mRender": function (data, type, row) {
                        return data["uuid"];
                    }
                },
                
                {
                    "mData" : {},
                    "mRender": function (data, type, row) {
                        return data["author"]["first_name"] + " " + data["author"]["last_name"]
                
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

function render_sample_table(samples) {
    if (samples.length > 0) {

        $('#sample-table').DataTable({
            data: samples,
            dom: 'Blfrtip',
            buttons: ['print', 'csv', 'colvis'],
            lengthMenu: [ [5, 10, 25, 50, -1], [5, 10, 25, 50, "All"] ],
            //pageLength: 5,

            columnDefs: [
                {targets: '_all', defaultContent: ''},
                {targets: [2, 4, 5], visible: false, "defaultContent": ""},
            ],
            order: [[1, 'desc']],

            columns: [

            {
                "mData": {},
                "mRender": function (data, type, row) {
                    var col_data = '';
                    col_data += render_colour(data["colour"])
                    col_data += "<a href='" + data["_links"]["self"] + "'>";
                    col_data += '<i class="fas fa-vial"></i> '
                    col_data += data["uuid"];
                    col_data += "</a>";
                    if (data["source"] != "New") {

                        col_data += '</br><small class="text-muted"><i class="fa fa-directions"></i> ';
                        col_data += '<a href="' + data["parent"]["_links"]["self"] + '" target="_blank">'
                        col_data += '<i class="fas fa-vial"></i> ';
                        col_data += data["parent"]["uuid"],
                            col_data += "</a></small>";
                    }

                    return col_data
                }
            },
            {data: "id"},
            {data: "barcode"},
            {data: "status"},
            {data: "source"},
            {data: "base_type"},
            {
                "mData": {},
                "mRender": function (data, type, row) {
                    var sample_type_information = data["sample_type_information"];

                    if (data["base_type"] == "Fluid") {
                        return sample_type_information["fluid_type"];
                    } else if (data["base_type"] == "Cell") {
                        return sample_type_information["cellular_type"] + " > " + sample_type_information["tissue_type"];
                    } else if (data["base_type"] == "Molecular") {
                        return sample_type_information["molecular_type"];
                    }

                }
            },
            {
                "mData": {},
                "mRender": function (data, type, row) {
                    var sample_type_information = data["sample_type_information"];

                    if (sample_type_information["cellular_container"] == null) {
                        return sample_type_information["fluid_container"];
                    } else {
                        return sample_type_information["cellular_container"];
                    }

                }
            },
            {
                "mData": {},
                "mRender": function (data, type, row) {
                    var percentage = data["remaining_quantity"] / data["quantity"] * 100 + "%"
                    var col_data = '';
                    col_data += '<span data-toggle="tooltip" data-placement="top" title="' + percentage + ' Available">';
                    col_data += data["remaining_quantity"] + "/" + data["quantity"] + get_metric(data["base_type"]);
                    col_data += '</span>';
                    return col_data
                }
            },

            {
                "mData": {},
                "mRender": function (data, type, row) {
                    return data["created_on"];
                }
            },
            ],
        });
    }
    else {
        $("#sample-div").hide();
    }
}



$(document).ready(function () {
    var shelf_information = get_shelf_information();
    render_subtitle(shelf_information);
    render_information(shelf_information);
    render_rack_table(shelf_information["racks"]);
    render_sample_table(shelf_information["samples"]);
    $("#loading-screen").fadeOut();
    $("#content").delay(500).fadeIn();

});