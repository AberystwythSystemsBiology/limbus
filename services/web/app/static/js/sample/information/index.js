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
    split_url.pop();
    var api_url = split_url.join("/") + "/query";
    
    var json = (function () {
        var json = null;
        $.post({
            'async': false,
            'global': false,
            'url': api_url,
            'contentType': 'application/json',
            'data': JSON.stringify(query),
            'success': function (data) {
                //console.log(data);
                if (data instanceof String || typeof data === "string") {
                    json = JSON.parse(data);
                } else {
                    json = data;
                }
            }
        });
        return json;
    })();

    return json["content"];
}


function add_samples_to_cart(api_url, samples) {
    var msg = "Adding a sample to cart will remove it from storage, press Confirm to proceed!";
    let aModal = $("#cart-confirmation-modal");
    aModal.find(".modal-title").html("Sample to Cart Confirmation");
    aModal.find("p.confirm-msg").html(msg);
    aModal.find(".btn[type=submit]").show();
    aModal.modal({
        show: true
    });

    aModal.find(".btn[type=submit]").on("click", function () {
        aModal.find(".btn[type=submit]").hide();
        aModal.modal({
            show: true
        });
        var json = (function () {
            var json = null;
            $.ajax({
                'async': false,
                'global': false,
                'url': api_url,
                'type': 'POST',
                'dataType': "json",
                'data': JSON.stringify({"samples": samples}),
                'contentType': 'application/json; charset=utf-8',
                'success': function (data) {
                    json = data;
                    aModal.find("p.confirm-msg").html(data["message"]);
                    aModal.modal({
                        show: true
                    });
                },
                'failure': function (data) {
                    json = data;
                    aModal.find("p").html(data["message"]);
                    aModal.modal({
                        show: true
                    });
                }
            });
            return json;
        })();

        return json;
    });
    return false;
}

function tocart_btn_logic(aTable) {
    let rows_selected = aTable.rows( { selected: true } ).data();
    if (rows_selected.length>0) {
        $("#sample-to-cart-btn").show();

        $("#sample-to-cart-btn").click(function (event) {
               var formdata = [];
               $.each(rows_selected, function (index, row) {
                   delete row['__proto__'];
                   formdata.push(row)
               });
               var api_url = window.location.origin+ "/sample/to_cart";
               res = add_samples_to_cart(api_url, formdata);
               if (res.success == true) {
                   aTable.rows({selected: true}).deselect();
                   window.location.href = window.location.origin + "/sample/user/cart";
               }

        });

    } else {
        $("#sample-to-cart-btn").hide();
    }
}

