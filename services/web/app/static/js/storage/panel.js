function get_panel_information() {
    var api_url = encodeURI(window.location+'/endpoint');
    
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


function render_counts(basic_statistics) {
    $("#site_count").html(basic_statistics["site_count"]);
    $("#room_count").html(basic_statistics["site_count"]);
    $("#building_count").html(basic_statistics["building_count"]);
    $("#cold_storage_count").html(basic_statistics["cold_storage_count"]);


}

function render_cold_storage_statistics(cold_storage_statistics) {
    new Chart(document.getElementById("cold_storage_type"), {
        type: 'horizontalBar',
        data: {
          labels: cold_storage_statistics["cold_storage_type"]["labels"],
          datasets: [{
                data: cold_storage_statistics["cold_storage_type"]["data"],
                backgroundColor: dynamicColours(cold_storage_statistics["cold_storage_type"]["labels"].length)
            }],

        },
        options: {
            legend: {
                display: false
            },
            title: {
                display: true,
                text: "Cold Storage Type"
               }}}
        );


        new Chart(document.getElementById("cold_storage_temp"), {
            type: 'doughnut',
            data: {
              labels: cold_storage_statistics["cold_storage_temp"]["labels"],
              datasets: [{
                    data: cold_storage_statistics["cold_storage_temp"]["data"],
                    backgroundColor: dynamicColours(cold_storage_statistics["cold_storage_temp"]["labels"].length)
                }],
    
            },
            options: {
                legend: {
                    display: true
                },
                title: {
                    display: true,
                    text: "Cold Storage Temperatures"
                   }}}
            );
}

$(document).ready(function() {
    var panel_information = get_panel_information();
    render_counts(panel_information["basic_statistics"]);
    render_cold_storage_statistics(panel_information["cold_storage_statistics"]);
    $("#loading-screen").fadeOut();
    $("#content").delay(500).fadeIn();
});