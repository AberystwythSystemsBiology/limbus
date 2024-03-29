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


function render_table(query, hide_cols=[]) {

    let exp_cols = Array.from({length: 19}, (v, k) => k);
    exp_cols = exp_cols.filter(function (x) {
        return [0, 1].indexOf(x) < 0; //exclude select/user_cart columns
    });
    let inv_cols = [0, 7, 11, 16, ]; //[1, 2, 5, 6, 10, -1]; ;
    if (hide_cols.length > 0) {
        inv_cols = inv_cols.concat(hide_cols);
    }

    var d = get_donors(query);
    //console.log("donor_info", d);
    $("#table_view").delay(300).fadeOut();
    $("#loading").fadeIn();

    let aTable = $('#donor-table').DataTable({
        data: d,
        dom: 'Blfrtip',
        pageLength: 100,
        language: {
            buttons: {
                selectNone: '<i class="far fa-circle"></i> None',
                colvis: 'Column visibility',
    
            },
            searchPanes: {
                clearMessage: 'Clear Selections',
                collapse: {0: '<i class="fas fa-sliders-h"></i> Filter', _: '<i class="fas fa-sliders-h"> (%d)'},
                viewTotal: false,
                columns: [3, 4, 9, 10, 15,18]
            }

        },
        //buttons: [ 'filter','print', 'csv', 'colvis' ],
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
                
            },

            {
                extend: 'csv',
                footer: false,
            
            },
            'colvis',
        ],

        columnDefs: [
            {targets: '_all', defaultContent: '-'},

            // {targets: [0, 2, 3, 4, 6, 7, 12, 13,  16], visible: false, "defaultContent": "-"},
            {targets: [2 , 4, 6, 7, 13, 14, 17, 18], visible: false, "defaultContent": "-"},

           
          //  {targets: inv_cols, visible: false, "defaultContent": "-"},
            {
                targets: 0,
                orderable: true,
                //className: 'select-checkbox',
                searchable: false,
            },

            //{width: 200, targets: 6 }
            {
                searchPanes: {
                    options: [
                        {
                            label: 'Under 20',
                            value: function (data, type, row) {
                                age = calc_age(data['dob'], data['registration_date'])
                                return age < 20;
                            }
                        },
                        {
                            label: '20 to 30',
                            value: function (data, type, row) {
                                age = calc_age(data['dob'], data['registration_date'])
                                return age <= 30 && age >= 20;
                            
                            }
                        },
                         {
                            label: '30 to 40',
                            value: function (data, type, row) {
                                age = calc_age(data['dob'], data['registration_date'])
                                return age <= 40 && age >= 30;

                            
                            }
                        },
                         {
                            label: '40 to 50',
                            value: function (data, type, row) {
                                age = calc_age(data['dob'], data['registration_date'])
                                return age <= 50 && age >= 40;
                            
                            }
                        },
                         {
                            label: '50 to 60',
                            value: function (data, type, row) {
                                age = calc_age(data['dob'], data['registration_date'])
                                return age <= 60 && age >= 50;

                            }
                        },
                         {
                            label: 'Over 60',
                            value: function (data, type, row) {
                                age = calc_age(data['dob'], data['registration_date'])
                                return age > 60;
    
                            }
                        }
                    ]
                },
                targets: [9]

            },
            // Categorical search for BMI
            {
                searchPanes: {
                    options: [
                        {
                            label: 'Underweight < 18.5',
                            value: function (data, type, row) {
                                bmi = calc_bmi(data['weight'], data['height'])
                                return bmi < 18.5;
                            }
                        },
                        {
                            label: 'Normal < 25 ',
                            value: function (data, type, row) {
                                bmi = calc_bmi(data['weight'], data['height'])
                                return bmi < 25 && bmi >=  18.5 ;
                            }
                        },
                         {
                            label: 'Overweight < 30',
                            value: function (data, type, row) {
                                bmi = calc_bmi(data['weight'], data['height'])
                                return bmi < 30 && bmi >=  25 ;
                            }
                        },
                         {
                            label: 'Obese >= 30',
                            value: function (data, type, row) {
                                bmi = calc_bmi(data['weight'], data['height'])
                                return bmi >= 30 ;
                            }
                        }
                        
                       
                    ]
                },
                targets: [12]
            }
        ],
       
        //fixedColumns: true,
        order: [[0, 'desc']],

        columns: [
            {data: 'id'},//0
            { // id, 1
                "mData": {},
                "mRender": function (data, type, row) {
                  //  console.log("come ");
                    var col_data = '';
                    col_data += render_colour(data["colour"])
                    col_data += "<a href='" + data["_links"]["self"] + "'>";
                    col_data += '<i class="fa fa-user-circle"></i> LIMBDON-'
                    col_data += data["id"];
                    col_data += "</a>";

                    return col_data;
                }
            },

            {data: 'uuid'},//2
            {data: 'mpn'}, //3
            {data: 'enrollment_site_id'}, //4


            {   // consents 5
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

            {   //samples 6
                "mData": {},
                "mRender": function (data, type, row) {
                    samples = data["samples_new"];
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

            {   // dob 7
                "mData": {},
                "mRender": function (data, type, row) {

                    var date = new Date(Date.parse(data['dob']));
                    const month = date.toLocaleString('default', { month: 'long' });
                    return month + ' ' + date.getFullYear();

                }
            },

            {data: 'registration_date'},//8

            { // Age at registration 9
                "mData": {},
                "mRender": function (data, type, row) {
                    age = calc_age(data['dob'], data['registration_date'])
                    return age;

                }
            },
            {  // Sex 10
                "mData": {},
                "mRender": function (data, type, row) {
                    return data["sex"];
                }
            },
            {data: 'race'}, //11
            { // BMI 12
                "mData": {},
                "mRender": function (data, type, row) {
                    bmi = calc_bmi(data['weight'], data['height'])
                    if (isNaN(bmi)) {
                        bmi = null;
                    }
                    return bmi;

                }
            },
            {data: 'weight'}, //13
            {data: 'height'},   //14
            {  // Status 15
                "mData": {},
                "mRender": function (data, type, row) {
                    return data["status"]
                }
            },
            { // Diagnoses 16
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
            { // Created_on 17
                "mData": {},
                "mRender": function (data, type, row) {
                    return data["created_on"]
                },
            },
            // Disease Diagnosis 18
            //hidden column, Date deleted to ensure that each piece of data is not unique
            // to allow for searches based on diagnosis
        {
            "mData": {},
                "mRender": function (data, type, row) {
                    diagnoses = data["diagnoses"];
                    var col_data = '';
                    $.each(diagnoses, function (index, diagnosis) {
                        //var col_data = '';
                        
                        col_data += "<a href='" + diagnosis['doid_ref']["iri"] + "'>";
                        col_data += '<i class="fa fa-stethoscope"></i> '
                        col_data += diagnosis['doid_ref']["label"];
                        col_data += "</a>";
                       

                        if (index < (diagnoses.length-1))
                             col_data += ', <br>';
                    });
                    return col_data;
                }
        }

        ],

    });

    $("#loading").fadeOut();
    $("#table_view").delay(300).fadeIn();

}


function get_filters() {
    var filters = {

    }


    var f = ["sex", "status", "race", "enrollment_site_id", "diagnosis",
        "age_min", "age_max", "bmi_min", "bmi_max"];

/*    $.each(f, function (_, filter) {
        var value = $("#" + filter).val();
        if (value && value != "None") {
            filters[filter] = value;
        }
    });*/
    $.each(f, function(_, filter) {
        var value = $("#"+filter).val();
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

    //console.log("filters:", filters);
    return filters;


}


$(document).ready(function () {
    var filters = get_filters();
    //render_table({});
    render_table(filters);

    $("#reset").click(function () {

        $('#donor-table').DataTable().destroy()
        //render_table({});
        window.location.reload();
    });

    $("#filter").click(function () {
        $("#table_view").fadeOut();
        $('#donor-table').DataTable().destroy()
        var filters = get_filters();
        render_table(filters);
    });


});