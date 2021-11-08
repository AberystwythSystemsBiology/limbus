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
    var current_url = encodeURI(window.location);
    var split_url = current_url.split("/");
    split_url = split_url.slice(0, -1);
    split_url.push('endpoint')
    var api_url = split_url.join("/")

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


function update_rack_information(rack_information, samples_new) {
    for (k in samples_new) {
        r = samples_new[k]['row'];
        c = samples_new[k]['col'];

        if (rack_information['view'][r][c]['empty'] == true) {
            rack_information['view'][r][c]['sample'] = samples_new[k];

            if (samples_new[k]['id'] != null) {
                rack_information['view'][r][c]['empty'] = false;
                // tostore - indicator for storage (not from file), only possible if empty==true
                rack_information['view'][r][c]['tostore'] = true;
                rack_information['view'][r][c]['status'] = 'empty2fill';

            } else {
                rack_information['view'][r][c]['status'] = 'empty';
            }

        } else if (samples_new[k]["id"] != null) {

            rack_information['view'][r][c]['sample_old'] = JSON.parse(JSON.stringify(rack_information['view'][r][c]['sample']));
            rack_information['view'][r][c]['sample'] = samples_new[k];

            if (rack_information['view'][r][c]['sample']['id'] != samples_new[k]['id']) {

                if (samples_new[k]["id"] != null)
                    rack_information['view'][r][c]['tostore'] = true;
                rack_information['view'][r][c]['status'] = 'fill2fill';

            } else {
                rack_information['view'][r][c]['tostore'] = false;
                rack_information['view'][r][c]['status'] = 'fill'
            }

        } else {
            rack_information['view'][r][c]['sample_old'] = JSON.parse(JSON.stringify(rack_information['view'][r][c]['sample']));
            rack_information['view'][r][c]['sample'] = samples_new[k];
            rack_information['view'][r][c]['tostore'] = false;
            rack_information['view'][r][c]['status'] = 'fill2empty';
        }
    }

    console.log("rack_information1: ", rack_information);
    return rack_information;
}



function render_subtitle(rack_information) {
    $("#colour").html(render_colour(rack_information["colour"]))
    $("#createdOn").html(rack_information["created_on"]);
    $("#createdBy").html(rack_information["author"]["first_name"] + " " + rack_information["author"]["last_name"]);
    var shelf_information = rack_information["shelf"];

    if (shelf_information != null) {
        var shelf_html = "<a href='" + shelf_information["_links"]["self"] + "'>"
        shelf_html += "<i class='fa fa-bars'></i> LIMBSHF-" + shelf_information["id"]
        shelf_html += "</a>"
        $("#sh").html(shelf_html);
    }

    else {
    }


}

function render_empty(row, col, count, assign_sample_url) {
    assign_sample_url = assign_sample_url.replace("rph", row);
    assign_sample_url = assign_sample_url.replace("cph", col);

    var content = '<div class="col" id="tube_' + [row, col].join("_") + '">'
    content += '<div class="square tube" droppable=true >'
    content += '<div class="align-middle">'
    //content += count
    content += "</div></div></div>"
    $("#row_" + row).append(content)

    $("#tube_" + [row, col].join("_")).click(function () {
        window.location = assign_sample_url;
    });
}

function render_axis(row, col) {
    var content = '<div class="col" id="axis_' + row+'_'+col + '">'

    if (row==0 & col==0) {
        tick = '';
        content += '<div class="float-right">'; // + tick + "</div>"
        content += '<strong>'+ tick + '</strong></div>';
    } else if (row>0 & col==0) {
        //display alphabet letter
        tick = String.fromCharCode(Number(row)+64);
        content += '<div class="float-right">';
        content += '<strong>'+ tick + '</strong></div>'
    } else {
        tick = col;
        //content += tick;
        content += '<div class="text-center">'; //+ tick + "</div>"
        content += '<strong>'+ tick + '</strong></div>'
    }
    content += "</div>";
    $("#row_" + row).append(content)
}

function get_barcode(sample_info, barc_type) {

    var url = encodeURI(sample_info["_links"]["barcode_generation"]);

    console.log(url);

    var b64 = "";

    $.post({
        async: false,
        global: false,
        url: url,
        dataType: "json",
        contentType: 'application/json',
        data: JSON.stringify ({
            "type": barc_type,
            "data": sample_info["uuid"]
        }),
        success: function (data) {
            b64 = data["b64"];
        },

    });

    return b64;

}

