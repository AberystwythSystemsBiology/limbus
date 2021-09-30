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

function get_donors(query) {
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


function calc_age(date0, date1) {
    date0 = new Date(date0 + "Z");
    date1 = new Date(date1 + "Z");
    var timeDiff = Math.abs(date0.getTime() - date1.getTime());
    var age = Math.ceil(timeDiff / (1000 * 3600 * 24)/ 365);
    return age;
}

function render_table(query) {
    var d = get_donors(query);
    $("#table_view").delay(300).fadeOut();
    $("#loading").fadeIn();

    $('#donor-table').DataTable({
        data: d,
        dom: 'Bfrtip',
        buttons: [ 'print', 'csv', 'colvis' ],
        columnDefs: [
            {targets: '_all', defaultContent: '-'},
            {targets: [1, 2, 3,  5, 6, 11, 12,  15], visible: false, "defaultContent": "-"},
        ],

        columns: [
            { // id,
                "mData": {},
                "mRender": function (data, type, row) {
                    var col_data = '';
                    col_data += render_colour(data["colour"])
                    col_data += "<a href='" + data["_links"]["self"] + "'>";
                    col_data += '<i class="fa fa-user-circle"></i> LIMBDON-'
                    col_data += data["id"];
                    col_data += "</a>";


                    return col_data
                }
            },

            {data: 'uuid'},//1
            {data: 'mpn'}, //2
            {data: 'enrollment_site_id'}, //3


            {   // consents
                "mData": {},
                "mRender": function (data, type, row) {
                    consents = data["consents"];
                    var col_data = '';
                    $.each(consents, function (index, consent) {
                        if (consent['withdrawn']==true) {
                            col_data += "<span style='color:indianred'>" + 'LIMBDC-' + consent['id'] + ': withdrawn' + "</span>";
                        } else {
                            col_data += "<span style='color:green'>" + 'LIMBDC-' + consent['id'] + "</span>";
                        }
                        if (index < (consents.length-1))
                             col_data += ', <br>';
                    });
                    return col_data;
                }
            },

            {   //samples 5
                "mData": {},
                "mRender": function (data, type, row) {
                    samples = data["samples"];
                    var col_data = '';
                    $.each(samples, function (index, sample) {
                        //var col_data = '';
                        col_data += render_colour(sample["colour"])
                        col_data += "<a href='" + sample["_links"]["self"] + "'>";
                        col_data += '<i class="fas fa-vial"></i> '
                        col_data += sample["uuid"];
                        col_data += "</a>";

                        var sample_type_information = sample["sample_type_information"];
                        if (sample["base_type"] == "Fluid") {
                            sample_type = sample_type_information["fluid_type"];
                        } else if (sample["base_type"] == "Cell") {
                            sample_type = sample_type_information["cellular_type"] + " > " + sample_type_information["tissue_type"];
                        } else if (sample["base_type"] == "Molecular") {
                            sample_type = sample_type_information["molecular_type"];
                        }

                        col_data += ': ['+ sample_type;
                        col_data += ', ' + sample['status'] + ', ';

                        col_data += sample["remaining_quantity"] + "/" + sample["quantity"] + get_metric(sample["base_type"]);
                        col_data += '</span>'
                        col_data += ']';

                        if (index < (samples.length-1))
                             col_data += ', <br>';
                    });
                    return col_data;
                }
            },

            {   // dob 6
                "mData": {},
                "mRender": function (data, type, row) {

                    var date = new Date(Date.parse(data['dob']));
                    const month = date.toLocaleString('default', { month: 'long' });
                    return month + ' ' + date.getFullYear();

                }
            },

            {data: 'registration_date'},

            { // Age at registration
                "mData": {},
                "mRender": function (data, type, row) {
                    age = calc_age(data['dob'], data['registration_date'])
                    return age;

                }
            },
            {
                "mData": {},
                "mRender": function (data, type, row) {
                    // Sex
                    return data["sex"];
                }
            },
            {data: 'race'},
            {data: 'weight'},
            {data: 'height'},
            {
                "mData": {},
                "mRender": function (data, type, row) {
                    // Status
                    return data["status"]
                }
            },
            { // Diagnoses 14
                "mData": {},
                "mRender": function (data, type, row) {
                    diagnoses = data["diagnoses"];
                    var col_data = '';
                    $.each(diagnoses, function (index, diagnosis) {
                        //var col_data = '';
                        col_data += diagnosis['diagnosis_date'] + ': ['
                        col_data += "<a href='" + diagnosis['doid_ref']["iri"] + "'>";
                        col_data += '<i class="fa fa-stethoscope"></i> '
                        col_data += diagnosis['doid_ref']["label"];
                        col_data += "</a>";
                        col_data += '</span>'
                        col_data += ']';

                        if (index < (diagnoses.length-1))
                             col_data += ', <br>';
                    });
                    return col_data;
                }
            },
            { // Created_on 15
                "mData": {},
                "mRender": function (data, type, row) {
                    return data["created_on"]
                },
            }

        ],

    });

    $("#loading").fadeOut();
    $("#table_view").delay(300).fadeIn();
    
}


function get_filters() {
    var filters = {

    }

    var f = ["sex", "status", "race"];

    $.each(f, function (_, filter) {
        var value = $("#" + filter).val();
        if (value && value != "None") {
            filters[filter] = value;
        }
    });

    return filters;


}


$(document).ready(function () {

    render_table({});

    $("#reset").click(function () {

        $('#donor-table').DataTable().destroy()
        render_table({});
    });

    $("#filter").click(function () {
        $("#table_view").fadeOut();
        $('#donor-table').DataTable().destroy()
        var filters = get_filters();
        render_table(filters);
    });


});