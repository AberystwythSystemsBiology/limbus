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


function update_rack_information(samples_new) {
    var with_info = [];
    for (k in samples_new) {
        r = samples_new[k]['row'];
        c = samples_new[k]['col'];
        with_info.push([r,c].join());
        //console.log("voew", rack_information['view'][r][c]);
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
                rack_information['view'][r][c]['tostore'] = true;
                rack_information['view'][r][c]['status'] = 'fill2fill';

            } else {
                rack_information['view'][r][c]['tostore'] = false;
                rack_information['view'][r][c]['status'] = 'fill';
            }

        } else {
            rack_information['view'][r][c]['sample_old'] = JSON.parse(JSON.stringify(rack_information['view'][r][c]['sample']));
            rack_information['view'][r][c]['sample'] = samples_new[k];
            rack_information['view'][r][c]['tostore'] = false;
            rack_information['view'][r][c]['status'] = 'fill2empty';
        }
    }

    // The tubes or positions without new info will not be changed unless
    // being moved to a different position provided in the csv file.
    for(let r = 1; r <rack_information['view'].length; r++) {
        var keys = Object.keys(rack_information['view'][r]);
        for (let c = 1; c < keys.length; c++) {

            if (with_info.includes([r,c].join()))
                continue;

            if (rack_information['view'][r][c]["empty"] == false) {

                rack_information['view'][r][c]["status"] = "fill";
                rack_information['view'][r][c]["tostore"] = false;

            } else {
                rack_information['view'][r][c]["status"] = "empty";
                rack_information['view'][r][c]["tostore"] = false;

            }

        }
    }
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
        content += '<div class="text-center">'; //+ tick + "</div>"
        content += '<strong>'+ tick + '</strong></div>'
    }
    content += "</div>";
    $("#row_" + row).append(content)
}

function get_barcode(sample_info, barc_type) {

    var url = encodeURI(sample_info["_links"]["barcode_generation"]);

    //console.log(url);

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
    var html = render_content("Barcode", sample_info["barcode"]);
    html += render_content("DBid", sample_info["id"]);
    html += render_content("Base Type", sample_info["base_type"]);
    html += render_content("Sample Content", render_sample_label(sample_info));
    html += render_content("Sample Source", sample_info["source"]);
/*
    html += render_content("Donor", '<a href=""> LIMBDON-'+sample_info["consent_information"]["donor_id"] +'</a>';
    html += render_content("Study", '<a href=""> LIMBDON-'+sample_info["consent_information"]["protocol"] +'</a>';
    html += render_content("Donor RefNo", '<a href=""> LIMBDON-'+sample_info["consent_information"]["donor_id"] +'</a>';
    html += render_content("ConsentID", sample_info["consent_information"]);*/
    html += render_content("Status", sample_info["status"]);
    html += render_content("Created On", sample_info["created_on"]);

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
        render_modal(sample_info);
        $("#sampleInfoModal").modal();
    });
}


