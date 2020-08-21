function get_panel_info() {
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


function dynamicColours(length) {
    var colours = [];
    for (i =0; i < length; i++) {
        var r = Math.floor(Math.random() * 255);
        var g = Math.floor(Math.random() * 255);
        var b = Math.floor(Math.random() * 255);
        colours.push("rgba(" + r + "," + g + "," + b + ", 1)");
    }
    return colours;
    
}

function fill_sample_statistics(sample_statistics) {
    new Chart(document.getElementById("sample_status"), {
        type: 'doughnut',
        data: {
          labels: sample_statistics["sample_status"]["labels"],
          datasets: [{
                data: sample_statistics["sample_status"]["data"],
                backgroundColor: dynamicColours(sample_statistics["sample_status"]["labels"].length)
            }],

        },
        options: {
            legend: {
                position: "bottom"
            },
            title: {
                display: true,
                text: "Sample Status"
               }}}
        );

        new Chart(document.getElementById("sample_source"), {
            type: 'doughnut',
            data: {
              labels: sample_statistics["sample_source"]["labels"],
              datasets: [{
                    data: sample_statistics["sample_source"]["data"],
                    backgroundColor: dynamicColours(sample_statistics["sample_source"]["labels"].length)

                }],
    
            },
            options: {
                legend: {
                    position: "bottom"
                },
                title: {
                    display: true,
                    text: "Sample Source"
                   }}}
            );
            new Chart(document.getElementById("sample_type"), {
                type: 'doughnut',
                data: {
                  labels: sample_statistics["sample_type"]["labels"],
                  datasets: [{
                        data: sample_statistics["sample_type"]["data"],
                        backgroundColor: dynamicColours(sample_statistics["sample_type"]["labels"].length)

                    }],
        
                },
                options: {
                    legend: {
                        position: "bottom"
                    },
                    title: {
                        display: true,
                        text: "Sample Type"
                       }}}
                );

                new Chart(document.getElementById("sample_biohazard"), {
                    type: 'doughnut',
                    data: {
                      labels: sample_statistics["sample_biohazard"]["labels"],
                      datasets: [{
                            data: sample_statistics["sample_biohazard"]["data"],
                            backgroundColor: dynamicColours(sample_statistics["sample_biohazard"]["labels"].length)

                        }],
            
                    },
                    options: {
                        legend: {
                            position: "bottom"
                        },
                        title: {
                            display: true,
                            text: "Sample Biohazard Level"
                           }}}
                    );


}

function fill_basic_statistics(basic_statistics) {
    $("#donor_count").html(basic_statistics["donor_count"]);
    $("#sample_count").html(basic_statistics["sample_count"]);
    $("#user_count").html(basic_statistics["user_count"]);
    $("#site_count").html(basic_statistics["site_count"]);
}

$(document).ready(function() {
    var panel_info = get_panel_info();
    $("#biobank_name").html(panel_info["name"]);
    fill_basic_statistics(panel_info["basic_statistics"]);
    fill_sample_statistics(panel_info["sample_statistics"]);

});