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

function get_donor() {
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


function deactivate_nav() {
    $("#diagnosis-nav").removeClass("active");
    $("#basic-info-nav").removeClass("active");
    $("#samples-nav").removeClass("active");
}

function hide_all() {
    $("#basic-info-div").fadeOut(50);
    $("#diagnosis-div").fadeOut(50);
    $("#consent-div").fadeOut(50);
    $("#samples-div").fadeOut(50);
    
}


function calculate_bmi(height, weight) {
    var hm = height / 100

    var ini = weight / hm
    return (ini / hm).toFixed(2);
}


function render_sample_table(d) {
    $('#donor-samples-table').DataTable( {
        data: d,
        dom: 'Bfrtip',
        buttons: [ 'print', 'csv', 'colvis' ],
        columnDefs: [
            { targets: -3,
            visible:false}, { targets: -2, visible: false}
        ],
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

            {data: "base_type"},
            {
                "mData" : {},
                "mRender": function (data, type, row) {
                    var sample_type_information = data["sample_type_information"];

                    if (data["base_type"] == "Fluid") {
                        return sample_type_information["fluid_type"];
                    }
                    else if (data["base_type"] == "Cell") {
                        return sample_type_information["cellular_type"] + " > " + sample_type_information["tissue_type"];
                    }


                }
            },
            {
                "mData": {},
                "mRender": function (data, type, row) {
                    var percentage = data["remaining_quantity"] / data["quantity"] * 100 + "%"
                    var col_data = '';
                    col_data += '<span data-toggle="tooltip" data-placement="top" title="'+percentage+' Available">';
                    col_data += data["remaining_quantity"]+"/"+data["quantity"]+get_metric(data["base_type"]);
                    col_data += '</span>';
                    return col_data
                }
        }



        ],

    });
}

function render_dob(dob) { 
    var date = new Date(Date.parse(dob));
    const month = date.toLocaleString('default', { month: 'long' });
    return [month + " " + date.getFullYear(), calculate_age(date.getMonth(), date.getFullYear()), date];
}

function render_action_links(self_link) {
    $("#action-new-consent").attr("href", self_link+"/new/consent")
}

function fill_basic_information(donor_information, age, dob) {

    html = render_content("Date of Birth", dob);
    html += render_content("Age", age)
    html += render_content("Height", donor_information["height"]+"cm");
    html += render_content("Weight", donor_information["weight"]+"kg");
    html += render_content("Biological Sex", donor_information["sex"])
    html += render_content("Body Mass Index", calculate_bmi(donor_information["height"], donor_information["weight"]));
    html += render_content("Race", donor_information["race"]);
    html += render_content("Status", donor_information["status"]);

    if (donor_information["status"] == "Deceased") {
        html += render_content("Date of Death", donor_information["death_date"]);
    }

    $("#basic-information-table").html(html);

}

function fill_diagnosis_information(diagnoses, date) {

    html = ""

    $.each(diagnoses,function(index, value){
        var media_html = "<div class='jumbotron media' style='padding:1em;'><div class='align-self-center mr-3'><h1><i class='fa fa-stethoscope'></i></h1></div><div class='media-body'>"

        media_html += "<h2>"
        media_html += value["doid_ref"]["label"]
        media_html +=' <span id="doid-label" class="btn-sm btn-danger label label-default pull-right">'
        media_html += value["doid_ref"]["name"]
        media_html += "</span></h2>";
        

        media_html += "<table class='table table-striped'>";
        media_html += render_content("Description", value["doid_ref"]["description"]);
        media_html += render_content("Stage", value["stage"]);
        media_html += render_content("Comments", value["comments"]);
        media_html += render_content("Date of Diagnosis", value["diagnosis_date"]);

        media_html += "</table>"

        media_html += "</div>"

        media_html += "</div></div></div>"


        html += media_html;
    });

    if (html == "" ) {
        html += "<h2>No diagnosis information found.</h2>"
    }

    $("#diagnosis-div").html(html);
    
 }

