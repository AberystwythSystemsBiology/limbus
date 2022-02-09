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
    api_url += "/sample/shipment/new/data";

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


function get_user_cart(user_id=null) {
    var api_url = encodeURI(window.location.origin);
    //api_url += "/sample/shipment/new/data";
    if (user_id==null || user_id=='')
        api_url += "/sample/cart/data";
    else
        api_url += "/sample/cart/LIMBUSR-" + user_id + "/data";

    var json = (function () {
        var json = null;
        $.ajax({
            'async': false,
            'global': false,
            'url': api_url,
            'dataType': "json",
            'success': function (data) {
                json = data["content"];
            },
            'failure': function (data) {
                console.log("failure", data);
                json = data["message"];
            }
        });
        return json;
    })();

    return json;
}


function reassign_samples_to_cart(api_url, samples) {
    var msg = "Selected samples will be moved to a different user cart, select a user and press confirm to proceed!";
    let aModal = $("#cart-confirmation-modal");
    aModal.find(".modal-title").html("Sample to Cart Confirmation");
    aModal.find("p.confirm-msg").html(msg);
    aModal.find(".btn[type=submit]").show();
    aModal.modal({
        show: true
    });

    //aModal.find(".btn[type=submit]").on("submit", function () {
    aModal.find(".btn[type=submit]").on("click", function () {
        var new_user_id = $("#select_user_id").val();
        console.log("new ..", new_user_id);
        new_user_id = parseInt(new_user_id);
        aModal.find(".btn[type=submit]").hide();
        $("#select_user_id").hide();
        alert("ok");
        aModal.find("p.confirm-msg").html("Updating ...");
        aModal.modal({
            show: true
        });

        var json = (function () {
            var json = null;
            console.log(" sss", JSON.stringify({"samples": samples, "new_user_id": new_user_id}));
            console.log("api_url", api_url);

            $.ajax({
                'async': false,
                'global': false,
                'url': api_url,
                'type': 'POST',
                'dataType': "json",
                'data': JSON.stringify({"samples": samples, "new_user_id": new_user_id}),
                'contentType': 'application/json; charset=utf-8',
                'success': function (data) {
                    json = data;
                    aModal.find("p.confirm-msg").html(data["message"]);
                    $('#select_user_id').hide();
                    aModal.modal({
                        show: true
                    });
                },
                'failure': function (data) {
                    json = data;
                    console.log(data, 'bad');
                    $('#select_user_id').hide();
                    aModal.find("p.confirm-msg").html(data["message"]);
                    aModal.modal({
                        show: true
                    });
                }
            });

            return json;
        })();

        alert(json);
        return json;
    });

    return false;
}

function tocart_btn_logic(aTable, user_id) {
    $("#sample-to-cart-btn").click(function (event) {
        let rows_selected = aTable.rows( { selected: true } ).data();
        if (rows_selected.length>0) {
            var formdata = [];
            $.each(rows_selected, function (index, row) {
                delete row['__proto__'];
                console.log("row", row)
                formdata.push(row["sample"]["id"]);
            });

           var api_url = window.location.origin;
           api_url += "/sample/cart/LIMBUSR-" + user_id + "/reassign";
           console.log("ap: ", api_url);
           console.log("form", formdata);
           res = reassign_samples_to_cart(api_url, formdata);
           if (res.success == true) {
              window.location.href = window.location.origin + "/sample/cart/LIMBUSR-"+new_user_id;
           } /*else {
              window.location.href = window.location.reload();
           }*/
        } else {
            alert("No sample selected!");
        }

    });
};


function fill_titile(user_id) {
    if ([null, undefined, ""].includes(user_id))
        $('#div h1').html("My Sample Cart");

}