function render_modal(sample_info) {
    $("#sampleName").html(render_colour(sample_info["colour"]) + sample_info["uuid"])

    var html = render_content("Biobank Barcode", sample_info["biobank_barcode"]);
    html += render_content("Sample Type", sample_info["base_type"]);
    html += render_content("Collection Site", sample_info["collection_site"]);
    html += render_content("Sample Source", sample_info["source"]);
    html += render_content("Created On", sample_info["created_on"]);

    // $("#sample_barcode").html("<img class='margin: 0 auto 0;' src='" + sample_info["_links"]["qr_code"] + "'>")
    //get_barcode("#sample_barcode", sample_info, "qr_code")

    $("#sample_view_btn").click( function() {
        window.location.href = sample_info["_links"]["self"];
    })

    $("#sampleModalInformation").html(html);

}

function render_full(info, row, col, count, assign_sample_url) {
    var sample_info = info["sample"]
    var content = '<div class="col" id="tube_' + [row, col].join("_") + '">'
    content += '<div class="square tube"><div class="align_middle present-tube">'
    content += '<img width="100%" src="data:image/png;base64,' + get_barcode(sample_info, "qrcode") + '">'
    
    
    content += "</div></div></div>"
    $("#row_" + row).append(content)

    $("#tube_" + [row, col].join("_")).click(function () {
        //window.location = sample_info["_links"]["self"];
        render_modal(sample_info);
        $("#sampleInfoModal").modal();
    });
}


function render_sample_label(data) {
    var label = '';
    var sample_type_information = data["sample_type_information"];
    if (data["base_type"] == "Fluid") {
        label += sample_type_information["fluid_type"];
    } else if (data["base_type"] == "Cell") {
        label += sample_type_information["cellular_type"] + " > " + sample_type_information["tissue_type"];
    } else if (data["base_type"] == "Molecular") {
        label += sample_type_information["molecular_type"];
    }
    label += data["remaining_quantity"] + "/" + data["quantity"] + get_metric(data["base_type"]);
    label += '</span>';
/*
    if (sample_type_information["cellular_container"] == null) {
        label += sample_type_information["fluid_container"];
    } else {
        label += sample_type_information["cellular_container"];
    }*/
    return(label)
}

function render_full_noimg(info, row, col, count, assign_sample_url, dispopt) {
    var sample_info = info["sample"]
    var sample_id = sample_info['id'];
    var content = '<div class="col" id="tube_' + [row, col].join("_") + '">'
    if (info['tostore']) {
        content += '<div id="s_'+ sample_id+'" draggable=true droppable=true class="square tube" style="background-color: lightblue ;">' +
            '<div class="align_middle present-tube" style="font-size:0.8em;word-wrap:break-word;">'
    } else {
        content += '<div id="s_'+ sample_id+'" draggable=true droppable=true class="square tube" style="background-color: lightpink ;">' +
            '<div class="align_middle present-tube" style="font-size:0.8em;word-wrap:break-word;">'
    }
    if (dispopt=='id')
        content += '<small>['+sample_info['id'] + '] ' +sample_info['barcode'] +'</small>';
    else if (dispopt=='donor') {
        content += '<small>[' + sample_info['consent_information']['donor_id'] + '] '
        content += render_sample_label(sample_info) + '</small>';
        //content += sample_info['barcode'] + '</small>';
    }
    content += "</div></div></div>"
    $("#row_" + row).append(content)

    $("#tube_" + [row, col].join("_")).click(function () {
        //window.location = sample_info["_links"]["self"];
        render_modal(sample_info);
        $("#sampleInfoModal").modal();
    });
}

