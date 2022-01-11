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
    var api_url = encodeURI(window.location.origin);
    api_url += "/sample/cart/data";

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

    let table = $('#cart-table').DataTable({
        data: cart,
        dom: 'Blfrtip',
        buttons: ['colvis', 'selectAll', 'selectNone'],
        lengthMenu: [[5, 10, 25, 50, -1], [5, 10, 25, 50, "All"]],
        //pageLength: 5,

        columnDefs: [
            {targets: '_all', defaultContent: ''},
            {targets: [3,5,10], visible: false, "defaultContent": ""},
            {
                targets: -1,
                orderable: false,
                className: 'select-checkbox',
            }

        ],
        order: [[1, 'desc']],
        select: {
            'style': 'multi',
            'selector': 'td:last-child',

        },
        columns: [
            {//Sample ID Column
                "mData": {},
                "mRender": function (data, type, row) {
                    var col_data = '';
                    col_data += render_colour(data["sample"]["colour"])
                    col_data += "<a href='" + data["sample"]["_links"]["self"] + "'>";
                    col_data += '<i class="fas fa-vial"></i> '
                    col_data += data["sample"]["uuid"];
                    col_data += "</a>";
                    if (data["sample"]["source"] != "New") {

                        col_data += '</br><small class="text-muted"><i class="fa fa-directions"></i> ';
                        col_data += '<a href="' + data["sample"]["parent"]["_links"]["self"] + '" target="_blank">'
                        col_data += '<i class="fas fa-vial"></i> ';
                        col_data += data["sample"]["parent"]["uuid"],
                            col_data += "</a></small>";
                    }

                    return col_data
                }
            },

            { // Disposal
                "mData": {},
                "mRender": function (data, type, row) {
                    var disposal = data["sample"]["disposal_information"];
                    if (disposal != null) {
                        var disposal_date = disposal['disposal_date'];
                        disposal_info = ['LIMBDSP-' + disposal['id'] + ": " + disposal_date, disposal["instruction"]].join(" | ");
                        return disposal_info;
                    }
                    return "";
                }
            },

            { // Linked review
                "mData": {},
                "mRender": function (data, type, row) {
                    var disposal = data["sample"]['disposal_information'];
                    var review_event = "";
                    if (disposal != null) {
                        review = disposal["review_event"];
                        if ( review != undefined && review != null ) {
                           review_event = "LIMBREV-"+[review["id"], review["result"], review["review_type"], review["quality"]].join(" | ");
                        }
                    }
                    return review_event;
                }
            },

            { // Consent ID
                "mData": {},
                "mRender": function (data, type, row) {
                    var consent = data["sample"]['consent_information'];
                    return 'LIMBDC-' + consent['id'];
                }
            },

            { // Consent status
                "mData": {},
                "mRender": function (data, type, row) {
                    var consent = data["sample"]['consent_information'];
                    var consent_status = 'Active';
                    if (consent['withdrawn'] == true) {
                        consent_status = 'Withdrawn';
                    }
                    return consent_status;
                }
            },

            {//Base Type Column
                "mData": {},
                "mRender": function (data, type, row) {
                    return data["sample"]["base_type"]


                }
            },

            {//Sample Type Column
                "mData": {},
                "mRender": function (data, type, row) {
                    var sample_type_information = data["sample"]["sample_type_information"];


                    if (data["sample"]["base_type"] == "Fluid") {
                        return sample_type_information["fluid_type"];
                    } else if (data["sample"]["base_type"] == "Cell") {
                        return sample_type_information["cellular_type"] + " > " + sample_type_information["tissue_type"];
                    }


                }
            },
            {//Container Column
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
            {//Quantity Column
                "mData": {},
                "mRender": function (data, type, row) {
                    var percentage = data["sample"]["remaining_quantity"] / data["sample"]["quantity"] * 100 + "%"
                    var col_data = '';
                    col_data += '<span data-toggle="tooltip" data-placement="top" title="' + percentage + ' Available">';
                    col_data += data["sample"]["remaining_quantity"] + get_metric(data["sample"]["base_type"]); //+"/"+data["sample"]["quantity"]
                    col_data += '</span>';
                    return col_data
                }
            },
            {//Shipping Status Column
                "mData": {},
                "mRender": function (data, type, row) {
                    return data["sample"]["status"]

                },
            },
            {//Created On column
                "mData": {},
                "mRender": function (data, type, row) {
                    return data["created_on"]


                }
            },

            {//Location Column
                "mData": {},
                "mRender": function (data, type, row) {
                    if (data["storage_type"] === "RUC") {
                        var col_data = '';
                        col_data += "<a href='" + data["rack"]["_links"]["self"] + "'>";
                        col_data += "<i class='fa fa-grip-vertical'></i>";
                        col_data += " LIMBRACK-" + data["rack"]["id"];
                        col_data += "</a>";
                        return col_data;
                    } else {
                        return "Not Stored";
                    }
                }
            },
/*            {//Action Column
                "mData": {},
                "mRender": function (data, type, row) {

                    links_map[data["sample"]["id"]] = data["sample"]["_links"]

                    var remove_id = "remove-cart-" + data["sample"]["id"];

                    var actions = ""
                    actions += "<div id='" + remove_id + "' class='btn btn-sm btn-danger'>";
                    actions += "<i class='fa fa-trash'></i>"
                    actions += "</div>"
                    if (data["storage_type"] === "RUC") {
                        $("#" + remove_id).on("click", function () {
                            $('#delete-confirmation').modal('show')
                            document.getElementById("delete-confirmation-modal-title").innerHTML = "Remove LIMBRACK-" + data["rack"]["id"] + " From Cart?";
                            document.getElementById("delete-confirmation-modal-submit").href = links_map[data["sample"]["id"]]["remove_rack_from_cart"];
                        });
                    } else {
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
            },*/
            {} //check-box column
        ],

    });
    //Event for selecting a row
    //Selects all records which are in the same rack
    table.on('select', function (e, dt, type, indexes) {
        var rowData = table.rows(indexes).data().toArray();

        //Change state of selected attribute
        rowData[0]['selected'] = true;
        var res;
        var api_url = window.location.origin + "/sample/shipment/cart/select";
        $.post({
            'async': false,
            'global': false,
            'url': api_url,
            'contentType': 'application/json',
            'data': JSON.stringify(rowData[0]),
            'success': function (data) {
                res = data;
            }
        });

        if (rowData[0]["storage_type"] === "RUC") {
            serial_num = rowData[0]["sample"]["storage"]["rack"]["serial_number"];
            unselected_rows = table.rows({selected: false});
            unselected_rows.every(
                function () {
                    if (this.data() !== undefined && this.data().storage_type === "RUC" && this.data().sample.storage.rack.serial_number === serial_num) {
                        this.select()
                    }
                }
            );
        }
    })  //Event for deselecting a row
        //Deselects all records which are in the same rack
        .on('deselect', function (e, dt, type, indexes) {
            var rowData = table.rows(indexes).data().toArray();

            //Change state of selected attribute
            rowData[0]['selected'] = false;
            var res;
            var api_url = window.location.origin + "/sample/shipment/cart/deselect";
            $.post({
                'async': false,
                'global': false,
                'url': api_url,
                'contentType': 'application/json',
                'data': JSON.stringify(rowData[0]),
                'success': function (data) {
                    res = data;
                }
            });

            if (rowData[0]["storage_type"] === "RUC") {
                serial_num = rowData[0]["sample"]["storage"]["rack"]["serial_number"];
                selected_rows = table.rows({selected: true});
                selected_rows.every(
                    function () {
                        if (this.data() !== undefined && this.data().storage_type === "RUC" && this.data().sample.storage.rack.serial_number === serial_num) {
                            this.deselect()
                        }
                    }
                );
            }
        });
    return table;
}

/*function checkDisposal(data) {
  var disposal_instr = false;
  try {
      disposal_date = data["sample"]["disposal_info"]["disposal_date"];
      disposal_instr =  (disposal_date != undefined && disposal_date != null);
  } catch {
      disposal_instr = false;
  }
  return disposal_instr;
}

function checkSelected(data) {
    var selected = false;
    try {
        var selected = data["selected"];
    } catch {
        selected = false;
    }
    return selected;
}*/

$(document).ready(function () {
    var cart = get_cart();
    //console.log("cart:", cart);
    //cart = cart.filter(checkSelected);
    //cart = cart.filter(checkDisposal);
    table = fill_cart_table(cart);
    rows = table.rows();
    rows.every(function () {
        if (this.data().selected) {
            this.select();
        }
    })

    $("#form-check").on("input", function(){
        var num_selected = table.rows( { selected: true } ).count();
        if (num_selected == $(this).val()) {
            $("#submit").prop('disabled', false)
        }
        else {
            $("#submit").prop('disabled', true)
        }
    });
});