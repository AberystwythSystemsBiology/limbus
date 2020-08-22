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
        }}
        );
}

function fill_sample_info(sample) {
    $("#uuid").html(sample["uuid"]);
    $("#remaining_quantity").attr("value", parseFloat(sample["remaining_quantity"]));
    $("#original_quantity").attr("value", parseFloat(sample["quantity"]));
    $("#remaining_metric").html(get_metric(sample["type"]));
    $("#original_metric").html(get_metric(sample["type"]));

}

function subtract_quantity() {
    $("#remaining_quantity").attr("value", $("#remaining_quantity").val()-0.12);
    update_graph();
}

$(document).ready(function() {
    var sample = get_sample();
    fill_sample_info(sample);
    update_graph();

    $("#cliky").click(function() {
        subtract_quantity();
    });
});