function render_full_file_noimg(info, row, col, count, assign_sample_url, dispopt) {
    var sample_info = info["sample"]
    var content = '<div class="col" id="tube_' + [row, col].join("_") + '">'
    if (info['status']=='empty') {
        content += '<div class="square tube" style="background-color: #f5f5f5 ;">' +
            '<div class="align_middle present-tube" style="font-size:0.8em;word-wrap:break-word;">'
    }

    if (info['status']=='empty2fill') {
        content += '<div class="square tube" style="background-color: lightblue ;">' +
            '<div class="align_middle present-tube" style="font-size:0.8em;word-wrap:break-word;">'
        if (dispopt=="id") {
            content += '<small>[' + sample_info['id'] + '] ' + sample_info['barcode'] + '</small>';
        } else if (dispopt=="donor") {
            content += '<small>[' + sample_info['consent_information']['donor_id'] + '] '
            content += render_sample_label(sample_info) + '</small>';
        }
        content += '<i class="fas fa-plus " style="color:blue  ;"></i>';
    } else if (info['status']=='fill')  {
        content += '<div class="square tube" style="background-color: lightpink ;">' +
            '<div class="align_middle present-tube" style="font-size:0.8em;word-wrap:break-word;">'
        if (dispopt=="id") {
            content += '<small>[' + sample_info['id'] + '] ' + sample_info['barcode'] + '</small>';
        } else if (dispopt=="donor") {
            content += '<small>[' + sample_info['consent_information']['donor_id'] + '] '
            content += render_sample_label(sample_info) + '</small>';
        }
        content += '<i class="fas fa-plus " style="color:blue;"></i>';
    } else if (info['status']=='fill2empty')  {
        content += '<div class="square tube" style="background-color: white;">' +
            '<div class="align_middle present-tube" style="font-size:0.8em;word-wrap:break-word;">';
        if (dispopt=="id") {
            content += '<small style="color:red ; text-decoration:line-through">[' + info['sample_old']['id'] + '] ' + info['sample_old']['barcode'] + '</small>';
        } else if (dispopt=="donor") {
            content += '<small style="color:red ; text-decoration:line-through">[' + sample_info['consent_information']['donor_id'] + '] ';
            content += render_sample_label(sample_info) + '</small>';
        }
        content += '<i class="fas fa-times " style="color:red;"></i>';
    }  else if (info['status']=='fill2fill')  {
        content += '<div class="square tube" style="background-color: lightseagreen ;">' +
            '<div class="align_middle present-tube" style="font-size:0.8em;word-wrap:break-word;">'
        // -- Old sample info
        if (dispopt=="id") {
            content += '<small style="color:red ; text-decoration:line-through">[' + info['sample_old']['id'] + ']' + info['sample_old']['barcode'] + '</small>';

        } else if (dispopt=="donor") {
            content += '<small style="color:red ; text-decoration:line-through">[' + sample_info['consent_information']['donor_id'] + '] ';
            content += render_sample_label(sample_info) + '</small>';
        }
        content += '<i class="fas fa-times " style="color:red;"></i>';
        // -- New sample info
        if (dispopt=="id") {
            content += '<small style="color:blue;"> [' + sample_info['id'] + '] ' + sample_info['barcode'] + '</small>';
        } else if (dispopt=="donor") {
            content += '<small style="color:blue">[' + sample_info['consent_information']['donor_id'] + '] ';
            content += render_sample_label(sample_info) + '</small>';
        }
        content += '<i class="fas fa-plus " style="color:blue;"></i>';
    }

    content += "</div></div></div>"
    $("#row_" + row).append(content)

    $("#tube_" + [row, col].join("_")).click(function () {
        //window.location = sample_info["_links"]["self"];
        render_modal(sample_info);
        $("#sampleInfoModal").modal();
    });
}

function render_occupancy_chart(counts) {
    new Chart(document.getElementById("status_chart"), {
        type: 'doughnut',
        data: {
            labels: ["Occupied", "Empty"],
            datasets: [
                {
                    //backgroundColor: ["#28a745", "#dc3545"],
                    backgroundColor: ["#dc3545", "#28a745"],
                    data: [counts["full"], counts["empty"]]
                }
            ]
        },
        options: {
            legend: {
                display: false
            }
        }
    }
    );
}


