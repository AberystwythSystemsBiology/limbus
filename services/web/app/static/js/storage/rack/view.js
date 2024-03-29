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

 
function get_rack_information(){
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

    var content = '<div class="col" id="tube_' + [row, col].join("_") + '">';
    content += '<div class="square tube">';
    content += '<div class="align-middle">';
    content += "</div></div></div>";
    $("#row_" + row).append(content);

    $("#tube_" + [row, col].join("_")).click(function () {
        window.location = assign_sample_url;
    });
}

function render_axis(row, col) {
    var content = '<div class="col" id="axis_' + row+'_'+col + '">';

    if (row==0 & col==0) {
        tick = '';
        content += '<div class="float-right">'; // + tick + "</div>"
        content += '<strong>'+ tick + '</strong></div>';
    } else if (row>0 & col==0) {
        //display alphabet letter
        tick = String.fromCharCode(Number(row)+64);
        content += '<div class="float-right">';
        content += '<strong>'+ tick + '</strong></div>';
    } else {
        tick = col;
        //content += tick;
        content += '<div class="text-center">'; //+ tick + "</div>"
        content += '<strong>'+ tick + '</strong></div>';
    }
    content += "</div>";
    $("#row_" + row).append(content)
}

function get_barcode(sample_info, barc_type) {

    var url = encodeURI(sample_info["_links"]["barcode_generation"]);

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

    // $("#sample_barcode").html("<img class='margin: 0 auto 0;' src='" + sample_info["_links"]["qr_code"] + "'>")

    //get_barcode("#sample_barcode", sample_info, "qr_code")

    $("#sample_view_btn").click( function() {
        window.location.href = sample_info["_links"]["self"];
    });

    $("#sample_to_cart_btn").click( function() {
        $("#sampleInfoModal").modal("hide");
        var msg = "Adding a sample to cart will remove it from storage, press OK to proceed!";
        if (confirm(msg)) {
            $.ajax({
                type: "POST",
                url: sample_info["_links"]["add_sample_to_cart"],
                dataType: "json",
       'success': function (data) {
           json = data;
           $("#cart-confirmation-msg").html(data["message"]);
           $("#cart-confirmation-modal").modal({
               show: true
           });
           },
       'failure': function (data) {
           json = data;
           $("#cart-confirmation-msg").html(data["message"]);
           $("#cart-confirmation-modal").modal({
               show: true
           });
           }
            });
        } else {
            return false;
        }
    });

    $("#sampleModalInformation").html(html);

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

function render_full(info, row, col, count, assign_sample_url) {
    var sample_info = info["sample"];
    var content = '<div class="col" id="tube_' + [row, col].join("_") + '">';
    content += '<div class="square tube"><div class="align_middle present-tube">';
    content += '<img width="100%" src="data:image/png;base64,' + get_barcode(sample_info, "qrcode") + '">'

    content += "</div></div></div>";
    $("#row_" + row).append(content);
    $("#tube_" + [row, col].join("_")).click(function () {
        render_modal(sample_info);
        $("#sampleInfoModal").modal();
    });
}

function render_full_noimg(info, row, col, count, assign_sample_url, dispopt) {
    var sample_info = info["sample"]
    var content = '<div class="col" id="tube_' + [row, col].join("_") + '">'
    content += '<div class="square tube" style="background-color: lightpink ;">' +
        '<div class="align_middle present-tube" style="font-size:0.8em;word-wrap:break-word;">'

    if (dispopt=='id') {
        content += '<small>[' + sample_info['id'] + '] ' + sample_info['barcode'];
        content += '</small>';
    }
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
    content += "</div></div></div>";

    $("#row_" + row).append(content);

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


function render_information(rack_information) {
    var html = render_content("UUID", rack_information["uuid"]);
    html += render_content("Serial Number", rack_information["serial_number"]);
    html +=  render_content("Description", rack_information["description"])

    $("#rack-information").html(html);

    $("#row").html(rack_information["num_rows"]);
    $("#col").html(rack_information["num_cols"]);
    if (rack_information["counts"]["full"]>0)
        $("#delete-rack").hide();
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
    var msg = "Adding a rack to cart will remove the rack, and samples it holds, from storage, press OK to proceed!";
    if (!confirm(msg)) {
      return false;
    }
    $.ajax({
        type: "POST",
        url: api_url,
        dataType: "json",
        success: function (data) {
            if (data["success"]) {
                $("#cart-confirmation-msg").html(data["message"]);
                $("#cart-confirmation-modal").modal({
                    show: true
                });
            }

            else {
                $("#cart-confirmation-msg").html(data["message"]);
                $("#cart-confirmation-modal").modal({
                    show: true
                });
            }
        }
    });
})




/*    function printContent()
{
    var e = document.createElement('div');
    e.id = 'view_area';
    e.innerHTML = $('#view_area').html();
    e.print();
    document.getElementById('t').appendChild(e);
}*/

$("#print-rack-btn").click(function () {
     print();

});


$('#cart-confirmation-modal').on('hidden.bs.modal', function () {
    location.reload();
})


$(document).ready(function () {
    collapse_sidebar();

    var rack_information = get_rack_information();
    var rack_id = rack_information["id"]

    render_subtitle(rack_information);
    render_information(rack_information);

    // $("input[id='qr_on']").attr('disabled', true);
    var dispopt = $("input[name='dispopt']:checked").val();
    var samples = render_view(rack_information["view"], rack_information["_links"]["assign_sample"], dispopt);

    $("input[name='dispopt']").change(function(){
        dispopt = $("input[name='dispopt']:checked").val();
        $("#view_area").empty()
        samples = render_view(rack_information["view"], rack_information["_links"]["assign_sample"], dispopt);
    })

    render_occupancy_chart(rack_information["counts"])
    render_sample_table(samples)


    $("#add-sample-btn").click(function() {
    var api_url = window.location.href = rack_information["_links"]["assign_samples"];
    var sampletostore = fill_sample_pos(api_url, rack_id, {}, commit=false)

    })

    $("#repos-rack-btn").click(function() {
    var api_url = window.location.href = rack_information["_links"]["edit_samples_pos"];
    var sampletostore = fill_sample_pos(api_url, rack_id, {}, commit=false)

    })

    $("#update-from-file-btn").click(function() {
    var api_url = window.location.href = rack_information["_links"]["update_samples"];
    var sampletostore = fill_sample_pos(api_url, rack_id, {}, commit=false)
    })

    $("#update-sample-from-file-btn").click(function() {
    var api_url = window.location.href = rack_information["_links"]["update_sample_info"];
    var sampletostore = fill_sample_pos(api_url, rack_id, {}, commit=false)
    })

    $("#loading-screen").fadeOut();
    $("#content").delay(500).fadeIn();


});