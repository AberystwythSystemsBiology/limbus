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

function make_doughnut(dom_id, data, labels, title) {
    new Chart(document.getElementById(dom_id), {
        type: 'doughnut',
        data: {
          labels: labels,
          datasets: [{
                data: data,
                backgroundColor: dynamicColours(labels.length)
            }],

        },
        options: {
            legend: {
                display: true
            },
            title: {
                display: true,
                text: title
               }}}
        );
}


function fill_document_statistics(document_statistics) {

    new Chart(document.getElementById("document_type"), {
        type: 'bar',
        data: {
          labels: document_statistics["document_type"]["labels"],
          datasets: [{
                data: document_statistics["document_type"]["data"],
                backgroundColor: dynamicColours(document_statistics["document_type"]["labels"].length)
            }],

        },
        options: {
            legend: {
                display: false
            },
            title: {
                display: true,
                text: "Document Type"
               }}}
        );
}

function fill_attribute_statistics(attribute_statistics) {
    new Chart(document.getElementById("attribute_type"), {
        type: 'bar',
        data: {
          labels: attribute_statistics["attribute_type"]["labels"],
          datasets: [{
                data: attribute_statistics["attribute_type"]["data"],
                backgroundColor: dynamicColours(attribute_statistics["attribute_type"]["labels"].length)
            }],

        },
        options: {
            legend: {
                display: false
            },
            title: {
                display: true,
                text: "Attribute Type"
               }}}
        );
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
                dispfill_donor_statisticslay: true,
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

function fill_protocol_statistics(protocol_statistics) {
    new Chart(document.getElementById("protocol_type"), {
        type: 'bar',
        data: {
          labels: protocol_statistics["protocol_type"]["labels"],
          datasets: [{
                data: protocol_statistics["protocol_type"]["data"],
                backgroundColor: dynamicColours(protocol_statistics["protocol_type"]["labels"].length)
            }],

        },
        options: {
            legend: {
                display: false
            },
            title: {
                display: true,
                text: "Protocol Type"
               }}}
        );
}

function fill_donor_statistics(donor_statistics) {
    make_doughnut("donor_status", donor_statistics["donor_status"]["data"], donor_statistics["donor_status"]["labels"], "Donor Status");
    console.log(donor_statistics);
    make_doughnut("donor_sex", donor_statistics["donor_sex"]["data"], donor_statistics["donor_sex"]["labels"], "Donor Sex");
    make_doughnut("donor_race", donor_statistics["donor_race"]["data"], donor_statistics["donor_race"]["labels"], "Donor Race");

}

function fill_basic_statistics(basic_statistics) {
    $("#donor_count").html(basic_statistics["donor_count"]);
    $("#sample_count").html(basic_statistics["sample_count"]);
    $("#user_count").html(basic_statistics["user_count"]);
    $("#site_count").html(basic_statistics["site_count"]);
}

function fill_panel() {
    var panel_info = get_panel_info();
    $("#biobank_name").html(panel_info["name"]);
    fill_basic_statistics(panel_info["basic_statistics"]);
    fill_sample_statistics(panel_info["sample_statistics"]);
    fill_donor_statistics(panel_info["donor_statistics"]);
    fill_document_statistics(panel_info["document_statistics"]);
    fill_attribute_statistics(panel_info["attribute_statistics"]);
    fill_protocol_statistics(panel_info["protocol_statistics"]);

}

$(document).ready(function() {

    fill_panel();
    $("#loading-screen").fadeOut();
    $("#content").delay(500).fadeIn();

});