function render_sample_table(samples) {

    if (samples.length > 0) {

        $('#sampleTable').DataTable( {
            data: samples,
            rowCallback: function(row, data, index){
                if(data['tostore']==true){
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
                {targets: [0, 4, 5, 9], visible: false, "defaultContent": ""},
            ],
            order: [[0, 'asc']],
            columns: [
                { // col id
                    "mData": {},
                    "mRender": function(data, type,row) {
                        return data["pos"][1];
                    },
                    "width": "3%"
                },
                { // pos: row, col
                    "mData": {},
                    "mRender": function(data, type,row) {
                        tick = String.fromCharCode(Number(data["pos"][0])+64);
                        //return data["pos"][0] + ", " + data["pos"][1]
                        return tick + ", " + data["pos"][1]                        
                    },
                    "width": "3%"
                },

            {"mData": {}, "mRender": function (row) {
                if (row['sample']['id'] == null)
                   return '<span style="text-decoration:line-through">' +row["sample"]["barcode"] + '</span>';
                return row['sample']['barcode'];}
            },

            { // Donor ID
                "mData": {},
                "mRender": function (data, type, row) {
                    if (row['sample']['id'] == null)
                        return '';

                    var consent = data['sample']['consent_information'];
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
                    if (row['sample']['id'] == null)
                        return '';

                    var consent = data['sample']['consent_information'];
                    return 'LIMBDC-' + consent['id'];
                }
            },
            { // Consent status
                "mData": {},
                "mRender": function (data, type, row) {
                    if (row['sample']['id'] == null)
                        return '';
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
                    if (row['sample']['id'] == null)
                        return '';

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

            {"mData": {}, "mRender": function (row) {
                if (row['sample']['id'] == null)
                    return '';
                return row['sample']['id'];}
            },
            {"mData": {}, "mRender": function (row) {
                if (row['sample']['id'] == null)
                    return '';
                return row['sample']['status'];}
            },
            {"mData": {}, "mRender": function (row) {
                if (row['sample']['id'] == null)
                    return '';
                return row['sample']['base_type'];}
            },
            {
                "mData": {},
                "mRender": function (data, type, row) {
                    if (row['sample']['id'] == null) return '';
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
                    if (row['sample']['id'] == null) return '';
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
                    if (row['sample']['id'] == null) return '';
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
                    if (row['sample']['id'] == null) return '';
                    var storage_data = data["sample"]["storage"];

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
                    return data["sample"]["storage"]
                }
            },

            {
                "mData": {},
                "mRender": function (data, type, row) {
                    if (row['sample']['id'] == null) return '';
                    return data["sample"]["created_on"];
                }
            },
    
            ],
            
        });
    }


    else {
        $("#sample-table-div").hide();
    }
}



function render_information(rack_information) {
    var html = render_content("UUID", rack_information["uuid"]);
    html += render_content("Serial Number", rack_information["serial_number"]);
    html +=  render_content("Description", rack_information["description"])

    $("#rack-information").html(html);

    $("#row").html(rack_information["num_rows"]);
    $("#col").html(rack_information["num_cols"]);
}

function render_view(view, assign_sample_url, dispopt) {
    var count = 0;

    var samples = [];

    for (r in view) {
        var row_id = "row_" + r
        $("#view_area").append('<div id="' + row_id + '" class="row no-gutters"></div>');
        var row = view[r]
        for (c in row) {
            if (c==0 || r==0) {
                render_axis(r, c);
            } else {
                count += 1
                var column = row[c];
                if (column["empty"]) {
                    render_empty(r, c, count, assign_sample_url);
                } else {

                    if (dispopt=='qr') {
                        render_full(column, r, c, count, assign_sample_url);
                    } else {
                        render_full_noimg(column, r, c, count, assign_sample_url, dispopt);
                    }
                    column["pos"] = [r, c]
                    samples.push(column)

                }
            }
        }
    }

    return samples;
}



function render_view_from_file(view, assign_sample_url, dispopt) {
    var count = 0;
    let samples = [];

    for (r in view) {
        var row_id = "row_" + r
        $("#view_area").append('<div id="' + row_id + '" class="row no-gutters"></div>');
        var row = view[r]
        for (c in row) {

            if (c==0 || r==0) {
                render_axis(r, c);
            } else {
                count += 1
                var column = row[c];

                if (column['status']=="empty") {
                    render_full_file_noimg(column, r, c, count, assign_sample_url, dispopt);
                    column['tostore']=true; // new assignment: blue
                    column["pos"] = [r, c]
                    if (column['sample'] == null)
                        column['sample'] = {'id': null}
                    samples.push(column);
                } else {
                    render_full_file_noimg(column, r, c, count, assign_sample_url, dispopt);
                    column["pos"] = [r, c]
                    // - deep copy
                    let colold = JSON.parse(JSON.stringify(column));
                    colold['sample']=column['sample_old'];
                    colold['tostore']=false; //old assignment: pink
                    column['tostore']=true;  //new assignment: blue
                    delete colold['sample_old'];
                    delete column['sample_old'];
                    if (column['sample'] == null)
                        column['sample'] = {'id': null};
                    samples.push(column);
                    if (colold['sample'] != null) {
                        samples.push(colold);
                    }
                }
            }
        }
    }

    return samples;

}


function fill_sample_pos(api_url, sampletostore, commit) {
    sampletostore = Object.assign({}, sampletostore, {'commit': commit})

    var json = (function () {
        var json = null;
        $.ajax({
            'async': false,
            'global': false,
            'url': api_url,
            'type': 'POST',
            'dataType': "json",
            'data': JSON.stringify(sampletostore),
            'contentType': 'application/json; charset=utf-8',
            'success': function (data) {
                json = data
            },
            'failure': function (data) {
                json = data;
            }

        });
        return json;
    })();

    return json;

}


function dragndrop_rack_view() {
       $("#confirm_position").hide();
       $("#cancel_change").hide();
       $("#submit_sampletorack").show();
        var dispopt = $("input[name='dispopt']:checked").val();
        var changed = [];
        document.ondragstart = function (event) {
            //event.dataTransfer.setData("text/plain", event.target.id);
            event.dataTransfer.setData('target_id', event.target.id);
        };

        /* Events fired on the drop target */
        document.ondragover = function (event) {
            event.preventDefault();
        };

        document.ondrop = function (event) {

            event.preventDefault();
            var drop_target = event.target.parentNode;
            if (drop_target.getAttribute("droppable")=="true") {
                var drag_target_id = event.dataTransfer.getData('target_id');
                var drag_target = $('#' + drag_target_id)[0];

                var drag_tube_id = drag_target.parentNode.id;
                var drop_tube_id = drop_target.parentNode.id;
                var tmp = document.createElement('swap');
                tmp.className = 'hide';

                if (!drag_target.hasAttribute("tube_id"))
                    drag_target.setAttribute("tube_id", drag_tube_id)
                if (!drop_target.hasAttribute("tube_id"))
                    drop_target.setAttribute("tube_id", drop_tube_id)

                changed.push(drag_tube_id);
                changed.push(drop_tube_id);

                drop_target.before(tmp);
                drag_target.before(drop_target);
                tmp.replaceWith(drag_target);

                $("#confirm_position").show();
                $("#cancel_change").hide();
                $("#submit_sampletorack").hide();

                if (dispopt == 'id') {
                    $("input[id='id_on']").attr('disabled', false);
                    $("input[id='donor_on']").attr('disabled', true);
                } else {
                    $("input[id='id_on']").attr('disabled', true);
                    $("input[id='donor_on']").attr('disabled', false);
                }
            }
        };


        $("#cancel_change").click(function (event) {
            window.location.reload();
        });


       $("#confirm_position").click(function(e){
           // update rackinformation and revise sampletostore in sessionStorage
           $("#confirm_position").hide();
           $("#cancel_change").show();
           $("#submit_sampletorack").show();

           console.log("rack before", rack_information);
           upd = {};
           changed.forEach(function(tube_id) {
               var orig_tube_id = document.getElementById(tube_id).firstChild.getAttribute("tube_id");
               console.log("orig_tube_id", orig_tube_id, tube_id);
               if (orig_tube_id != tube_id) {

                   var ss = orig_tube_id.replace("tube_", "").split("_");
                   var row = parseInt(ss[0]);
                   var col = parseInt(ss[1]);

                   upd[tube_id] = JSON.parse(JSON.stringify(rack_information['view'][row][col]));
                   if (upd[tube_id]["empty"] == true) {
                       upd[tube_id]["tostore"] = false;
                       upd[tube_id]["pos"] = [row, col];
                   } else {
                       upd[tube_id]["tostore"] = true;
                       upd[tube_id]["pos"] = [row, col];
                       upd[tube_id]['sample']['pos'] = [row, col];
                       upd[tube_id]['sample']['row'] = row;
                       upd[tube_id]['sample']['col'] = col;
                   }
               }
           });

           Object.keys(upd).forEach(function(k) {
               var ss = k.replace("tube_", "").split("_");
               var row = parseInt(ss[0]);
               var col = parseInt(ss[1]);
               rack_information['view'][row][col]=JSON.parse(JSON.stringify(upd[k]));

               if (upd[k]["empty"]==true)
                   rack_information['view'][row][col]["tostore"]=false;
               else
                   rack_information['view'][row][col]["tostore"]=true;

           })

            dispopt = $("input[name='dispopt']:checked").val();
            $("#view_area").empty()
            var samples = render_view(rack_information["view"], rack_information["_links"]["assign_sample"], dispopt);

            $('#sampleTable').DataTable().destroy();
            render_sample_table(samples);

            $("input[id='id_on']").attr('disabled', false);
            $("input[id='donor_on']").attr('disabled', false);

            $("input[name='dispopt']").change(function(){
                var dispopt = $("input[name='dispopt']:checked").val();
                $("#view_area").empty()
                   samples = render_view(rack_information["view"], rack_information["_links"]["assign_sample"], dispopt);
            })

           samples_pos = [];
           Object.keys(samples).forEach(function(k) {
               sample=samples[k];
               console.log("sample k", sample)
               sample["sample"]["empty"] = sample['empty'];
               sample["sample"]["tostore"] = sample['tostore'];
               sample["sample"]['pos'] = sample['pos'];
               sample["sample"]['row'] = sample['pos'][0];
               sample["sample"]['col'] = sample['pos'][1];

               if (samples[k]['tostore']==true)
                    samples_pos.push(samples[k]["sample"])
           });

           sampletostore = JSON.parse(sessionStorage.getItem("sampletostore"));
           console.log("sampletostore", sampletostore)
           sampletostore["samples"] = samples_pos;
           sessionStorage.setItem("sampletostore", JSON.stringify(sampletostore));
           changed =[];
       });

}

var rack_information = get_rack_information();
$(document).ready(function () {
    collapse_sidebar();
    //var rack_information = get_rack_information();
    sampletostore = JSON.parse(sessionStorage.getItem("sampletostore"));
    rack_id = sampletostore["rack_id"]
    samples_new = sampletostore["samples"]
    from_file = sampletostore["from_file"]

    if("update_only" in sampletostore)
        update_only = sampletostore["update_only"]
    else
        update_only = False

    $("input[id='qr_on']").attr('hidden', true);

    $("#cancel_change").hide();
    $("#confirm_position").hide();

    update_rack_information(rack_information, samples_new);
    render_subtitle(rack_information);
    render_information(rack_information);

    var dispopt = $("input[name='dispopt']:checked").val();

    if (from_file==true) {
        var samples = render_view_from_file(rack_information["view"], rack_information["_links"]["assign_sample"], dispopt);
    } else {
        var samples = render_view(rack_information["view"], rack_information["_links"]["assign_sample"], dispopt);
    }

    $("input[name='dispopt']").change(function(){
        var dispopt = $("input[name='dispopt']:checked").val();
        $("#view_area").empty()
        if (from_file==true) {
           samples = render_view_from_file(rack_information["view"], rack_information["_links"]["assign_sample"], dispopt);
       } else
           samples = render_view(rack_information["view"], rack_information["_links"]["assign_sample"], dispopt);
    })

    render_occupancy_chart(rack_information["counts"]);
    render_sample_table(samples);


    dragndrop_rack_view();

    $("#submit_sampletorack").click(function (event) {
        if (from_file)
            var api_url = window.location.origin + "/storage/rack/refill_with_samples"
        else if (!update_only)
            var api_url = window.location.origin + "/storage/rack/fill_with_samples"
        else
            var api_url = window.location.origin + "/storage/rack/edit_samples_pos"

        res = fill_sample_pos(api_url, sampletostore,commit=true);
        if (commit & res['success']){
            alert(res['message'])
            sessionStorage.clear();
            window.open(rack_information["_links"]["self"],"_self");
        } else {
            alert(res['message'])
        }
    })

    $("#loading-screen").fadeOut();
    $("#content").delay(500).fadeIn();

});