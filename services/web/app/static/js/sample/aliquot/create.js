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

function get_containers() {
    var current_url = encodeURI(window.location);
    var split_url = current_url.split("/");
    var url_stub = split_url.slice(0, 3); // url scheme, "://", domain+port
    var api_url = url_stub.concat(['api', 'sample', 'containers']).join('/')
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

    return json["content"];}

function get_sample() {
    var current_url = encodeURI(window.location);
    var split_url = current_url.split("/");
    split_url.pop()
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

function check_barcode_form() {
    var present_barcodes = []
    var fail = false;

    $(".barcode").each(function() {
        console.log(present_barcodes);
        var barcode = $(this).val();
        if (barcode != "") {
            if(jQuery.inArray(barcode, present_barcodes) != -1) {
                fail = true;
            }
            present_barcodes.push(barcode);
        }
        
    });

    return fail;
}

function remove_whitespace(v) { 
    return v.replace(/\s/g,'');

}

function check_barcode_database(entered_barcode) {

    var json = (function () {
        var json = null;
        $.post({
            'async': false,
            'global': false,
            'url': sample["_links"]["webapp_query"],
            'contentType': 'application/json',
            'data': JSON.stringify({barcode: entered_barcode}),
            'success': function (data) {
                json = data;
            }
        });
        return json;
    })();

    

    if (json["content"].length > 0) {
        return true
    }
    return false;
    
}


// Global because I hate myself.
var sample = get_sample();
var container_information = get_containers();
var indexes = [];

function update_graph() {
    var remaining_quantity = $("#remaining_quantity").val();
    var quantity = $("#original_quantity").val();
    var metric = $("#original_metric").html();



    new Chart(document.getElementById("quantity-chart"), {
        type: 'doughnut',
        data: {
            labels: ["Remaining " + metric, "Used " + metric],
            datasets: [
                {
                    backgroundColor: ["#28a745", "#dc3545"],
                    data: [remaining_quantity, quantity-remaining_quantity ]
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

function fill_sample_info() {
    $("#uuid").html(sample["uuid"]);
    $("#sample_href").attr("href", sample["_links"]["self"])
    $("#remaining_quantity").attr("value", parseFloat(sample["remaining_quantity"]));
    $("#original_quantity").attr("value", parseFloat(sample["quantity"]));
    $("#remaining_metric").html(get_metric(sample["base_type"]));
    $("#original_metric").html(get_metric(sample["base_type"]));


    if (sample["base_type"] == "Cell") {
        $("#fixation_type_th").show()
    }

}

function subtract_quantity() {
    var remaining_quantity = sample["remaining_quantity"];

    var quantities = 0.0;

    $('input[type="number"].aliquotted-quantity').each(function () {
        quantities += parseFloat($(this).val());
    });

    $("#remaining_quantity").attr("value", remaining_quantity-quantities);
    update_graph();

    if ((remaining_quantity - quantities) < 0) {
        $("#quantityalert").show();

        $("#submit").attr("disabled", true);
    }

    else {
        $("#quantityalert").hide();
        $("#submit").attr("disabled", false);
    }

}

function update_number() {
    $("#total_aliquots").html($("#aliquoted_sample_table > tbody tr").length);
}

function generate_container_select(indx) {
    console.log(container_information);
    var containers = container_information[sample["base_type"]]

    var containers_list = containers["container"];

    // Start select
    var select_html = '<select class="form-control" data-live-search=true id="container_select_'+indx+'">';

    for (i in containers_list) { 
        select_html += '<option value="' + containers_list[i][0] + '">'+containers_list[i][1] + '</option>'
    }

    // End html
    select_html += '</select>'
    return select_html;
}


function generate_fixation_select(indx) {
    var containers = container_information[sample["base_type"]]
    var fixation_list = containers["fixation_type"]

    // Start select
    var select_html = '<select class="form-control" data-live-search=true>'


    for (i in fixation_list) {
        select_html += '<option value="' + fixation_list[i][0] + '">'+fixation_list[i][1] + '</option>'
    }

    // End select
    select_html += '</select>'
    return select_html;
}

function copy_row(indx) {
    $("row_"+indx).clone().appendTo("#aliquoted_sample_table");
}

function make_new_form(indx) {
    var row_form_html = '';

    // Start Row
    row_form_html += '<tr id="row_'+indx+'">';
    // Container
    row_form_html += '<td>'+generate_container_select(indx)+'</td>'
    if (sample["base_type"] == "Cell") {
        row_form_html += '<td>'+generate_fixation_select(indx)+'</td>';
    }
    // Volume start
    row_form_html += '<td>';
    row_form_html += '<input id="volume_'+indx+'" type="number" class="form-control aliquotted-quantity" step="0.05" min="0.01" value="0.01">'
    row_form_html += '</td>';
    // Volume end
    row_form_html += '<td>';
    row_form_html += '<input id="barcode_'+indx+'" type="text" class="form-control barcode" placeholder="Sample Barcode"></td>'
    row_form_html += '<td>'
    row_form_html += '<div id="trash_'+indx+'" class="btn btn-danger windows"><i class="fa fa-trash"></i></div>';
    row_form_html += '<div id="cpy_'+indx+'" class="btn btn-primary copy"><i class="fa fa-copy"></i></div>';

    row_form_html += '</td>'
    // End Row
    row_form_html += '</tr>';


    $("#aliquoted_sample_table > tbody:last-child").append(row_form_html);
    update_number();
    subtract_quantity();
    indexes.push(indx);

    // Because Windows is trash.
    $(".windows").click(function() {
        var to_remove = $(this).attr("id").split("_")[1]
        remove_row(to_remove);
        subtract_quantity();
    });

    $(".copy").click(function() {
        copy_row();
    })



    $(".aliquotted-quantity").change(function() {
        subtract_quantity();
    });

    $('#aliquotted_quantity').on('change keyup', function() {
        // Remove invalid characters
        var sanitized = $(this).val().replace(/[^0-9]/g, '');
        // Update value
        $(this).val(sanitized);
    });

    $(".barcode").change(function() {
        $(this).val(remove_whitespace($(this).val()));
        // If the barcode is in the database
        
        if ($(this).val() != "") {
            if (check_barcode_database($(this).val()) == true ) {
                $("#submit").attr("disabled", true);
                $("#database_error").show();
            }
            else {
                $("#submit").attr("disabled", false);
                $("#database_error").hide();

            }
        }

        if (check_barcode_form() == true) {
            $("#submit").attr("disabled", true);
            $("#duplicate_barcode").show();
        }

        else {
            $("#submit").attr("disabled", false);
            $("#duplicate_barcode").hide();
        }
        

        
    });
}

function remove_row(indx) {
    $("#row_"+indx).remove();
    indexes.splice( $.inArray(indx, indexes), 1 );
    update_number();

}

function preprate_data() {

    var a = [];

    indexes.forEach(function(i) {

        var aliquot = {
            container: $("#container_select_"+i).val(),
            volume: $("#volume_"+i).val(),
            barcode: $("#barcode_"+i).val()

        }

        a.push(aliquot);

    });

    var data = {
        processing_protocol: $("#processing_protocol").val(),
        processed_by: $("#processed_by").val(),
        aliquot_date: $("#aliquot_date").val(),
        aliquot_time: $("#aliquot_time").val(),
        parent_id: sample["id"],
        comments: $("#comments").val(),
        aliquots: a

    }


    var json = (function () {
        var json = null;
        $.post({
            'async': false,
            'global': false,
            'url': sample["_links"]["webapp_aliquot"],
            'contentType': 'application/json',
            'data': JSON.stringify(data),
            'success': function (data) {
                json = data;
                window.location.href = json["content"]["_links"]["self"];
                
            },
            'error': function (data) {
                $("#error_code").html(data.status);
                $("#aliquot_error").show();
            }
        });
        return json;
    })();
}

$(document).ready(function () {
    fill_sample_info();
    update_graph();

    var indx = 1;
    make_new_form(indx);

    $("[name=new]").click(function(){ 
        indx += 1;
        make_new_form(indx);
    });


    $("#submit").click(function() {
        $('#confirmationModal').modal("toggle");
    });

    $("#modalSubmit").click(function() {
        preprate_data();
    })

});

