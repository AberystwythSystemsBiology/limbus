function get_sample() {
    var api_url = encodeURI(window.location+'/data');

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

function get_metric(type) {
    if (type == "Fluid") {
        var metric = "mL";
    }
    else if (type == "Molecular") {
        var metric = "μg/mL";
    }
    else {
        var metric = "Cell(s)"
    }

    return metric
}


function fill_quantity_chart(type, quantity, remaining_quantity) {
    
    var metric = get_metric(type);


    new Chart(document.getElementById("quantity-chart"), {
        type: 'pie',
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

$(document).ready(function() {
    var sample_info = get_sample();
    
    $("#loading-screen").fadeOut();
    fill_quantity_chart(sample_info["type"], sample_info["quantity"], sample_info["remaining_quantity"])
    $("#content").delay(500).fadeIn();

});