function fill_consent_information(consent_information) {
    $("#consentModalLabel").html("Digital Consent Form: "+"LIMBDC-"+consent_information["id"])
    $("#consent_name").html(consent_information["template"]["name"]);
    $("#consent_version").html(consent_information["template"]["version"]);
    $("#consent_identifier").html(consent_information["identifier"]);
    $("#consent_comments").html(consent_information["comments"]);


    for (answer in consent_information["answers"]) {
        var answer_info = consent_information["answers"][answer];

        var answer_html = '';
        answer_html += '<li class="list-group-item flex-column align-items-start"><div class="d-flex w-100 justify-content-between"><h5 class="mb-1">Answer ';
        answer_html += + (parseInt(answer) + 1) + '<h5></div><p class="mb-1">' + answer_info["question"] + '</p></li>';

        $("#questionnaire-list").append(answer_html);
    }

    var consent_status = "Active"
    if (consent_information["withdrawn"]==true) {
        consent_status = "Withdrawn"
    }
    var donor_id = "LIMBDON-"+consent_information["donor_id"];
    donor_link = "<a href="+window.location.origin+"/donor/"+donor_id+">";
    donor_link += donor_id+"</a>";
    $("#donor_id").html(donor_link);
    $("#consent_date").html(consent_information["date"]);
    $("#consent_status").html(consent_status);
    $("#withdrawal_date").html(consent_information["withdrawal_date"]);


}

