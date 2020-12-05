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



function fill_title(sample) {

    var author_information = sample["author"];
    var title_html = render_colour(sample["colour"]);
    title_html += sample["uuid"]
    $("#uuid").html(title_html);
    var author_html = ""+author_information["first_name"]+" "+author_information["last_name"]
    $("#created_by").html(author_html);
    $("#created_on").html(sample["created_on"]);

    if ( sample["source"] != "New" ) {
        var parent_html = '';
        parent_html += '<a href="'+sample["parent"]["_links"]["self"]+'" target="_blank">'
        parent_html += '<i class="fas fa-vial"></i> ';
        parent_html += sample["parent"]["uuid"]
        parent_html += '</a>'
        $("#parent").html(parent_html);
        $("#parent-div").show();
    }

   
}

function fill_comments(comments) {
    if (comments == "") {
        var comments = "No comments available";
    }
    $("#comments").html(comments);
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

function fill_basic_information(sample_information) {
    var html = "";

    if (sample_information["type"] == "Fluid") {
        var measurement = "mL";
        var sample_type = sample_information["sample_type_information"]["flui_type"];
    }

    else if (sample_information["type"] == "Molecular") {
        var measurement = "μg/mL";
        var sample_type = sample_information["sample_type_information"]["mole_type"];

    }

    else {
        var measurement = "Cells";
        var sample_type = sample_information["sample_type_information"]["cell_type"];
    }

    html += render_content("Status", sample_information["status"]);
    html += render_content("Biobank Barcode", sample_information["barcode"]);
    html += render_content("Biohazard Level", sample_information["biohazard_level"]);
    html += render_content("Type", sample_information["type"]);
    html += render_content("Sample Type", sample_type);


    html += render_content("Quantity", sample_information["remaining_quantity"] + " / " + sample_information["quantity"] + " " + measurement);

    $("#basic-information").html(html);
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
    if (document_information.length) {
        $("#documentTable").DataTable( {
            data: document_information,
            pageLength: 5,
            columns: [
                {
                    mData: {},
                    mRender: function(data, type, row) {
                        console.log(data)

                        document_data = "<a href='"+data["_links"]["self"]+"'>";
                        document_data += '<i class="fas fa-file"></i> LIMBDOC-'
                        document_data += data["id"] + ": "
                        document_data += data["name"] + "</a>"
                        return document_data
                    }
                },
                {
                    mData: {},
                    mRender: function(data, type, row) {
                        return data["type"]
                    }
                }
                
            ]
        });

    }
    
    else {
        $("#documents").hide();
    }

}

function fill_lineage_table(subsamples) {

    if (subsamples.length > 0) {
        $('#subSampleTable').DataTable( {
            data: subsamples,
            pageLength: 5,
            columns: [
                {
                    "mData": {},
                    "mRender": function (data, type, row) {
                        var col_data = '';
                        col_data += render_colour(data["colour"])
                        col_data += "<a href='"+data["_links"]["self"]+ "'>";
                        col_data += '<i class="fas fa-vial"></i> '
                        col_data += data["uuid"];
                        col_data += "</a>";
                        if (data["source"] != "New") {
    
                        col_data += '</br><small class="text-muted"><i class="fa fa-directions"></i> ';
                        col_data += '<a href="'+data["parent"]["_links"]["self"]+'" target="_blank">'
                        col_data += '<i class="fas fa-vial"></i> ';
                        col_data += data["parent"]["uuid"],
                        col_data += "</a></small>";
                    }
    
                        return col_data
                    }
                },
                {data: "type"},
                {
                    "mData": {},
                    "mRender": function (data, type, row) {
                        var percentage = data["remaining_quantity"] / data["quantity"] * 100 + "%"
                        var col_data = '';
                        col_data += '<span data-toggle="tooltip" data-placement="top" title="'+percentage+' Available">';
                        col_data += data["remaining_quantity"]+"/"+data["quantity"]+get_metric(data["type"]); 
                        col_data += '</span>';
                        return col_data
                    }
            },
    
            ],
            
        });
    }


    else {
        $("#lineage").hide();
    }
    
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

    fill_title(sample_info);
    fill_basic_information(sample_info);
    fill_quantity_chart(sample_info["type"], sample_info["quantity"], sample_info["remaining_quantity"]);
    fill_collection_information(sample_info["collection_information"]);
    fill_consent_information(sample_info["consent_information"]);
    fill_processing_information(sample_info["processing_information"]);
    fill_lineage_table(sample_info["subsamples"]);
    fill_comments(sample_info["comments"]);
    fill_document_information(sample_info["documents"]);
    $("#content").delay(500).fadeIn();


    $("#qrcode").click(function() {
        get_barcode("qrcode");

    });

    $("#datamatrix").click(function() {
        get_barcode("datamatrix");

    });


    $("#print-label-btn").click(function() {
        window.location.href = sample_info["_links"]["label"]
    });

});