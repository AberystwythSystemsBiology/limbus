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
    row_form_html += '<tr row="row_"'+indx+'>';

    row_form_html += '<td><select class="form-control" data-live-search=true></select></td>'
    row_form_html += '<td><input type="number" class="form-control"></td>'
    row_form_html += '<td><input type="text" class="form-control"></td>'
    row_form_html += '<td>'
    row_form_html += '<div name="remove_'+indx+'" id="trash" class="btn btn-danger btn-sm"><i class="fa fa-trash"></i></div>';
    row_form_html += '</td>'

    // End Row
    row_form_html += '</tr>';

    $("#aliquoted_sample_table > tbody:last-child").append(row_form_html);
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
});