function cart_select_update(table, indexes, selected) {
        var rowData = table.rows(indexes).data().toArray();
        //console.log("rowData: ", rowData);

        var rows = [];
        let ids = new Set();
        let rack_ids = new Set();

        for (let rid in rowData) {
            var rowd = rowData[rid];
            if (rowd.selected !== selected) {
                rowd.selected = selected;
                ids.add(rowd["sample"]["id"]);
                if (rowd["storage_type"] === "RUC") {
                    rack_ids.add(rowd["rack"]["id"]);
                };
            };
        };

        //console.log("rack_id", rack_ids);
        let to_upd_rows = table.rows({selected: !selected, storage_type: "RUC"});
        to_upd_rows.every(function () {
            for(let rack_id of rack_ids) {
                if (this.data() !== undefined && this.data().storage_type === "RUC" && this.data().rack.id === rack_id) {
                    // only trigger the select/deselect event update database first in batch first and
                    this.data()["selected"] = selected;
                    ids.add(this.data()["sample"]["id"]);
                }
            }
        });

        for(let sample_id of ids) {
            rows.push({"id": sample_id, "selected": selected});
        };

        if (rows.length>0) {
            var json = null;
            var api_url = window.location + "/update/samples";
            console.log("api_url", api_url);

            $.post({
                'async': false,
                'global': false,
                'url': api_url,
                'contentType': 'application/json',
                'data': JSON.stringify({"samples": rows}),
                'success': function (data) {
                    json = data;
                },
                'failure': function (data) {
                    json = data;
                }
            });

            to_upd_rows.every(function () {
                for(let rack_id of rack_ids) {
                    if (this.data() !== undefined && this.data().storage_type === "RUC" && this.data().rack.id === rack_id) {
                        if (selected) {
                            this.select();
                        }
                        else {
                            this.deselect();
                        }
                    }
                }
            });


            return json;
        };

};

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
            {targets: [3], visible: false, "defaultContent": ""},
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
            {//Action Column
                "mData": {},
                "mRender": function (data, type, row) {

                    links_map[data["sample"]["id"]] = data["sample"]["_links"]

                    var remove_id = "remove-cart-" + data["sample"]["id"];
                    var api_url = window.location.href;

                    var actions = ""
                    actions += "<div id='" + remove_id + "' class='btn btn-sm btn-danger'>";
                    actions += "<i class='fa fa-trash'></i>"
                    actions += "</div>"
                    if (data["storage_type"] === "RUC") {
                        if (api_url.indexOf("LIMBUSR-")==-1) {
                            api_url = links_map[data["sample"]["id"]]["remove_rack_from_cart"];
                        }
                        else {
                            api_url += "/remove/LIMBRACK-" + data["rack"]["id"];
                        }

                        $("#" + remove_id).on("click", function () {
                            $('#delete-confirmation').modal('show')
                            document.getElementById("delete-confirmation-modal-title").innerHTML = "Remove LIMBRACK-" + data["rack"]["id"] + " From Cart?";
                            document.getElementById("delete-confirmation-modal-submit").href = api_url;
                            console.log("api_url", api_url);
                            alert("ok")
                        });
                    } else {


                        $("#" + remove_id).on("click", function () {
                            var id = $(this).attr("id").split("-")[2];
                            if (api_url.indexOf("LIMBUSR-")==-1) {
                                api_url = links_map[id]["remove_sample_from_cart"];
                            }
                            else {
                                api_url += "/" + data["sample"]["uuid"] + "/remove";
                            }
                            console.log("api_url", api_url);
                            alert("ok11")
                            $.ajax({
                                url: api_url,
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

    //Event for selecting a row
    //Selects all records which are in the same rack
    table.on('select', function (e, dt, type, indexes) {
        //console.log("select");
        cart_select_update(table, indexes, true);
    })
    .on('deselect', function (e, dt, type, indexes) {
        //console.log("deselect");
        cart_select_update(table, indexes, false);
    });
    return table;
}


$(document).ready(function () {
    //var cart = get_cart();
    var user_id = $("#user_id").text();
    fill_titile(user_id);
    var cart = get_user_cart(user_id);
    //console.log("cart:", cart);
    aTable = fill_cart_table(cart);
    rows = aTable.rows();
    rows.every(function () {
        if (this.data().selected) {
            this.select();
        }
    })

    tocart_btn_logic(aTable, parseInt(user_id));

});