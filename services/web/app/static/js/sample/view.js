/*
Copyright (C) 2020 Keiron O'Shea <keo7@aber.ac.uk>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
*/

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



function get_barcode(sample_info, barc_type) {
    
    var url = encodeURI(sample_info["_links"]["barcode_generation"]);

    $.post({
        async: false,
        global: false,
        url: url,
        dataType: "json",
        contentType: 'application/json',
        data: JSON.stringify ({
            "type": barc_type,
            "data": sample_info["uuid"]
        }),
        success: function (data) {
            $("#barcode").attr("src", "data:image/png;base64," + data["b64"]);
        },

    });



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
    $("#comments").text(comments);
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

    $("#consent_date").html(consent_information);


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

function deactivate_nav() {
    $("#basic-info-nav").removeClass("active");
    //$("#collection-nav").removeClass("active");
    $("#processing-nav").removeClass("active");
    $("#associated-documents-nav").removeClass("active");
    $("#sample-review-nav").removeClass("active");
    $("#lineage-nav").removeClass("active");
    $("#custom-attr-nav").removeClass("active");
}

function hide_all() {
    var tim = 50;
    $("#basic-info").fadeOut(50);
    //$("#collection-info").fadeOut(50);
    $("#processing-info").fadeOut(50);
    $("#associated-documents").fadeOut(50);
    $("#lineage-info").fadeOut(50);

}


$(document).ready(function() {
    var sample_info = get_sample();
    
    $("#loading-screen").fadeOut();
    get_barcode(sample_info, "qrcode");

    fill_title(sample_info);
    fill_basic_information(sample_info);
    fill_quantity_chart(sample_info["type"], sample_info["quantity"], sample_info["remaining_quantity"]);
    //fill_collection_information(sample_info["collection_information"]);
    fill_consent_information(sample_info["consent_information"]);
    // fill_processing_information(sample_info["processing_information"]);
    fill_lineage_table(sample_info["subsamples"]);
    fill_comments(sample_info["comments"]);
    fill_document_information(sample_info["documents"]);
    $("#content").delay(500).fadeIn();


    $("#qrcode").click(function() {
        get_barcode(sample_info, "qrcode");

    });

    $("#datamatrix").click(function() {
        get_barcode(sample_info, "datamatrix");

    });

    $("#print-label-btn").click(function() {
        window.location.href = sample_info["_links"]["label"]
    });

    $("#basic-info-nav").on("click", function() {
        deactivate_nav();
        $(this).addClass("active");
        hide_all();
        $("#basic-info").fadeIn(100);
    });

    $("#collection-nav").on("click", function() {
        deactivate_nav();
        $(this).addClass("active");
        hide_all();
        $("#collection-info").fadeIn(100);
    });

    $("#processing-nav").on("click", function() {
        deactivate_nav();
        $(this).addClass("active");
        hide_all();
        $("#processing-info").fadeIn(100);
    });

    $("#associated-documents-nav").on("click", function() {
        deactivate_nav();
        $(this).addClass("active");
        hide_all();
        $("#associated-documents").fadeIn(100);
    });

    $("#lineage-nav").on("click", function() {
        deactivate_nav();
        $(this).addClass("active");
        hide_all();
        $("#lineage-info").fadeIn(100);
    });
});