function render_sample_table(samples, div_id, hide_cols=[]) {
    let exp_cols = Array.from({length: 18}, (v, k) => k);
    exp_cols = exp_cols.filter(function (x) {
        return [0, 1].indexOf(x) < 0; //exclude select/user_cart columns
    });

    let inv_cols = [3, 6, 7, 11, 15, 16, 17, 18]; //[1, 2, 5, 6, 10, -1]; ;
    if (hide_cols.length > 0) {
        inv_cols = inv_cols.concat(hide_cols);
    }

    $("#sample-to-cart-btn").hide();


    let aTable = $('#' + div_id).DataTable({
        data: samples,
        deferRender: true,
        dom: 'Bfrtlip',
        pageLength: 100,
        fixedHeader: true,

        language: {

        buttons: {
            selectNone: '<i class="far fa-circle"></i> None',
            colvis: 'Column',

        },
            searchPanes: {
                clearMessage: 'Clear Selections',
                collapse: {0: '<i class="fas fa-sliders-h"></i> Filter', _: '<i class="fas fa-sliders-h"> (%d)'}
            }


        },

        buttons: [
            //'selectAll',
            { // select all applied to filtered rows only
                text: '<i class="far fa-check-circle"></i> All', action: function () {
                    aTable.rows({search: 'applied'}).select();
                }
            },
            'selectNone',
 /*               searchPanes: {
                    show: false
                },
                targets: [1,2,3,4,14,16],*/
            {
                extend: 'searchPanes',
                config: {
                    cascadePanes: true
                },

            },

            {
                extend: 'print',
                exportOptions: {
                    columns: exp_cols
                }
            },

            {
                extend: 'csv',
                footer: false,
                exportOptions: {
                    columns: exp_cols
                    //columns: ':visible'
                }
            },
            'colvis',
        ],
        columnDefs: [
            {targets: '_all', defaultContent: ''},
            {targets: 1, defaultContent: '-'},
            {targets: inv_cols, visible: false, "defaultContent": ""},
            {
                targets: 0,
                orderable: false,
                className: 'select-checkbox',
                //searchable: false,
            },
        ],
        order: [[3, 'desc']],
        select: {
            'style': 'multi',
            'selector': 'td:first-child'
        },

        columns: [
            {}, //checkbox select column
            {
                "mData": {},
                "mRender": function (data, type, row) {
                    var col_data = "";
                    if (data["user_cart_info"] != undefined && data["user_cart_info"] != null) {
                        var cart_url = window.location.origin;
                        cart_url += "/sample/cart/LIMBUSR-" + data["user_cart_info"]["user_id"];
                        col_data += "<a href='" + cart_url + "'>";
                        col_data += '<i class="fa fa-shopping-cart" aria-hidden="true"></i>';
                        col_data += data["user_cart_info"]["user_name"];
                        col_data += "</a> ";
                    }
                    return col_data;
                }
            },
            {

                "mData": {},
                "mRender": function (data, type, row) {
                    var col_data = '';
                    col_data += render_colour(data["colour"])
                    col_data += "<a href='" + data["_links"]["self"] + "'>";
                    col_data += '<i class="fas fa-vial"></i> ';
                    col_data += data["uuid"];
                    col_data += "</a>";
                    if (data["source"] != "New") {

                        col_data += '</br><small class="text-muted"><i class="fa fa-directions"></i> ';
                        col_data += '<a href="' + data["parent"]["_links"]["self"] + '" target="_blank">';
                        col_data += '<i class="fas fa-vial"></i> ';
                        col_data += data["parent"]["uuid"];
                        col_data += "</a></small>";
                    }

                    return col_data;
                }
            },


            {data: "id"},
            {data: "barcode"},
            { // Donor ID
                "mData": {},
                "mRender": function (data, type, row) {
                    var consent = data['consent_information'];
                    col_data = "";
                    if (consent['donor_id'] != null) {
                        var donor_link = window.location.origin + '/donor/LIMBDON-' + consent['donor_id'];
                        col_data += '<a href="' + donor_link + '" target="_blank">';
                        col_data += '<i class="fa fa-user-circle"></i>' + 'LIMBDON-' + consent['donor_id'];
                        col_data += '</a>';
                    }
                    return col_data;
                }
            },

            { // Consent ID
                "mData": {},
                "mRender": function (data, type, row) {
                    var consent = data['consent_information'];
                    return 'LIMBDC-' + consent['id'];
                }
            },
            { // Consent status
                "mData": {},
                "mRender": function (data, type, row) {
                    var consent = data['consent_information'];
                    var consent_status = 'Active';
                    if (consent['withdrawn'] == true) {
                        consent_status = 'Withdrawn';
                    }
                    return consent_status;
                }
            },

            { // study ID
                "mData": {},
                "mRender": function (data, type, row) {
                    var consent = data['consent_information'];
                    var col_data = "";

                    if (consent['study'] != undefined && consent['study'] != null) {
                        doi = consent['study']['protocol']['doi'];
                        if (doi == null)
                            doi = "";

                        protocol_name = consent['study']['protocol']['name'];
                        if (protocol_name == null)
                            protocol_name = "";

                        col_data += '<a href="' + doi2url(doi) + '" target="_blank">';
                        // col_data += doi;
                        col_data += '<i class="fas fa-users"></i>' + protocol_name;
                        col_data += '</a>';

                    }
                    return col_data;
                }
            },

            { // donor reference no
                "mData": {},
                "mRender": function (data, type, row) {
                    var consent = data['consent_information'];
                    var reference_id = "";
                    if (consent['study'] != undefined && consent['study'] != null) {
                        reference_id = consent['study']['reference_id']
                    }
                    return reference_id;
                }
            },

            {data: "status"},

            {data: "base_type"},
            {
                "mData": {},
                "mRender": function (data, type, row) {
                    var sample_type_information = data["sample_type_information"];

                    if (data["base_type"] == "Fluid") {
                        return sample_type_information["fluid_type"];
                    } else if (data["base_type"] == "Cell") {
                        return sample_type_information["cellular_type"] + " > " + sample_type_information["fixation_type"];
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
                    var col_data = "";
                    if (data["attributes"] != undefined && data["attributes"].length > 0) {
                        data["attributes"].forEach( function(att) {
                            if (col_data != "") {
                                col_data +=" | ";
                            }
                            col_data += att["attribute"]["term"] + ": ";
                            if (att["data"] != undefined && att["data"] != null) {
                                col_data += att["data"];
                            }
                            if (att["option"] != undefined && att["option"] != null) {
                                col_data += att["option"]["term"];
                            }

                        })
                    }
                    return col_data;
                }
            },

            {
                "mData": {},
                "mRender": function (data, type, row) {
                    var storage_data = data["storage"];

                    if (storage_data == null) {
                        return "<span class='text-muted'>Not stored.</span>"
                    } else if (storage_data["storage_type"] == "STB") {
                        var rack_info = storage_data["rack"];
                        var html = "<a href='" + rack_info["_links"]["self"] + "'>";
                        html += "<i class='fa fa-grip-vertical'></i> LIMBRACK-" + rack_info["id"];
                        html += "</a>"
                        return html
                    } else if (storage_data["storage_type"] == "STS") {
                        var shelf_info = storage_data["shelf"];
                        var html = "<a href='" + shelf_info["_links"]["self"] + "'>";
                        html += "<i class='fa fa-bars'></i> LIMBSHF-" + shelf_info["id"];
                        html += "</a>"
                        return html
                    }
                    return data["storage"]
                }
            },
            {data: "current_site_id"},
            {data: "site_id"},
            {
                "mData": {},
                "mRender": function (data, type, row) {
                    return data["created_on"]
                }
            },

        ],


    });


    aTable.on('select', function (e, dt, type, indexes) {
        tocart_btn_logic(aTable);

    });

    aTable.on('deselect', function (e, dt, type, indexes) {
        tocart_btn_logic(aTable);
    });

};


function render_table(filters) {
    var startTime = performance.now()
    let d = get_samples(filters);
    var endTime = performance.now()
    console.log(`Call to get_samples took ${endTime - startTime} milliseconds`)
    // console.log("samples", d)
    $("#table_view").delay(300).fadeOut();
    $("#loading").fadeIn();

    let hide_cols = [1]; // hide user_cart column
    if ("reminder_type" in filters) {
        hide_cols=[];
    }

    var startTime = performance.now()
    render_sample_table(d, "sampleTable", hide_cols);
    var endTime = performance.now()
    console.log(`Call to rendertable took ${endTime - startTime} milliseconds`)

    $("#loading").fadeOut();
    $("#table_view").delay(300).fadeIn();

}

function get_filters() {
    var filters = {};

    var f = ["reminder_type", "barcode", "biohazard_level", "base_type", "sample_type", "colour", "source",
            "status", "current_site_id", "consent_status", "consent_type", "not_consent_type",
            "protocol_id", "source_study"];

    $.each(f, function(_, filter) {
        var value = $("#"+filter).val();
        //console.log('f', filter);
        // if (typeof(value) == 'string' && filter == "current_site_id") {
        // // Multiple site selection
        //         value = value.split(",");
        //         filters[filter] = value;
        // } else
        if (typeof(value) == 'object') {
            if (value.length>0) {
                filters[filter] = value.join();
            }
        } else {
            if (value && value != "None") {
                filters[filter] = value;
            }
        }
    });

    return filters;

}


$(document).ready(function() {
    var filters = get_filters();
    //console.log("filter: ", filters)
    //render_table({});
    render_table(filters);
    
    $("#reset").click(function() {

        $('#sampleTable').DataTable().destroy();
        //render_table({});
        window.location.reload();
    });

    $("#filter").click(function() {
        $("#table_view").fadeOut();
        $('#sampleTable').DataTable().destroy();
        var filters = get_filters();
        //console.log("filter: ", filters)
        render_table(filters);
    });

    $("#reminder_type").change(function() {
        $("#table_view").fadeOut();
        $('#sampleTable').DataTable().destroy();
        var filters = get_filters();
        render_table(filters);
    });
    $("#filter-bell-btn").click(function() {
        $("#table_view").fadeOut();
        $('#sampleTable').DataTable().destroy();
        var filters = get_filters();
        render_table(filters);
    });


});