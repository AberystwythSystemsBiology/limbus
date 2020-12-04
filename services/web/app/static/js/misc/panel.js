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

function make_doughnut(dom_id, data, labels) {
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
                display: false
               }}}
        );
}

function make_pie(dom_id, data, labels) {
    new Chart(document.getElementById(dom_id), {
        type: 'pie',
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
                display: false
               }}}
        );
}

function make_bar(dom_id, data, labels) {
    new Chart(document.getElementById(dom_id), {
        type: 'bar',
        data: {
          labels: labels,
          barThickness: "flex",
          datasets: [{
                data: data,
                backgroundColor: dynamicColours(labels.length)
            }],

        },
        options: {
            legend: {
                display: false
            },
            title: {
                display: false
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
                display: false,
                text: "Attribute Type"
               }}}
        );
}

function fill_sample_statistics(sample_statistics) {
    make_doughnut("sample_status", sample_statistics["sample_status"]["data"], sample_statistics["sample_status"]["labels"], "");
    make_bar("sample_source", sample_statistics["sample_source"]["data"], sample_statistics["sample_source"]["labels"], "");
    make_pie("sample_biohazard", sample_statistics["sample_biohazard"]["data"], sample_statistics["sample_biohazard"]["labels"], "");
    make_doughnut("sample_type", sample_statistics["sample_type"]["data"], sample_statistics["sample_type"]["labels"], "");


}

function fill_protocol_statistics(protocol_statistics) {
    make_pie("protocol_type", protocol_statistics["protocol_type"]["data"], protocol_statistics["protocol_type"]["labels"], "");

}

function fill_donor_statistics(donor_statistics) {
    make_doughnut("donor_status", donor_statistics["donor_status"]["data"], donor_statistics["donor_status"]["labels"], "Donor Status");
    make_pie("donor_sex", donor_statistics["donor_sex"]["data"], donor_statistics["donor_sex"]["labels"], "Donor Sex");
    make_bar("donor_race", donor_statistics["donor_race"]["data"], donor_statistics["donor_race"]["labels"], "Donor Race");

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
    $("body").css({"backgroundColor":"#f8f9fa"});
    fill_panel();
    $("#loading-screen").fadeOut();
    $("#content").delay(500).fadeIn();

});