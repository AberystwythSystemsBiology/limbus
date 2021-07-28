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

function get_cart() {
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

function fill_cart_table(cart) {

    var links_map = {};

    let table = $('#cart-table').DataTable( {
        data: cart,
        dom: 'Bfrtip',
        buttons: ['colvis','selectAll', 'selectNone'],
        lengthMenu: [ [5, 10, 25, 50, -1], [5, 10, 25, 50, "All"] ],
        //pageLength: 5,

        columnDefs: [
            {targets: '_all', defaultContent: ''},
            // {targets: [2, 3, 4], visible: false, "defaultContent": ""},
            {
                targets:  -1,
                orderable: false,
                className: 'select-checkbox',
            }

        ],
        order: [[1, 'desc']],
        select: {'style': 'multi',
            'selector': 'td:last-child',},
        columns: [
            {
                "mData": {},
                "mRender": function (data, type, row) {
                    var col_data = '';
                    col_data += render_colour(data["sample"]["colour"])
                    col_data += "<a href='"+data["sample"]["_links"]["self"]+ "'>";
                    col_data += '<i class="fas fa-vial"></i> '
                    col_data += data["sample"]["uuid"];
                    col_data += "</a>";
                    if (data["sample"]["source"] != "New") {

                    col_data += '</br><small class="text-muted"><i class="fa fa-directions"></i> ';
                    col_data += '<a href="'+data["sample"]["parent"]["_links"]["self"]+'" target="_blank">'
                    col_data += '<i class="fas fa-vial"></i> ';
                    col_data += data["sample"]["parent"]["uuid"],
                    col_data += "</a></small>";
                }

                    return col_data
                }
            },

            {
                "mData" : {},
                "mRender": function (data, type, row) {
                   return data["sample"]["base_type"]


                }
            },

            {
                "mData" : {},
                "mRender": function (data, type, row) {
                    var sample_type_information = data["sample"]["sample_type_information"];


                    if (data["sample"]["base_type"] == "Fluid") {
                        return sample_type_information["fluid_type"];
                    }
                    else if (data["sample"]["base_type"] == "Cell") {
                        return sample_type_information["cellular_type"] + " > " + sample_type_information["tissue_type"];
                    }


                }
            },
            {
                "mData": {},
                "mRender": function (data, type, row) {
                    var sample_type_information = data["sample"]["sample_type_information"];

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
                    var percentage = data["sample"]["remaining_quantity"] / data["sample"]["quantity"] * 100 + "%"
                    var col_data = '';
                    col_data += '<span data-toggle="tooltip" data-placement="top" title="'+percentage+' Available">';
                    col_data += data["sample"]["remaining_quantity"]+get_metric(data["sample"]["base_type"]); //+"/"+data["sample"]["quantity"]
                    col_data += '</span>';
                    return col_data
                }
        },
        {
            "mData": {},
            "mRender": function(data, type, row) {
                return data["sample"]["status"]

            },
        },
      {
        "mData": {},
        "mRender": function (data, type, row) {
            return data["created_on"]


        }
    },

            {
                "mData":{},
                "mRender": function (data,type,row) {
                    // console.log(data)
                    if (data["storage_type"] === "RUC"){
                        var col_data = '';
                        col_data += "<a href='" + data["rack"]["_links"]["self"] + "'>";
                        col_data += data["rack"]["serial_number"]
                        col_data += "</a>"
                        return col_data
                    }
                    else{
                        return "Not Stored"
                    }
                }
            },
    {
        "mData": {},
        "mRender": function (data, type, row) {

            links_map[data["sample"]["id"]] = data["sample"]["_links"]

            var remove_id = "remove-cart-" + data["sample"]["id"];

            var actions = ""
            actions += "<div id='"+remove_id+"' class='btn btn-sm btn-danger'>";
            actions += "<i class='fa fa-trash'></i>"
            actions += "</div>"
            if(data["storage_type"] === "RUC"){
                $("#" + remove_id).on("click", function () {
                    $('#delete-confirmation').modal('show')
                    document.getElementById("delete-confirmation-modal-title").innerHTML = "Remove LIMBRACK-"+data["rack"]["id"]+ " From Cart?";
                    document.getElementById("delete-confirmation-modal-submit").href = links_map[data["rack"]["id"]]["remove_rack_from_cart"];
                });
            }
            else {
                $("#" + remove_id).on("click", function () {
                    var id = $(this).attr("id").split("-")[2];
                    $.ajax({
                        url: links_map[id]["remove_sample_from_cart"],
                        type: 'DELETE',
                        success: function (response) {
                            json = response;
                            location.reload();
                        }
                    });
                });
            }
            return actions
        }
    },
            {} //check-box column
        ],

    });
    table.on( 'select', function ( e, dt, type, indexes ) {
            var rowData = table.rows(indexes).data().toArray();
            if (rowData[0]["storage_type"] === "RUC") {
                serial_num = rowData[0]["sample"]["storage"]["rack"]["serial_number"];
                unselected_rows = table.rows({selected: false});
                unselected_rows.every(
                    function (){
                        if(this.data() !== undefined&&this.data().storage_type === "RUC"  && this.data().sample.storage.rack.serial_number === serial_num){
                            this.select()
                        }
                    }
                );
            }
    } )
.on( 'deselect', function ( e, dt, type, indexes ) {
        var rowData = table.rows(indexes).data().toArray();
        if (rowData[0]["storage_type"] === "RUC") {
            serial_num = rowData[0]["sample"]["storage"]["rack"]["serial_number"];
            selected_rows = table.rows({selected: true});
            selected_rows.every(
                function (){
                    if(this.data() !== undefined && this.data().sample.storage.rack.serial_number === serial_num){
                        this.deselect()
                    }
                }
            );
        }
    } );

}


$(document).ready(function() {
    var cart = get_cart();
    fill_cart_table(cart);
});