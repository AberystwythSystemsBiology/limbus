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

// - not in use
function get_rack_information() {
    var api_url = encodeURI(window.location + '/endpoint');

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
    content += '<div class="square tube">'
    content += '<div class="align-middle">'
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
        render_modal(sample_info);
        $("#sampleInfoModal").modal();
    });
}

function render_full_noimg(info, row, col, count, assign_sample_url) {
    var sample_info = info["sample"]
    // console.log(sample_info)
    var content = '<div class="col" id="tube_' + [row, col].join("_") + '">'
    content += '<div class="square tube" style="background-color: lightpink ;"><div class="align_middle present-tube">'
    content += sample_info['id']
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
                if(data['tostore']){
                    $(row).find('td:eq(0)').css('background-color', 'lightblue');
                } else {
                    $(row).find('td:eq(0)').css('background-color', 'lightpink');
                }
            },
            dom: 'Blfrtip',
            buttons: [ 'print', 'csv', 'colvis' ],
            lengthMenu: [ [5, 10, 25, 50, -1], [5, 10, 25, 50, "All"] ],
            columnDefs: [
                {targets: '_all', defaultContent: ''},
                {targets: [3,4,5], visible: false, "defaultContent": ""},
            ],
            columns: [
                {
                    "mData": {},
                    "mRender": function(data, type,row) {
                        return data["pos"][0] + ", " + data["pos"][1]
                    },
                    "width": "3%"
                },
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

            {"mData": {}, "mRender": function (row) {return row['sample']['id'];}},
            {"mData": {}, "mRender": function (row) {return row['sample']['barcode'];}},
            {"mData": {}, "mRender": function (row) {return row['sample']['status'];}},
            {"mData": {}, "mRender": function (row) {return row['sample']['base_type'];}},
            {
                "mData": {},
                "mRender": function (data, type, row) {
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
                    col_data += '<span data-toggle="tooltip" data-placement="top" title="' + percentage + ' Available">';
                    col_data += data["sample"]["remaining_quantity"] + "/" + data["sample"]["quantity"] + get_metric(data["sample"]["base_type"]);
                    col_data += '</span>';
                    return col_data
                }
            },

            {
                "mData": {},
                "mRender": function (data, type, row) {
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

function render_view(view, assign_sample_url, img_on) {
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

                    if (img_on) {
                        render_full(column, r, c, count, assign_sample_url);
                    } else {
                        render_full_noimg(column, r, c, count, assign_sample_url);
                    }
                    column["pos"] = [r, c]
                    samples.push(column)

                }
            }
        }
    }

    return samples;

}

function fill_sample_pos(api_url, rack_id, sampletostore, commit) {
    var json = (function () {
        var json = null;
        $.ajax({
            'async': false,
            'global': false,
            'url': api_url,
            'type': 'POST',
            'dataType': "json",
            'data': JSON.stringify({'rack_id': rack_id,
                'samples':(sampletostore), 'commit': commit
            }),
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


$("#add-rack-cart-btn").click(function() {
    var api_url = window.location.href + "/to_cart";
    $.ajax({
        type: "POST",
        url: api_url,
        dataType: "json",
        success: function (data) {
            if (data["success"]) {
                $("#cart-confirmation-msg").html(data["content"]["msg"]);
                $("#cart-confirmation-modal").modal({
                    show: true
                });
            }

            else {
                $("#cart-confirmation-msg").html(data["content"]["msg"]);
                $("#cart-confirmation-modal").modal({
                    show: true
                });
            }
        }
    });
})

$('#cart-confirmation-modal').on('hidden.bs.modal', function () {
    location.reload();
})

// $("#cart-confirmation-close").click(function(){
//     location.reload();
// })

$(document).ready(function () {
    collapse_sidebar();

    var rack_information = get_rack_information();
    var rack_id = rack_information["id"]

    render_subtitle(rack_information);
    render_information(rack_information);

    var img_on = $('#img_on').prop('checked');
    var samples = render_view(rack_information["view"], rack_information["_links"]["assign_sample"], img_on);
    $("#img_on").click(function(){
        $("#view_area").empty()
        img_on = $('#img_on').prop('checked');
        samples = render_view(rack_information["view"], rack_information["_links"]["assign_sample"], img_on);
    });

    render_occupancy_chart(rack_information["counts"])
    render_sample_table(samples);

    $("#add-sample-btn").click(function() {
    var api_url = window.location.href = rack_information["_links"]["assign_samples"];
    var sampletostore = fill_sample_pos(api_url, rack_id, {}, commit=false)
           // console.log('sampletostore', sampletostore)
           // if (sampletostore.success == false){
           //      alert(sampletostore.message)
           //      return false
           // } else {
           //     if (sampletostore.content.samples.length==0) {
           //         alert('All selected samples have been stored in the selected rack!');
           //         return false;
           //     }
           //     if (sampletostore.message != '') {
           //         if (confirm(sampletostore.message)) {
           //
           //         } else {
           //             return false
           //         }
           //     }
           // }
           // samplestore =  sampletostore['content']
           // sessionStorage.setItem("rack_id", rack_id);
           // sessionStorage.setItem("sampletostore", JSON.stringify(sampletostore)); //JSON.stringify(formdata));
           // //window.open("view_sample_to_rack.html");
           // //window.open(api_url, "_blank"); //, "_self");
           // window.open(api_url, "_self");

        //}

    })

    $("#loading-screen").fadeOut();
    $("#content").delay(500).fadeIn();


});