function render_sample_label(data) {
    var label = '<span>';
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
        content += '<small>';
        if (sample_info['consent_information']['donor_id']!=null)
            content += '[' + sample_info['consent_information']['donor_id'] + '] ';

        if (sample_info['consent_information']['study']!=null) {
            content += '(S' + sample_info['consent_information']['study']['protocol']['id'];

            if (sample_info['consent_information']['study']['reference_id']!="") {
                content += '-' + sample_info['consent_information']['study']['reference_id'];
            }
            content += ') ';
        }
        content += render_sample_label(sample_info) + '</small>';

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
    try {
        var change = sample_info["changeset"]["barcode"];
    } catch {
        var change = undefined;
    }

    if (info["status"]=='fill')
        //console.log("info", info)
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

            content += '<small>';
            //if (![undefined, null].includes(sample_info['consent_information']['donor_id']))//!=null)
            if (sample_info['consent_information']['donor_id']!=undefined
                && sample_info['consent_information']['donor_id']!=null)//!=null)
                content += '[' + sample_info['consent_information']['donor_id'] + '] ';

            if (sample_info['consent_information']['study']!=null) {
                content += '(S' + sample_info['consent_information']['study']['protocol']['id'];

                if (sample_info['consent_information']['study']['reference_id']!="") {
                    content += '-' + sample_info['consent_information']['study']['reference_id'];
                }
                content += ') ';
            }
            content += render_sample_label(sample_info) + '</small>';

        }
        content += '<i class="fas fa-plus " style="color:blue  ;"></i>';

    } else if (info['status']=='fill')  {
        content += '<div class="square tube" style="background-color: lightpink ;">' +
            '<div class="align_middle present-tube" style="font-size:0.8em;word-wrap:break-word;">'

        if (dispopt=="id") {
            //content += '<small>[' + sample_info['id'] + '] ' + sample_info['barcode'] + '</small>';
            content += '<small>[' + sample_info['id'] + '] ';
            if (change !== undefined && change.length>1) {
                content += '<del>' + change[0] + '</del>';
                content += '<samll style="color:red">'+ sample_info['barcode'] +'</samll>';
            } else {
                content += sample_info['barcode'];
            }
            content += '</small>';

        } else if (dispopt=="donor") {

            content += '<small>';
            if (sample_info['consent_information']['donor_id']!=undefined
                && sample_info['consent_information']['donor_id']!=null)
                content += '[' + sample_info['consent_information']['donor_id'] + '] ';

            if (sample_info['consent_information']['study']!=null) {
                content += '(S' + sample_info['consent_information']['study']['protocol']['id'];

                if (sample_info['consent_information']['study']['reference_id']!="") {
                    content += '-' + sample_info['consent_information']['study']['reference_id'];
                }
                content += ') ';
            }
            content += render_sample_label(sample_info) + '</small>';

        }

        content += '<i class="fas fa-plus " style="color:blue;"></i>';
        if (change !== undefined && change.length>1) {
            content += '<i class="fa fa-pen" style="color:red;"></i>';
        }


    } else if (info['status']=='fill2empty')  {
        content += '<div class="square tube" style="background-color: white;">' +
            '<div class="align_middle present-tube" style="font-size:0.8em;word-wrap:break-word;">';
        if (dispopt=="id") {

            content += '<small style="color:red ; text-decoration:line-through">[' +
                info['sample_old']['id'] + '] ' + info['sample_old']['barcode'] + '</small>';

        } else if (dispopt=="donor") {

            content += '<small style="color:red ; text-decoration:line-through">';
            if (info['sample_old']['donor_id']!=null)
                content += '[' + info['sample_old']['consent_information']['donor_id'] + '] ';

            if (info['sample_old']['consent_information']['study']!=null) {
                content += '(S' + info['sample_old']['consent_information']['study']['protocol']['id'];

                if (info['sample_old']['consent_information']['study']['reference_id']!="") {
                    content += '-' + info['sample_old']['consent_information']['study']['reference_id'];
                }
                content += ') ';
            }
            content += render_sample_label(info['sample_old']) + '</small>';

        }
        content += '<i class="fas fa-times " style="color:red;"></i>';

    }  else if (info['status']=='fill2fill')  {
        content += '<div class="square tube" style="background-color: lightseagreen ;">' +
            '<div class="align_middle present-tube" style="font-size:0.8em;word-wrap:break-word;">'
        // -- Old sample info
        if (dispopt=="id") {
                content += '<small style="color:red ; text-decoration:line-through">[' +
                    info['sample_old']['id'] + ']' + info['sample_old']['barcode'] + '</small>';

        } else if (dispopt=="donor") {

            content += '<small style="color:red ; text-decoration:line-through">';
            if (info['sample_old']['donor_id']!=null)
                content += '[' + info['sample_old']['consent_information']['donor_id'] + '] ';

            if (info['sample_old']['consent_information']['study']!=null) {
                content += '(S' + sample_info['consent_information']['study']['protocol']['id'];

                if (sample_info['consent_information']['study']['reference_id']!="") {
                    content += '-' + sample_info['consent_information']['study']['reference_id'];
                }
                content += ') ';
            }
            content += render_sample_label(info['sample_old']) + '</small>';

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
    //if (info["status"]=="fill")
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
                    data: [counts["full"], counts["empty"]],
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
                continue;
            }
        count += 1
        var column = row[c];

        if (column['empty']==true) {
            render_empty(r, c, count, assign_sample_url);
            continue;
        }

            render_full_file_noimg(column, r, c, count, assign_sample_url, dispopt);
            column['tostore'] = false; // new assignment: blue
            column["pos"] = [r, c]
            if (column['sample'] == null)
                column['sample'] = {'id': null}
            samples.push(column);

            // For new rack
            if (column['status'] == "empty") {
                continue;
            }
            if (column['status'] == "fill") {
                continue;
            }
            if (column['status'] == "empty2fill") {
                column['tostore'] = true; // new assignment: blue
                continue;
            }

        // -- In case of "empty2fill", "fill2empty", Old sample in the position, deep copy
        let colold = JSON.parse(JSON.stringify(column));
        colold['sample'] = column['sample_old'];
        colold['tostore'] = false; //old assignment: pink
        column['tostore'] = true;  //new assignment: blue
/*
        if (column['sample'] == null)
            column['sample'] = {'id': null};
        samples.push(column);
*/
        if (colold['sample'] != null) {
            samples.push(colold);
        }}
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
       //$("#cancel_change").hide();
       $("#cancel_change").show();

       $("#submit_sampletorack").fadeTo(1000, 0.3, function() { $(this).fadeTo(500, 1.0); });
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
                $("#cancel_change").show();
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

           upd = {};
           changed.forEach(function(tube_id) {
               var orig_tube_id = document.getElementById(tube_id).firstChild.getAttribute("tube_id");

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
               sample["sample"]["empty"] = sample['empty'];
               sample["sample"]["tostore"] = sample['tostore'];
               sample["sample"]['pos'] = sample['pos'];
               sample["sample"]['row'] = sample['pos'][0];
               sample["sample"]['col'] = sample['pos'][1];

               if (samples[k]['tostore']==true)
                    samples_pos.push(samples[k]["sample"])
           });

           sampletostore = JSON.parse(sessionStorage.getItem("sampletostore"));
           //console.log("sampletostore", sampletostore)
           sampletostore["samples"] = samples_pos;
           sessionStorage.setItem("sampletostore", JSON.stringify(sampletostore));
           changed =[];
       });

}


