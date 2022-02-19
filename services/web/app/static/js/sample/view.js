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
    var api_url = encodeURI(window.location + '/data');

    var json = (function () {
        var json = null;
        $.ajax({
            'async': false,
            'global': false,
            'url': api_url,
            'dataType': "json",
            'success': function (data) {
                json = data;
            },
            'failure': function (data) {
                json = data;
            }
            
        });
        return json;
    })();

    return json;
   

}



function get_barcode(sample_info, barc_type) {

    var url = encodeURI(sample_info["_links"]["barcode_generation"]);

    $.ajax({
        type: "post",
        async: false,
        global: false,
        url: url,
        dataType: "json",
        contentType: 'application/json',
        data: JSON.stringify({
            "type": barc_type,
            "data": sample_info["uuid"]
        }),
        success: function (data) {
            $("#barcode").attr("src", "data:image/png;base64," + data["b64"]);
        },

    });

}


function add_samples_to_cart(api_url, samples) {
    var msg = "Adding a sample to cart will remove it from storage, press OK to proceed!";
    if (!confirm(msg)) {
      return false;
    }

    var json = (function () {
       var json = null;
       $.ajax({
           'async': false,
           'global': false,
           'url': api_url,
           'type': 'POST',
           'dataType': "json",
           'data': JSON.stringify({"samples": samples}),
           'contentType': 'application/json; charset=utf-8',
           'success': function (data) {
               json = data;
               $("#cart-confirmation-msg").html(data["message"]);
               $("#cart-confirmation-modal").modal({
                   show: true
               });
               },
           'failure': function (data) {
               json = data;
               $("#cart-confirmation-msg").html(data["message"]);
               $("#cart-confirmation-modal").modal({
                   show: true
               });
               }
       });

       return json;
    })();

    return json;
}


