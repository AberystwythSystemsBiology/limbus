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



function get_barcode(type) {
    var barcode_url = encodeURI(window.location+'/barcode/'+type);
    $("#barcode").attr("src", barcode_url);

}

function render_content(label, content) {
    if (content == undefined) {
        content = "Not Available."
    }
    return '<div class="row"><div class="col-5">'+ label + ':</div><div class="col-7">'+content+'</div></div>';
     
}

function fill_title(uuid) {
    var html = "";
    html += '<span class="colour-circle bg-primary"></span>'
    html += uuid
    $("#uuid").html(html);
}


function fill_collection_information(collection_information) {
    
    var protocol_info = collection_information["protocol"];
    var html = "";
    
    html += '<div class="media">';
    html += '<h1 class="align-self-start mr-3"><i class="fab fa-buffer"></i></h1>'
    html += '<div class="media-body">'
    html += '<a href="' + protocol_info["_links"]["self"] +'" target="_blank">'
    html += '<h5 class="mt-0">LIMBPRO-'+protocol_info["id"]+': '+protocol_info["name"] +'</h5>'
    html += '</a>'
    html += render_content("Collected On", collection_information["datetime"])
    html += render_content("Collected By", collection_information["undertaken_by"])
    html += render_content("Comments", collection_information["comments"])

    html += '</div>'
    html += '</div>'

    $("#collection_information").html(html);
}

function fill_consent_information(consent_information) {
    
    $("#consent_name").html(consent_information["template"]["name"]);
    $("#consent_version").html(consent_information["template"]["version"]);
    $("#consent_identifier").html(consent_information["identifier"]);
    $("#consent_comments").html(consent_information["comments"]);
    

    for (answer in consent_information["answers"]) {
        var answer_info = consent_information["answers"][answer];
        
        var answer_html = '';
        answer_html += '<li class="list-group-item flex-column align-items-start"><div class="d-flex w-100 justify-content-between"><h5 class="mb-1">Answer ';
        answer_html += + (parseInt(answer)+1) + '<h5></div><p class="mb-1">'+ answer_info["question"] + '</p></li>';
        
        $("#questionnaire-list").append(answer_html);
    }

    $("#consent_date_signed").html(consent_information);


}

function fill_basic_information(sample_info) {

    var html = "";

    html += render_content("Biobank Barcode", sample_info["barcode"])
    html += render_content("Sample Type", sample_info["type"])
    html += render_content("Biohazard Level", sample_info["biohazard_level"])


    $("#basic_information").html(html);
}


function fill_processing_information(processing_information) {
    var protocol_info = processing_information["protocol"];
    var html = "";
    
    html += '<div class="media">';
    html += '<h1 class="align-self-start mr-3"><i class="fab fa-buffer"></i></h1>'
    html += '<div class="media-body">'
    html += '<a href="' + protocol_info["_links"]["self"] +'" target="_blank">'
    html += '<h5 class="mt-0">LIMBPRO-'+protocol_info["id"]+': '+protocol_info["name"] +'</h5>'
    html += '</a>'
    html += render_content("Processed On", processing_information["datetime"])
    html += render_content("Processed By", processing_information["undertaken_by"])
    html += render_content("Comments", processing_information["comments"])

    html += '</div>'
    html += '</div>'

    $("#processing_information").html(html);
}

function fill_document_information(document_information) {

}


function fill_quantity_chart(type, quantity, remaining_quantity) {
    
    var metric = get_metric(type);

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

$(document).ready(function() {
    var sample_info = get_sample();
    
    $("#loading-screen").fadeOut();
    get_barcode("qrcode");

    fill_title(sample_info["uuid"]);
    fill_basic_information(sample_info);
    fill_quantity_chart(sample_info["type"], sample_info["quantity"], sample_info["remaining_quantity"]);
    fill_collection_information(sample_info["collection_information"]);
    fill_consent_information(sample_info["consent_information"]);
    fill_processing_information(sample_info["processing_information"])
    $("#content").delay(500).fadeIn();


    $("#qrcode").click(function() {
        get_barcode("qrcode");

    });

    $("#datamatrix").click(function() {
        get_barcode("datamatrix");

    });


});