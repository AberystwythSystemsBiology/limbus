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


function get_shipment() {
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

function fill_jumbotron(shipment_data) {
    $("#created-on").html(shipment_data["shipment"]["created_on"]);
    $("#author").html(render_author(shipment_data["shipment"]["author"]));

}

function fill_table(shipment_data) {
    html = ""
    h1 = '<a href="' + shipment_data["shipment"]["new_site"]['_links']['view_site'] + '">'
    h1 += '<i class="fa fa-hospital"></i>'
    h1 += shipment_data["shipment"]["new_site"]["name"]
    h1 += '</a>'
    html += render_content("Shipping destination", h1);

    html += render_content("Created Date", shipment_data["shipment"]["created_on"]);
    html += render_content("Comments", shipment_data["shipment"]["comments"]);

    $("#basic-information").html(html);

    html= ""
    html += render_content("Status",shipment_data["status"])
    html += render_content("Tracking number",shipment_data["tracking_number"])
    html += render_content("Comments",shipment_data["comments"])
    html += render_content("Updated Date/Time", shipment_data["datetime"].split("T").join(" "));
    $('#shipment-status-information').html(html);
}


function hide_all() {
    $("#basic-info-div").fadeOut(50);
    $("#involved-samples-div").fadeOut(50);
    $("#shipment-status-div").fadeOut(50);
}


function deactivate_nav() {
    $("#basic-info-nav").removeClass("active");
    $("#involved-samples-nav").removeClass("active");
    $("#shipment-status-nav").removeClass("active");
}

function fill_involved_samples0(involved_samples, new_site) {
    var html = "";
    for (i in involved_samples) {
        var inv = involved_samples[i];
        html += '<li class="list-group-item"> '
        html += '<a href="' + inv["sample"]["_links"]["self"] + '">'
        html += '<i class="fas fa-vial"></i>'
        html += inv["sample"]["uuid"]
        html += '</a>'
        html += '<p>'
        html +=  inv["old_site"]["name"] + '->' + new_site["name"]
        html += '</p>'

        html += '</li>'
    }

    $("#involved-samples-list-group").html(html);
}

function fill_involved_samples(involved_samples) {

    var links_map = {};

    let table = $('#involved-samples-table').DataTable({
        data: involved_samples,
        dom: 'Bfrtip',
        buttons: ['csv', 'print', 'colvis'],
        order: [[11, 'desc']],
        lengthMenu: [[5, 10, 25, 50, -1], [5, 10, 25, 50, "All"]],
        //pageLength: 5,

        columnDefs: [
            {targets: '_all', defaultContent: ''},
            {targets: [1, 2, 3, 6], visible: false, "defaultContent": ""},

        ],
        order: [[2, 'desc']],
        select: {
            'style': 'multi',
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

            {//DB ID Column
                "mData": {},
                "mRender": function (data, type, row) {
                    return data["sample"]["id"]

                },
            },
            {//DB ID Column
                "mData": {},
                "mRender": function (data, type, row) {
                    return data["sample"]["barcode"]

                },
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
            {//Source Column
                "mData": {},
                "mRender": function (data, type, row) {
                    return data["sample"]["source"]

                },
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
            {//Sample Status Column
                "mData": {},
                "mRender": function (data, type, row) {
                    return data["sample"]["status"]

                },
            },

            {//Location Column
                "mData": {},
                "mRender": function (data, type, row) {
                    data = data["sample"]["storage"]
                    if (data === null) {
                        return "";
                    }
                    else if (data["storage_type"] === 'STB') {
                        var col_data = '';
                        col_data += "<a href='" + data["rack"]["_links"]["self"] + "'>";
                        col_data += "<i class='fa fa-grip-vertical'></i>";
                        col_data += " LIMBRACK-" + data["rack"]["id"];
                        col_data += "</a>";
                        return col_data;
                    } else {
                        return "";
                    }
                }
            },

            {//From site Column
                "mData": {},
                "mRender": function (data, type, row) {
                    var col_data = '';
                    col_data += "<a href='" + data["old_site"]["_links"]["view_site"] + "'>";
                    col_data += "<i class='fa fa-hospital'></i>";
                    col_data += data["old_site"]["name"];
                    col_data += "</a>";
                    return col_data;
                }
            },

            {//Created On column
                "mData": {},
                "mRender": function (data, type, row) {
                    return data['sample']["created_on"]

                }
            },

        ],

    });
    return table;
}

$(document).ready(function() {
    var shipment_data = get_shipment();

    $("#loading-screen").fadeOut();
    fill_jumbotron(shipment_data);
    fill_table(shipment_data);
    //fill_involved_samples(shipment_data['shipment']["involved_samples"], shipment_data['shipment']["new_site"]);
    fill_involved_samples(shipment_data['shipment']["involved_samples"]);
    $("#content").delay(500).fadeIn();

    $("#basic-info-nav").on("click", function () {
        deactivate_nav();
        $(this).addClass("active");
        hide_all();
        $("#basic-info-div").fadeIn(100);
    });

    $("#involved-samples-nav").on("click", function () {
        deactivate_nav();
        $(this).addClass("active");
        hide_all();
        $("#involved-samples-div").fadeIn(100);
    });

    $("#shipment-status-nav").on("click", function () {
        deactivate_nav();
        $(this).addClass("active");
        hide_all();
        $("#shipment-status-div").fadeIn(100);
    });

});