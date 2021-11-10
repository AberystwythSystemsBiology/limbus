function render_sample_table(samples) {

    if (samples.length > 0) {

        $('#sampleTable').DataTable( {
            data: samples,
            rowCallback: function(row, data, index){
                if(data['tostore']){
                    $(row).find('td:eq(0)').css('background-color', 'lightblue');
                } else {
                    $(row).find('td:eq(0)').css('background-color', 'lightpink');
                }
            },
            dom: 'Blfrtip',
            buttons: [ 'print', 'csv', 'colvis' ],
            lengthMenu: [ [5, 10, 25, 50, -1], [5, 10, 25, 50, "All"] ],
            pageLength: -1,
            columnDefs: [
                {targets: '_all', defaultContent: ''},
                {targets: [0, 4, 5, 9, -2,-1], visible: false, "defaultContent": ""},
            ],
            order: [[0, 'asc']],
            columns: [
                { // col id
                    "mData": {},
                    "mRender": function(data, type,row) {
                        return data["pos"][1]
                    },
                    "width": "3%"
                },

                { // pos
                    "mData": {},
                    "mRender": function(data, type,row) {
                        tick = String.fromCharCode(Number(data["pos"][0])+64);
                        return tick + data["pos"][1]
                    },
                    "width": "3%"
                },

            {"mData": {}, "mRender": function (data) {
                if (data["sample"]["id"]==null) {

                    try {
                        if (data['sample']['barcode'] != null && data['sample']['barcode']!="")
                            return '<p style="text-decoration:line-through">' + data['sample']['barcode'] + '</p>';
                    } catch {}
                } else
                    return "";
                return data['sample']['barcode'];
            }},

            { // Donor ID
                "mData": {},
                "mRender": function (data, type, row) {
                    if (data["sample"]["id"]==null)
                        return "";
                    var consent = data['sample']['consent_information'];
                    if (consent == undefined)
                        return "";

                    link = window.location.origin + "/donor/"+'LIMBDON-' + consent['donor_id'];
                    html = "";
                    if (consent['donor_id'] != null) {
                        html += '<a href="'+link+'" >';
                        html += 'LIMBDON-' + consent['donor_id'];
                        html += '</a>';
                    }

                    return html;
                }
            },
            { // Consent ID
                "mData": {},
                "mRender": function (data, type, row) {
                    if (data["sample"]["id"]==null)
                        return "";
                    var consent = data['sample']['consent_information'];
                    if (consent == undefined)
                        return "";
                    return 'LIMBDC-' + consent['id'];
                }
            },
            { // Consent status
                "mData": {},
                "mRender": function (data, type, row) {
                    if (data["sample"]["id"]==null)
                        return "";

                    var consent = data['sample']['consent_information'];
                    var consent_status = 'Active';
                    if (consent['withdrawn'] == true) {
                        consent_status = 'Withdrawn';
                    }
                    return consent_status;
                }
            },

             {
                    "mData": {},
                    "mRender": function (data, type, row) {
                    if (data["sample"]["id"]==null) {
                        if (data['sample']['uuid']!=null) {
                            return '<p style="text-decoration:line-through">' + data['sample']['uuid'] + '</p>';
                        }
                        else {
                            return "";
                        }}

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
            {"mData": {}, "mRender": function (row) {return row['sample']['id'];}},
            {"mData": {}, "mRender": function (row) {return row['sample']['status'];}},
            {"mData": {}, "mRender": function (row) {return row['sample']['base_type'];}},
            {
                "mData": {},
                "mRender": function (data, type, row) {
                    if (data["sample"]["id"]==null)
                        return "";

                    var sample_type_information = data["sample"]["sample_type_information"];

                    if (data["sample"]["base_type"] == "Fluid") {
                        return sample_type_information["fluid_type"];
                    } else if (data["sample"]["base_type"] == "Cell") {
                        return sample_type_information["cellular_type"] + " > " + sample_type_information["tissue_type"];
                    } else if (data["sample"]["base_type"] == "Molecular") {
                        return sample_type_information["molecular_type"];
                    }

                }
            },
            {
                "mData": {},
                "mRender": function (data, type, row) {
                    if (data["sample"]["id"]==null)
                        return "";

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
                    if (data["sample"]["id"]==null)
                        return "";

                    var percentage = data["sample"]["remaining_quantity"] / data["sample"]["quantity"] * 100 + "%"
                    var col_data = '';
                    col_data += '<span data-toggle="tooltip" data-placement="top" title="' + percentage + ' Available">';
                    col_data += data["sample"]["remaining_quantity"] + "/" + data["sample"]["quantity"] + get_metric(data["sample"]["base_type"]);
                    col_data += '</span>';
                    return col_data
                }
            },

            {
                "mData": {},
                "mRender": function (data, type, row) {
                    return data["entry_datetime"];
                }
            },

            {
                "mData": {},
                "mRender": function (data, type, row) {
                    return data["entry"];
                }
            },

            {
                "mData": {},
                "mRender": function (data, type, row) {
                    return data["updated_on"];
                }
            },

            {
                "mData": {},
                "mRender": function (data, type, row) {
                    if ("editor" in data)
                        return data["editor"]["first_name"].substring(0,1)+data["editor"]["last_name"].substring(0,1);
                    else
                        return "";
                }
            },

            ],

        });
    }


    else {
        $("#sample-table-div").hide();
    }
}