function fill_title(sample) {

    var author_information = sample["author"];
    var title_html = render_colour(sample["colour"]);
    title_html += sample["uuid"];
    if (sample["is_closed"]) {
        title_html += "  <i class=\"fas fa-archive\" style=\"color:yellow;\"></i>"
    } else if (sample["is_locked"]) {
        title_html += "  <i class=\"fa fa-lock\" style=\"color:yellow; padding-left: 3px;\"></i>"
    }

    $("#uuid").html(title_html);

    var edit_link = sample["consent_information"]["_links"]["remove"];
    edit_link = edit_link.replace("/donor/consent/", "/donor/sample/"+sample["uuid"]+"/consent/");
    edit_link = edit_link.replace("/remove", "/edit");
    $("#action-edit-consent").attr("href", edit_link);

    var author_html = "" + author_information["first_name"] + " " + author_information["last_name"]
    $("#created_by").html(author_html);
    $("#created_on").html(sample["created_on"]);

    if (sample["source"] != "New") {
        var parent_html = '';
        parent_html += '<a href="' + sample["parent"]["_links"]["self"] + '" target="_self">';
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


function fill_consent_information(consent_information) {
    //console.log("consent_information", consent_information)
    $("#consentModalLabel").html("Digital Consent Form: "+"LIMBDC-"+consent_information["id"])
    $("#consent_name").html(consent_information["template"]["name"]);
    $("#consent_version").html(consent_information["template"]["version"]);
    $("#consent_identifier").html(consent_information["identifier"]);
    $("#consent_comments").html(consent_information["comments"]);
    $("#consent_undertakenby").html(consent_information["undertaken_by"]);


    var study = consent_information["study"]
    try {
        doilink="";
        if (study["protocol"]["name"]["doi"]!="") {
            var link = doi2url(study["protocol"]["doi"]);
            doilink += '<a href=' + link + '>' + '<a href=' + link + '>' + '[' + study["protocol"]["doi"] + '] ';
            doilink += study["protocol"]["name"] + '</a>';
        }  else {
            doilink += study["protocol"]["name"];
        }
        $("#consent_study").html(doilink);
        $("#consent_refno").html(study['reference_id']);
    } catch {
        $("#consent_study").html("");
        $("#consent_refno").html("");
   }

    let answer_ids = [];
    for (answer in consent_information["answers"]) {
        var answer_info = consent_information["answers"][answer];
        answer_ids.push(answer_info["id"])
    }
    $("#questionnaire-list").html("")
    for (question in consent_information["template_questions"]) {
            var question_info = consent_information["template_questions"][question];
            var answer_html = '';
            answer_html += '<li class="list-group-item flex-column align-items-start"><div class="d-flex w-100 justify-content-between"><h5 class="mb-1">Item ';
            answer_html += +(parseInt(question) + 1);
            if (answer_ids.includes(question_info["id"])) {
                answer_html += '  <i class="fas fa-check" style="color:green;"></i><h5></div>';
                answer_html += '<p class="mb-1">' + question_info["question"] + '</p>';
            } else {
                answer_html += '<i class="fas fa-minus-circle" style="color:red;"></i><h5></div>';
                answer_html += '<p class="mb-1" style="text-decoration: line-through;">' + question_info["question"]+ '</p>';
            }

            answer_html += '</li>';

            $("#questionnaire-list").append(answer_html);

    }

    var consent_status = "Active"
    if (consent_information["withdrawn"]==true) {
        consent_status = "Withdrawn"
    }
    donor_link = ""
    var donor_id = consent_information["donor_id"];
    if (donor_id != null) {
        donor_link += "<a href=" + window.location.origin + "/donor/LIMBDON-" + donor_id + ">";
        donor_link += '<i class="fa fa-user-circle"></i>' + "LIMBDON-" + donor_id + "</a>";
        $("#donor_id").html(donor_link);
        $("#donor").html(donor_link);

    }
    else {
        $("#donor_id").text(donor_link);
    }
    $("#consent_date").html(consent_information["date"]);
    $("#consent_status").html(consent_status);
    $("#withdrawal_date").html(consent_information["withdrawal_date"]);

    $('#print-consent').on('click', function () {
      var header = "Digital Consent Form: "+"LIMBDC-"+consent_information["id"];
      printCard(header);
    })

    function printCard(header) {
        var divContents = document.getElementById("card-content").innerHTML;
        var doc = window.open('', '');
        doc.document.write('<html>');
        doc.document.write('<body ><h5>'+ header +'</h5><br>');
        doc.document.write(divContents);
        doc.document.write('</body></html>');
        doc.document.close();
        doc.print();
    }
}


function def_remove_attrdata(el) {
    $("#"+el).click(function () {
        var id = $(this).attr("id").split("-")[2];
        var limbscad_id = "LIMBSCAD-" + id;
        var warning_msg = "<B>Warning:</B> This action cannot be undone!";
        $("#delete-protocol-warning").html(warning_msg)
        $("#delete-protocol-event-confirm").html("To confirm, enter "+"<B>"+limbscad_id+"</B>");
        $("#protocol-uuid-remove-confirmation-input").val("").attr("placeholder", "Type "+limbscad_id+" here").show();
        $("#delete-protocol-confirm-modal").modal({
            show: true
        });

        var removal_link = window.location + "/attribute/" + limbscad_id + "/remove";

        $("#protocol-uuid-remove-confirmation-input").on("change", function () {
            var user_entry = $(this).val();
            if (user_entry == limbscad_id) {
                $("#protocol-remove-confirm-button").prop("disabled", false);
                $('#protocol-remove-confirm-button').click(function () {
                    $.ajax({
                        type: "POST",
                        url: removal_link,
                        dataType: "json",
                        success: function (data) {
                            $("#delete-protocol-event-confirm").html(data["message"]);
                            $("#protocol-uuid-remove-confirmation-input").hide();
                            $("#protocol-remove-confirm-button").hide();
/*
                            $("#delete-protocol-confirm-modal").modal({
                                show: false
                            });
*/
                            if (data["success"]) {
                                $("#row-LIMBSCAD-"+id).hide();
                                //window.location.reload()
                            } else {
                                //window.location.reload();
                                //return false
                            }
                            return data["message"]
                        }
                    });
                });
            } else {
                $("#protocol-remove-confirm-button").prop("disabled", true);
            }
        })
    });

}

function render_attr_content(label, content, actions, item_id) {
    if (content == undefined || content == "" || content == null) {
        content = "Not Available."
    }

    var row = "<tr class='rowdisp' id='row-"+ item_id+"'>";
    row += '<td width="30%" style="font-weight:bold">' + label + ':</td>'
    row += '<td>' + content + '</td>';
    row += '<td>';

    for (const i in actions) {
        var act = actions[i];
        row += "<button type='button' id="+ act +'-'+ item_id + " class='btn btn-delete-icon'>";
        //row += "<a href='#' id="+ act +'-'+ item_id + ">";
        if (act == 'del') {
            row += "<i class='fa fa-trash'></i>"
        }
        else {
            row += "<i class='fa fa-edit'>" + act + "</i>";
        }
        row += "</button>";
        //row +="</a>";
    }
    row += '</td></tr>';
    return row;
}

function fill_custom_attributes(custom_attributes) {
    var html = "";
    //html += "<thead><tr><th>Term</th><th>Value</th><th>Action</th></tr></thead>"
    html += "<tbody>";

    for (i in custom_attributes) {
        var attribute = custom_attributes[i];

        var label = attribute["attribute"]["term"];

        if (attribute["option"] == null) {
            var content = attribute["data"];
        } else {
            var content = attribute["option"]["term"];
        }

        var item_id = "LIMBSCAD-" + attribute["id"];
        html += render_attr_content(label, content, ["del"], item_id);
    }

    html += "</tbody>";
    $("#custom-attributes-table").html(html);

    // Define remove button click functions
    for (i in custom_attributes){
        var attribute = custom_attributes[i];
        var el = 'del-'+ "LIMBSCAD-" + attribute["id"];
        def_remove_attrdata(el);
    }
}


function fill_basic_information(sample_information) {
    var html = "";

    if (sample_information["base_type"] == "Fluid") {
        measurement = "mL";
        var sample_type = sample_information["sample_type_information"]["fluid_type"];
    }

    else if (sample_information["base_type"] == "Molecular") {
        measurement = "μg/mL";
        var sample_type = sample_information["sample_type_information"]["molecular_type"];

    }

    else {
        measurement = "Cells";
        var sample_type = sample_information["sample_type_information"]["cellular_type"];
    }

    html += render_content("Status", sample_information["status"]);
    html += render_content("Biobank Barcode", sample_information["barcode"]);
    html += render_content("Biohazard Level", sample_information["biohazard_level"]);
    html += render_content("Type", sample_information["base_type"]);
    html += render_content("Sample Type", sample_type);
    html += render_content("Quantity", sample_information["remaining_quantity"] + " / " + sample_information["quantity"] + " " + measurement);
    if (sample_information["storage"] != null) {
        var storage_info = ""
        //"Not Available"
        if (sample_information["storage"]["storage_type"] == "STB") {
            var rack_info = sample_information["storage"]["rack"];
            var storage_info = "<a href='"+rack_info["_links"]["self"]+"'>";
            storage_info +=  "<i class='fa fa-grip-vertical'></i> LIMBRACK-" + rack_info["id"];
            storage_info += ' | '+rack_info["serial_number"] + "</a>";

        } else if (sample_information["storage"]["storage_type"] == "STS") {
            var shelf_info = sample_information["storage"]["shelf"];
            var storage_info = "<a href='"+shelf_info["_links"]["self"]+"'>";
            storage_info +=  "<i class='fa fa fa-bars'></i> LIMBSHF-" + shelf_info["id"];
            storage_info += ' | '+shelf_info["name"] + "</a>";

        }
    }
    html += render_content("Location", storage_info);
    html += render_content("Collection site", sample_information["site_id"]);
    html += render_content("Current site", sample_information["current_site_id"]);

    $("#basic-information").html(html);

}


function fill_document_information(document_information) {
        $("#documentTable").DataTable({
            data: document_information,
            pageLength: 5,
            columns: [
                {
                    mData: {},
                    mRender: function (data, type, row) {

                        document_data = "<a href='" + data["_links"]["self"] + "'>";
                        document_data += '<i class="fas fa-file"></i> LIMBDOC-'
                        document_data += data["id"] + ": "
                        document_data += data["name"] + "</a>"
                        return document_data
                    }
                },
                {
                    mData: {},
                    mRender: function (data, type, row) {
                        return data["type"]
                    }
                }

            ]
        });



}

function fill_sample_reviews(reviews) {
    let review_events = new Map();
    for (r in reviews) {
        var review_info = reviews[r];
        // Start ul
        var event_datetime = '';
        var undertaken_by = '';
        var comments = '';
        if (review_info["event"] != null || review_info["event"] != undefined) {
            if (review_info["event"].hasOwnProperty('datetime')) {
                event_datetime = review_info["event"]["datetime"];
            }
            if (review_info["event"].hasOwnProperty('undertaken_by')) {
                undertaken_by = review_info["event"]["undertaken_by"];
            }
            if (review_info["event"].hasOwnProperty('comments')) {
                comments = review_info["event"]["comments"];
            }
        }
        html = "<li>"
        html += "<p class='text-muted'>Undertaken on " + event_datetime + "</p>"

        // Start card body
        html += "<div class='card'>"

        var header_colour = "text-white bg-warning"
        var glyphicon = "fa fa-star";

        if (review_info["result"] == "Pass") {
            var header_colour = "text-white bg-success";
            var glyphicon = "fa fa-check-circle"
        }

        else if (review_info["result"] == "Fail") {
            var header_colour = "text-white bg-danger";
            var glyphicon = "fa fa-times-circle"
        }

        html += "<div class='card-header "+header_colour+"'>"
        html += review_info["review_type"];
        html += "</div>";
        html += "<div class=' card-body'>"
        html += "<div class='media'>"
        html += "<div class='align-self-center mr-3'>"
        html += "<h1><i class='"+ glyphicon + "'></i></h1>"
        html += "</div>"
        html += "<div class='media-body'>"
        html += "<h5 class='mt-0' id='review-uuid-"+ review_info["id"] +"'>" + review_info["uuid"] + "</h5>";
        html += "<table class='table table-striped'>"
        html += render_content("Quality", review_info["quality"]);
        html += render_content("Conducted By", undertaken_by);
        html += render_content("Comments", comments);
        html += "</table>"
        html += "</div>"

        html += "</div>"
        // End card body
        html += "</div>"
        html += "<div class='card-footer'>"
        //html += "<a href='" + review_info["_links"]["edit"] + "'>"
        html += "<div class='btn btn-warning float-left disabled'>Edit</div>"
        //html += "</a>"
        html += "<div id='remove-review-"+review_info["id"] + "' class='btn btn-danger float-right'>Remove</div>"

        html += "</div>"
        html += "</div>"

        // End ul
        html += "</li>"

        review_events.set(review_info["id"].toString(), review_info);
        $("#sample-review-li").append(html);

        $("#remove-review-"+review_info["id"]).on("click", function () {
            var id = $(this).attr("id").split("-")[2];

            var uuid = $("#review-uuid-"+id).text();
            $("#delete-review-confirm-modal").modal({
                show: true
            });

            var removal_link = review_events.get(id)["_links"]["remove"];

            $("#review-uuid-remove-confirmation-input").on("change", function() {
                var user_entry = $(this).val();
                if (user_entry == uuid) {
                    $("#review-remove-confirm-button").prop("disabled", false);
                    $('#review-remove-confirm-button').click(function() {
                        //window.location.href = removal_link;
                        $.ajax({
                        type: "POST",
                        url: removal_link,
                        dataType: "json",
                        success: function (data) {
                            $("#delete-review-confirm-modal").modal({
                            show: false
                            });
                            if (data["success"]) {
                                window.location.reload();
                            } else {
                                window.location.reload();
                                //alert("We have a problem! "+data["message"]);
                                return false
                            }
                            }
                        });
                    });
                }
                else {
                    $("#review-remove-confirm-button").prop("disabled", true);

                }
            })
        });
    }
}



function fill_protocol_events(events) {

    let protocol_events = new Map();


    for (e in events) {
        var event_info = events[e];
        var event_datetime = '';
        var undertaken_by = '';
        var comments = '';
        var reduced_quantity = '';

        if (event_info["reduced_quantity"] != null)
            reduced_quantity = event_info["reduced_quantity"] + " " + measurement;

        //console.log("event_info", event_info);
        if (event_info["event"] != null || event_info["event"] != undefined) {
            if (event_info["event"].hasOwnProperty('datetime')) {
                event_datetime = event_info["event"]["datetime"];
            }
            if (event_info["event"].hasOwnProperty('undertaken_by')) {
                undertaken_by = event_info["event"]["undertaken_by"];
            }
            if (event_info["event"].hasOwnProperty('comments')) {
                comments = event_info["event"]["comments"];
            }
        }
        // Start ul
        html = "<li>"
        html += "<p class='text-muted'>Undertaken on " + event_datetime + "</p>"
        // Start card body
        html += "<div class='card'>"
        html += "<div class='card-header'>"
        html += event_info["protocol"]["type"];
        html += "</div>";
        html += "<div class=' card-body'>"
        html += "<div class='media'>"
        html += "<div class='align-self-center mr-3'>"
        html += "<h1><i class='fa fa-project-diagram'></i></h1>"
        html += "</div>"
        html += "<div class='media-body'>"
        html += "<h5 class='mt-0' id='protocol-uuid-" + event_info["id"] +"'>" + event_info["uuid"] + "</h5>";
        html += "<a href='"+ event_info["protocol"]["_links"]["self"] +"'>"
        html += "<h6 class='mt-0'>LIMBPRO-" + event_info["protocol"]["id"] + ": " + event_info["protocol"]["name"] + "</h6>";
        html += "</a>"
        if (event_info["parent"] != null) {
            var parent_html = "<h6 > On parent sample :";
            parent_html += '<a href="' + event_info["parent"]["_links"]["self"] + '">'
            parent_html += '<i class="fas fa-vial"></i> ';
            parent_html += event_info["parent"]["uuid"]
            parent_html += '</a></h6>'
            html += parent_html;
        }

        html += "<table class='table table-striped'>"
        html += render_content("Sample Qty Reduction", reduced_quantity);
        html += render_content("Undertaken By", undertaken_by);
        html += render_content("Comments", comments);
        html += "</table>"
        html += "</div>"


        html += "</div>"
        // End card body
        html += "</div>"
        html += "<div class='card-footer'>"
        html += "<a href='" + event_info["_links"]["edit"] + "'>"
        html += "<div id='edit-protocol-"+event_info["id"] +"-"+event_info["is_locked"] + "' class='btn btn-warning float-left'>Edit</div>"
        html += "</a>"
        if (!["Sample Transfer", "Sample Destruction"].includes(event_info["protocol"]["type"]) ) {
        html += "<div id='remove-protocol-"+event_info["id"] +"-"+event_info["is_locked"] + "' class='btn btn-danger float-right'>Remove</div>"
        html += "</div>"
        }
        html += "</div>"

        // End ul
        html += "</li>"

        protocol_events.set(event_info["id"].toString(), event_info);
        $("#protocol-event-li").append(html);

        $("#remove-protocol-"+event_info["id"]+'-'+event_info["is_locked"]).on("click", function () {
            var id = $(this).attr("id").split("-")[2];
            var locked = $(this).attr("id").split("-")[3];
            
            var uuid = $("#protocol-uuid-"+id).text();
            var warning_msg = "<B>Warning:</B> This action cannot be undone!";
            if (locked == 'true') {
                warning_msg += "<br> <B>!!! This protocol event created sample(s), removing it will delete the sample(s) it created as well!!!</B>" ;
            }
            $("#delete-protocol-warning").html(warning_msg)
            $("#delete-protocol-event-confirm").html("Please enter the Protocol Event UUID to confirm that you want to remove this Event:")
            $("#protocol-uuid-remove-confirmation-input").val("").attr("placeholder", "Type Protocol Event UUID here").show();
            $("#protocol-remove-confirm-button").show();
            $("#delete-protocol-confirm-modal").modal({
                show: true
            });

            var removal_link = protocol_events.get(id)["_links"]["remove"];

            $("#protocol-uuid-remove-confirmation-input").on("change", function() {
                var user_entry = $(this).val();
                if (user_entry == uuid) {
                    $("#protocol-remove-confirm-button").prop("disabled", false);
                    $('#protocol-remove-confirm-button').click(function() {
                        // window.location.href = removal_link;
                        $.ajax({
                        type: "POST",
                        url: removal_link,
                        dataType: "json",
                        success: function (data) {
                            $("#delete-protocol-confirm-modal").modal({
                            show: false
                            });

                            if (data["success"]) {
                                if (locked == 'true') {
                                    window.location.assign(window.location.origin + "/sample");
                                } else {
                                    window.location.reload();
                                }
                            } else {
                                window.location.reload();
                                //alert("We have a problem! "+data["message"]);
                                return false
                            }
                            }
                        });
                    });
                } 
                else {
                    $("#protocol-remove-confirm-button").prop("disabled", true);

                }
            })
        });
    }
}


function fill_lineage_table(subsamples) {

    let table = $('#subSampleTable').DataTable({
        data: subsamples,
        dom: 'Blfrtip',
        buttons: ['print', 'csv', 'colvis',
            //'selectAll',
            {text: 'Select All', action: function () {
                table.rows( {search:'applied'} ).select();
            }},
            {text: 'Not Stored', action: function () {
                table.rows('.not-stored').select();
            }},
        'selectNone'
        ],
        lengthMenu: [ [5, 10, 25, 50, -1], [5, 10, 25, 50, "All"] ],
        //pageLength: 5,

        columnDefs: [
            {targets: '_all', defaultContent: ''},
            {targets: [2, 3, 4], visible: false, "defaultContent": ""},
            {
                targets:  -1,
                 orderable: false,
                 className: 'select-checkbox',
            }

        ],
        order: [[1, 'desc']],
        select: {'style': 'multi',
                'selector': 'td:last-child'},

       'createdRow': function( row, data, dataIndex ) {
            if ( data["storage"] == null ) {
              $(row).addClass( 'not-stored' );
            }
        },

        columns: [

            {
                "mData": {},
                "mRender": function (data, type, row) {
                    var col_data = '';
                    col_data += render_colour(data["colour"])
                    col_data += "<a href='" + data["_links"]["self"] + "'>";
                    col_data += '<i class="fas fa-vial"></i> '
                    col_data += data["uuid"];
                    col_data += "</a>";
                    if (data["source"] != "New") {

                        col_data += '</br><small class="text-muted"><i class="fa fa-directions"></i> ';
                        col_data += '<a href="' + data["parent"]["_links"]["self"] + '">'
                        col_data += '<i class="fas fa-vial"></i> ';
                        col_data += data["parent"]["uuid"],
                            col_data += "</a></small>";
                    }

                    return col_data
                }
            },
            {data: "id"},
            {data: "barcode"},
            {data: "status"},

            {data: "base_type"},
            {
                "mData": {},
                "mRender": function (data, type, row) {
                    var sample_type_information = data["sample_type_information"];

                    if (data["base_type"] == "Fluid") {
                        return sample_type_information["fluid_type"];
                    } else if (data["base_type"] == "Cell") {
                        return sample_type_information["cellular_type"] + " > " + sample_type_information["tissue_type"];
                    } else if (data["base_type"] == "Molecular") {
                        return sample_type_information["molecular_type"];
                    }

                }
            },
            {
                "mData": {},
                "mRender": function (data, type, row) {
                    var sample_type_information = data["sample_type_information"];

                    if (sample_type_information["cellular_container"] == null) {
                        return sample_type_information["fluid_container"];
                    } else {
                        return sample_type_information["cellular_container"];
                    }

                }
            },
            {
                "mData": {},
                "mRender": function (data, type, row) {
                    var percentage = data["remaining_quantity"] / data["quantity"] * 100 + "%"
                    var col_data = '';
                    col_data += '<span data-toggle="tooltip" data-placement="top" title="' + percentage + ' Available">';
                    col_data += data["remaining_quantity"] + "/" + data["quantity"] + get_metric(data["base_type"]);
                    col_data += '</span>';
                    return col_data
                }
            },
            {
                "mData": {},
                "mRender": function (data, type, row) {
                    var storage_data = data["storage"];

                    if (storage_data == null) {
                        return "<span class='text-muted'>Not stored.</span>"
                    } else if (storage_data["storage_type"] == "STB") {
                        var rack_info = storage_data["rack"];
                        var html = "<a href='" + rack_info["_links"]["self"] + "'>";
                        html += "<i class='fa fa-grip-vertical'></i> LIMBRACK-" + rack_info["id"];
                        html += "</a>"
                        return html
                    } else if (storage_data["storage_type"] == "STS") {
                        var shelf_info = storage_data["shelf"];
                        var html = "<a href='" + shelf_info["_links"]["self"] + "'>";
                        html += "<i class='fa fa-bars'></i> LIMBSHF-" + shelf_info["id"];
                        html += "</a>"
                        return html
                    }
                    return data["storage"]
                }
            },

            {
                "mData": {},
                "mRender": function (data, type, row) {
                    return data["created_on"];
                }
            },

            {} //checkbox select column

        ],

    });


    $("#subsample-to-cart-btn").click(function (event) {
        var rows_selected = table.rows( { selected: true } ).data();

        if (rows_selected.length>0) {
           var formdata = [];
           $.each(rows_selected, function (index, row) {
               delete row['__proto__'];
               formdata.push(row)
           });
           var api_url = window.location.origin+ "/sample/to_cart";
           res = add_samples_to_cart(api_url, formdata);
           if (res.success == true) {
               table.rows({selected: true}).deselect();
           }

        } else {
            alert("No sample selected!")
        }

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
        }
    }
    );
}

function deactivate_nav() {
    $("#basic-info-nav").removeClass("active");
    $("#protocol-events-nav").removeClass("active");
    $("#associated-documents-nav").removeClass("active");
    $("#sample-review-nav").removeClass("active");
    $("#lineage-nav").removeClass("active");
    $("#custom-attr-nav").removeClass("active");
}

function hide_all() {
    var time = 50;
    $("#basic-info").fadeOut(50);
    $("#protocol-event-info").fadeOut(50);
    $("#associated-documents").fadeOut(50);
    $("#lineage-info").fadeOut(50);
    $("#sample-review-info").fadeOut(50);
    $("#custom-attributes-div").fadeOut(50);
}

function lock_action() {
    $("#action-dispose").hide();
    $("#action-review").hide();
    $("#action-protocol-event").hide();
    $("#action-aliquot").hide();
    $("#action-derive").hide();
}

function qty_zero_action() {
    $("#action-aliquot").hide();
    $("#action-protocol-event").hide();
    $("#action-derive").hide();
}


$(document).ready(function () {
    $('#myTable').DataTable();

    var measurement = "";
    //var versionNo = $.fn.dataTable.version;
    //alert(versionNo);
    var sample_info = get_sample();
    if (sample_info["success"] == false) {
        $("#screen").fadeOut();
        $("#error").delay(500).fadeIn();
    }

    else {
        var sample_info = sample_info["content"];
        $("#loading-screen").fadeOut();
        get_barcode(sample_info, "qrcode");
    
        fill_title(sample_info);
        fill_basic_information(sample_info);
        fill_custom_attributes(sample_info["attributes"]);
        fill_quantity_chart(sample_info["base_type"], sample_info["quantity"], sample_info["remaining_quantity"]);
        fill_consent_information(sample_info["consent_information"]);
        fill_lineage_table(sample_info["subsamples"]);
        fill_comments(sample_info["comments"]);
        fill_document_information(sample_info["documents"]);
        if (sample_info["subsample_event"]!=undefined && sample_info["subsample_event"]!=null) {
            sample_info["subsample_event"]["parent"] = sample_info["parent"];
            sample_info["events"].unshift(sample_info["subsample_event"])
        }
        fill_protocol_events(sample_info["events"]);
        fill_sample_reviews(sample_info["reviews"]);
        //console.log('sample_info', sample_info)
        const intransit = ["Transferred", "Pending Collection"]
        if (sample_info["is_locked"]==true || intransit.includes(sample_info["status"])) {
            lock_action()
        }
        if (sample_info["remaining_quantity"]==0 )
            qty_zero_action()

        $("#content").delay(500).fadeIn();
    
    
        $("#qrcode").click(function () {
            get_barcode(sample_info, "qrcode");
    
        });
    
        $("#datamatrix").click(function () {
            get_barcode(sample_info, "datamatrix");
    
        });
    
        $("#print-label-btn").click(function () {
            window.location.href = sample_info["_links"]["label"]
        });
    
        $("#add-cart-btn").click(function() {
            var msg = "Adding a sample to cart will remove it from storage, press OK to proceed!";
            if (confirm(msg)) {
                $.ajax({
                    type: "POST",
                    url: sample_info["_links"]["add_sample_to_cart"],
                    dataType: "json",
           'success': function (data) {
               json = data;
               $("#cart-confirmation-msg").html(data["message"]);
               $("#cart-confirmation-modal").modal({
                   show: true
               });
               },
           'failure': function (data) {
               json = data;
               $("#cart-confirmation-msg").html(data["message"]);
               $("#cart-confirmation-modal").modal({
                   show: true
               });
               }
                });
            } else {
                return false;
            }
        })

        $("#shallow-remove").on("click", function () {

            var uuid = sample_info["uuid"];
            var warning_msg = "<B>Warning:</B> This action cannot be undone!";
            warning_msg += "<br> <B>Shallow remove only removes a single sample without any sub- or parent samples associated. !!</B>" ;
            $("#delete-protocol-warning").html(warning_msg)
            $("#delete-protocol-confirm-modal-title").html("Confirm Sample Removal")
            $("#delete-protocol-event-confirm").html("Please enter the Sample UUID to confirm that you want to remove this Sample!")
            $("#delete-protocol-confirm-modal").modal({
                show: true
            });

            var removal_link = sample_info["_links"]["self"]+"/remove";
            $("#protocol-uuid-remove-confirmation-input").on("change", function() {
                var user_entry = $(this).val();
                if (user_entry == uuid) {
                    $("#protocol-remove-confirm-button").prop("disabled", false);
                    $('#protocol-remove-confirm-button').click(function() {
                        // window.location.href = removal_link;
                        $.ajax({
                        type: "POST",
                        url: removal_link,
                        dataType: "json",
                        success: function (data) {
                            $("#delete-protocol-confirm-modal").modal({
                            show: false
                            });
                            if (data["success"]) {
                                //window.location.reload();
                                window.location.assign(window.location.origin + "/sample");
                            } else {
                                window.location.reload();
                                //alert("We have a problem! "+data["message"]);
                                return false
                            }
                            }
                        });
                    });
                }
                else {
                    $("#protocol-remove-confirm-button").prop("disabled", true);

                }
            })
        });

        $("#deep-remove").on("click", function () {
            var uuid = sample_info["uuid"];
            var warning_msg = "<B>Warning:</B> This action cannot be undone!";
            warning_msg += "<br> <B>Deep remove will delete the sample and its sub-samples and associated data. !!</B>" ;
            $("#delete-protocol-warning").html(warning_msg)
            $("#delete-protocol-confirm-modal-title").html("Confirm Sample Removal")
            $("#delete-protocol-event-confirm").html("Please enter the Sample UUID to confirm that you want to remove this Sample!")
            $("#delete-protocol-confirm-modal").modal({
                show: true
            });

            var removal_link = sample_info["_links"]["self"]+"/deep_remove";
            $("#protocol-uuid-remove-confirmation-input").on("change", function() {
                var user_entry = $(this).val();
                if (user_entry == uuid) {
                    $("#protocol-remove-confirm-button").prop("disabled", false);
                    $('#protocol-remove-confirm-button').click(function() {
                        // window.location.href = removal_link;
                        $.ajax({
                        type: "POST",
                        url: removal_link,
                        dataType: "json",
                        success: function (data) {
                            $("#delete-protocol-confirm-modal").modal({
                            show: false
                            });
                            if (data["success"]) {
                                //window.location.reload();
                                window.location.assign(window.location.origin + "/sample");
                            } else {
                                window.location.reload();
                                //alert("We have a problem! "+data["message"]);
                                //return false;
                            }
                            }
                        });
                    });
                }
                else {
                    $("#protocol-remove-confirm-button").prop("disabled", true);

                }
            })
        });

        $("#basic-info-nav").on("click", function () {
            deactivate_nav();
            $(this).addClass("active");
            hide_all();
            $("#basic-info").fadeIn(100);
        });
    
        $("#custom-attr-nav").on("click", function() {
            deactivate_nav();
            $(this).addClass("active");
            hide_all();
            $("#custom-attributes-div").fadeIn(100);
        });
    
        $("#protocol-events-nav").on("click", function () {
            deactivate_nav();
            $(this).addClass("active");
            hide_all();
            $("#protocol-event-info").fadeIn(100);
        });
    
        $("#sample-review-nav").on("click", function() {
            deactivate_nav();
            $(this).addClass("active");
            hide_all();
            $("#sample-review-info").fadeIn(100);
    
        });
    
        $("#associated-documents-nav").on("click", function () {
            deactivate_nav();
            $(this).addClass("active");
            hide_all();
            $("#associated-documents").fadeIn(100);
        });
    
        $("#lineage-nav").on("click", function () {
            deactivate_nav();
            $(this).addClass("active");
            hide_all();
            $("#lineage-info").fadeIn(100);
        });
    }

    
});