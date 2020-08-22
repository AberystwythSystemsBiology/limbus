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
                    data: [remaining_quantity, quantity - remaining_quantity]
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

function fill_sample_info(sample) {
    $("#uuid").html(sample["uuid"]);
    $("#sample_href").attr("href", sample["_links"]["self"])
    $("#remaining_quantity").attr("value", parseFloat(sample["remaining_quantity"]));
    $("#original_quantity").attr("value", parseFloat(sample["quantity"]));
    $("#remaining_metric").html(get_metric(sample["type"]));
    $("#original_metric").html(get_metric(sample["type"]));

}

function subtract_quantity() {
    $("#remaining_quantity").attr("value", $("#remaining_quantity").val() - 0.12);
    update_graph();
}

function update_number() {
    $("#total_aliquots").html($("#aliquoted_sample_table > tbody tr").length);
}

function make_new_form(indx) {
    var row_form_html = '';

    // Start Row
    row_form_html += '<tr id="row_'+indx+'">';

    row_form_html += '<td><select class="form-control" data-live-search=true></select></td>'
    row_form_html += '<td>';
    row_form_html += '<div class="input-group mb-2">'
    row_form_html += '<input name="aliquotted_quantity" type="number" class="form-control" step="0.01" min="0.0" value="0.0"></td>'
    row_form_html += '<div class="input-group-append">'
    row_form_html += '<div class="input-group-text"><span id="remaining_metric">ERR</span></div>'
    row_form_html += '</div></div>'
    row_form_html += '<td><input type="text" class="form-control" placeholder="Sample Barcode"></td>'
    row_form_html += '<td>'
    row_form_html += '<div id="trash_'+indx+'" class="btn btn-danger windows"><i class="fa fa-trash"></i></div>';
    row_form_html += '</td>'
    // End Row
    row_form_html += '</tr>';

    $("#aliquoted_sample_table > tbody:last-child").append(row_form_html);
    update_number();
}

function remove_row(indx) {
    $("#row_"+indx).remove();
    update_number();

}

$(document).ready(function () {
    var sample = get_sample();
    fill_sample_info(sample);
    update_graph();

    var indx = 1;

    make_new_form(indx);

    $("[name=new]").click(function(){ 
        indx += 1;
        make_new_form(indx);
    });

    $('#aliquotted_quantity').on('change keyup', function() {
        // Remove invalid characters
        var sanitized = $(this).val().replace(/[^0-9]/g, '');
        // Update value
        $(this).val(sanitized);
      });

    // Because Windows is trash.
    $(".windows").click(function() {
        var to_remove = $(this).attr("id").split("_")[1]
        remove_row(to_remove);
    });
});