function fill_consents_information(consent_information) {
    let consents = new Map();
    for (e in consent_information) {
        var consent_info = consent_information[e];
        console.log('consent1:', consent_info);

        var consent_date = '';
        var undertaken_by = '';
        var comments = '';
        var template_name = '';
        var template_version = '';
        var consent_status = "Active";
        var withdrawal_date = '';

        if (consent_info["date"] != null || consent_info["date"] != undefined) {
            consent_date = consent_info["date"];
            undertaken_by = consent_info["undertaken_by"];
            comments = consent_info["comments"];
        }
        if (consent_info["template"] != null || consent_info["template"] != undefined) {
            template_name = consent_info["template"]["name"]
            template_version = consent_info["template"]["version"]
        }

        if (consent_info["withdrawn"] != null & consent_info["withdrawn"] == true) {
            consent_status = "Withdrawn"
            withdrawal_date = consent_info["withdrawal_date"];
            //consent_status = consent_status + " " + str(withdrawal_date)
        }

        // Start ul
        html = "<li>"
        //html += "<p class='text-muted'>Undertaken on " + event_info["event"]["datetime"] + "</p>"
        html += "<p class='text-muted'>Undertaken on " + consent_date + "</p>"

        // Start card body
        html += "<div class='card'>"
        var header_colour = "text-white bg-warning"
        var glyphicon = "fa fa-star";

        if (consent_status == "Active") {
            var header_colour = "text-white bg-success";
            var glyphicon = "fa fa-check-circle"
        } else {
            var header_colour = "text-white bg-danger";
            var glyphicon = "fa fa-times-circle"
        }
        html += "<div class='card-header "+header_colour+"'>"
        html += "Status: " + consent_status
        if (consent_status != 'Active') {
            html += " on " + withdrawal_date
        }
        html += "</div>";
        html += "<div class=' card-body'>"
        html += "<div class='media'>"
        html += "<div class='align-self-center mr-3'>"
        html += "<h1><i class='"+ glyphicon + "'></i></h1>"
        //html += "<h1><i class='fa fa-project-diagram'></i></h1>"
        html += "</div>"
        html += "<div class='media-body'>"
        html += "<h5 class='mt-0' id='consent-id-" + consent_info["id"] +"'>" + 'LIMBDC-' + consent_info["id"] + "</h5>";
        html += "<a href='"+ consent_info["template"]["_links"]["self"] +"'>"
        html += "<h6 class='mt-0'>LIMBDCF-" + consent_info["template"]["id"] + ": " + template_name + " version " + template_version + "</h6>";
        html += "</a>"
        html += "<table class='table table-striped'>"
        html += render_content("Undertaken By", undertaken_by);
        html += render_content("Comments", comments);
        html += "</table>"
        html += "</div>"


        html += "</div>"
        // End card body
        html += "</div>"
        html += "<div class='card-footer'>"
        //html += "<a href='" + consent_info["_links"]["edit"] + "'>
        //<button type="button" class="btn btn-outline-dark" data-toggle="modal" data-target="#consentModal"><i
        //                     class="fa fa-question"></i> View Consent</button>"
        //html += '<div class='btn btn-warning float-left' data-toggle='modal' data-target='#consentModal'>View</div>"
        html += "<div id='view-consent-" + consent_info["id"] + "' class='btn btn-warning float-left'>View</div>"
        //html += "</a>"

        html += "<div id='remove-consent-" + consent_info["id"] + "' class='btn btn-danger float-right'>Remove</div>"
        html += "</div>"
        html += "</div>"

        consents.set(consent_info["id"].toString(), consent_info);

        // End ul
        html += "</li>"
        $("#consent-li").append(html);

        $("#view-consent-" + consent_info["id"]).on("click", function () {
            fill_consent_information(consent_info);
            $("#consentModal").modal('show');
        });
        $("#remove-consent-" + consent_info["id"]).on("click", function () {
            var id = $(this).attr("id").split("-")[2];
            var limbdc_id = $("#consent-id-" + id).text();
            $("#delete-protocol-confirm-modal").modal({
                show: true
            });

            var removal_link = consents.get(id)["_links"]["remove"];

            $("#protocol-id-remove-confirmation-input").on("change", function () {
                var user_entry = $(this).val();
                if (user_entry == limbdc_id) {
                    $("#protocol-remove-confirm-button").prop("disabled", false);
                    $('#protocol-remove-confirm-button').click(function () {
                        // window.location.href = removal_link;
                        $("#protocol-remove-confirm-button").prop("disabled", true);

                        $.ajax({
                            type: "POST",
                            url: removal_link,
                            dataType: "json",
                            success: function (data) {
                                $("#delete-protocol-confirm-modal").modal({
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
                } else {
                    $("#protocol-remove-confirm-button").prop("disabled", true);
                }
            })
        });
    }
}



$(document).ready(function () {

    var donor_information = get_donor();

    render_sample_table(donor_information["samples"]);

    render_window_title("LIMBDON-" + donor_information["id"]);

    $("#donor-id").html(donor_information["id"]);

    render_action_links(donor_information["_links"]["self"])

    $("#edit-donor-btn").on("click", function() {
        window.location.href = donor_information["_links"]["edit"];
    });

    $("#assign-diagnosis-btn").on("click", function() {
        window.location.href = donor_information["_links"]["assign_diagnosis"];
    });

    $("#new-sample-btn").on("click", function() {
        window.location.href = donor_information["_links"]["new_sample"]
    });

    $("#assign-sample-btn").on("click", function() {
        window.location.href = donor_information["_links"]["associate_sample"]
    });

    var arr = render_dob(donor_information["dob"])

    var dob = arr[0];
    var age = arr[1];
    var date = arr[2];

    fill_basic_information(donor_information, age, dob);
    fill_diagnosis_information(donor_information["diagnoses"], date);
    fill_consents_information(donor_information["consents"]);

    $("#diagnosis-nav").on("click", function() {
        deactivate_nav();
        $(this).addClass("active");
        hide_all();
        $("#diagnosis-div").fadeIn(1000);
    });

    $("#consent-nav").on("click", function() {
        deactivate_nav();
        $(this).addClass("active");
        hide_all();
        $("#consent-div").fadeIn(1000);
    });

    $("#basic-info-nav").on("click", function() {
        deactivate_nav();
        $(this).addClass("active");
        hide_all();
        $("#basic-info-div").fadeIn(1000);

    });

    $("#samples-nav").on("click", function() {
        deactivate_nav();
        $(this).addClass("active");
        hide_all();
        $("#samples-div").fadeIn(1000);

    })
});