function init_rack_view(num_rows, num_cols) {
    var view = {};
    for (var r = 1; r <= num_rows; r++) {
        view[r]={};
        for (var c = 1; c <= num_cols; c++) {
            view[r][c]={"empty": true};
        }
    }
    let rack = {"view": view,
        "num_rows": num_rows, "num_cols": num_cols,
        "_links": {"assign_sample":"/storage/rack/new/from_file",
            "self": '/storage/rack/LIMBRACK-'},
        "counts": {"full":0, "empty": num_rows*num_cols},
    };

    return rack;
};

var sampletostore = JSON.parse(sessionStorage.getItem("sampletostore"));
//console.log("sampletostore ", sampletostore)
var rack_id = sampletostore["rack_id"];

var current_url = encodeURI(window.location);
if (rack_id==null || rack_id==undefined) {
    rack_id = null;
    var rack_information = init_rack_view(sampletostore["num_rows"],
                                sampletostore["num_cols"]);
}
else {

    var rack_information = get_rack_information();
}

// console.log("rack_information", rack_information);

$(document).ready(function () {
    collapse_sidebar();
    var samples_new = sampletostore["samples"];
    var from_file = sampletostore["from_file"];

    if ("update_only" in sampletostore) {
        update_only = sampletostore["update_only"];
    }
    else {
        update_only = false;
    }
    if ("new_rack" in sampletostore) {
        var new_rack = sampletostore["new_rack"] || (rack_id==null);
    }
    else {
        var new_rack = false;
    }

    if ("update_storage" in sampletostore) {
        var update_storage = sampletostore["update_storage"];
    } else {
        var update_storage = true;
    }

    if (update_storage == false) {
        $("#submit_sampletorack").text("Update Sample in Rack");
    }

    $("input[id='qr_on']").attr('hidden', true);

    $("#confirm_position").hide();

    update_rack_information(samples_new)

    if (new_rack) {
        $("#rack-heading").hide();
        $("#submit_sampletorack").text('Create Rack');

    } else {
        render_subtitle(rack_information);
        render_information(rack_information);
    }


    var dispopt = $("input[name='dispopt']:checked").val();

    if (from_file==true) {
        //console.log("rack_information[view]", rack_information["view"]);
        var samples = render_view_from_file(rack_information["view"],
            rack_information["_links"]["assign_sample"], dispopt);

    } else {
        var samples = render_view(rack_information["view"],
            rack_information["_links"]["assign_sample"], dispopt);
    }


    $("input[name='dispopt']").change(function(){
        var dispopt = $("input[name='dispopt']:checked").val();
        $("#view_area").empty()
        if (from_file==true) {
           samples = render_view_from_file(rack_information["view"],
               rack_information["_links"]["assign_sample"], dispopt);
       } else
           samples = render_view(rack_information["view"],
               rack_information["_links"]["assign_sample"], dispopt);
    })

    render_occupancy_chart(rack_information["counts"]);
    render_sample_table(samples);


    if (from_file == true) {
        $("#cancel_change").show();
    }
    else {
        $("#cancel_change").show();
        dragndrop_rack_view();
        $("#submit_sampletorack").show()

    }


    $("#cancel_change").click(function (event) {
        //window.location.reload();
        if (new_rack)
            window.open(window.location.origin + "/storage/rack/new/from_file");
        else
            window.open(rack_information["_links"]["self"],"_self");

    });

    if (update_storage) {
        alert("Note: Please check the storage info before pressing STORE-SAMPLE-TO-RACK button to confirm!!")
    } else {
        alert("Note: Please check the storage info before pressing UPDATE-SAMPLE-IN-RACK button to confirm!!")
    }


    $("#submit_sampletorack").click(function (event) {
        if (from_file) {
            if (new_rack)
                var api_url = window.location.origin + "/storage/rack/new_with_samples";

            else
                var api_url = window.location.origin + "/storage/rack/refill_with_samples";

                if (update_storage) {
                        var api_url = window.location.origin + "/storage/rack/refill_with_samples";
                } else {
                        var api_url = window.location.origin + "/storage/rack/update_sample_info";
                }

        }
        else if (!update_only)
            var api_url = window.location.origin + "/storage/rack/fill_with_samples"
        else
            var api_url = window.location.origin + "/storage/rack/edit_samples_pos"

        console.log("api_url: ", api_url);
        res = fill_sample_pos(api_url, sampletostore,commit=true);
        if (commit && res['success']){
            alert(res['message'])
            sessionStorage.removeItem("sampletostore")
            if (new_rack && res["content"]["id"]!=undefined) {
                rack_information["_links"]["self"] += res["content"]["id"]
            }

            window.open(rack_information["_links"]["self"],"_self");
        } else {
            alert(res['message'])
        }
    })

    $("#loading-screen").fadeOut();
    $("#content").delay(50).fadeIn();

});