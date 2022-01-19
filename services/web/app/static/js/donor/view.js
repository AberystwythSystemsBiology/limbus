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


function fill_sample_table(samples) {

    let table = $('#donor-samples-table').DataTable({
        data: samples,
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
            {targets: [2, 3, 6], visible: false, "defaultContent": ""},
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
                        col_data += '<a href="' + data["parent"]["_links"]["self"] + '" target="_blank">'
                        col_data += '<i class="fas fa-vial"></i> ';
                        col_data += data["parent"]["uuid"],
                            col_data += "</a></small>";
                    }

                    return col_data
                }
            },
            {data: "id"},
            {data: "barcode"},
            { // Consent ID
                "mData": {},
                "mRender": function (data, type, row) {
                    var consent = data['consent_information'];
                    return 'LIMBDC-' + consent['id'];
                }
            },
            { // Consent status
                "mData": {},
                "mRender": function (data, type, row) {
                    var consent = data['consent_information'];
                    var consent_status = 'Active';
                    if (consent['withdrawn'] == true) {
                        consent_status = 'Withdrawn';
                    }
                    return consent_status;
                }
            },

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

    $("#samples-to-cart-btn").click(function (event) {
        var rows_selected = table.rows( { selected: true } ).data();

        if (rows_selected.length>0) {
           var formdata = [];
           $.each(rows_selected, function (index, row) {
               delete row['__proto__'];
               formdata.push(row)
           });

           var api_url = window.location.origin+ "/sample/to_cart";
           res = add_samples_to_cart(api_url, formdata);
           //var api_url = window.location.origin+ "/sample/shipment/cart"
           //window.open(api_url, "_blank");
           //window.open(api_url"_self");
           if (res.success == true) {
               table.rows({selected: true}).deselect();
           }

        } else {
            alert("No sample selected!")
        }

    });

}


function render_dob(dob) { 
    var date = new Date(Date.parse(dob));
    const month = date.toLocaleString('default', { month: 'long' });
    return [month + " " + date.getFullYear(), calculate_age(date.getMonth(), date.getFullYear()), date];
}

function render_action_links(self_link) {
    $("#action-new-consent").attr("href", self_link+"/new/consent")
    $("#action-withdraw-consent").attr("href", self_link+"/withdraw/consent")
}

function fill_basic_information(donor_information, age, dob) {

    html = render_content("Date of Birth", dob);
    html += render_content("Age", age)
    if (donor_information["height"] != null)
        html += render_content("Height", donor_information["height"]+" cm");
    if (donor_information["weight"] != null)
    html += render_content("Weight", donor_information["weight"]+" kg");
    if (donor_information["sex"] != null)
    html += render_content("Biological Sex", donor_information["sex"])

    if (donor_information["height"] != null && donor_information["weight"] != null)
        html += render_content("Body Mass Index", calculate_bmi(donor_information["height"], donor_information["weight"]));
    html += render_content("Race", donor_information["race"]);
    html += render_content("Status", donor_information["status"]);

    if (donor_information["status"] == "Deceased") {
        html += render_content("Date of Death", donor_information["death_date"]);
    }

    $("#basic-information-table").html(html);

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


function fill_diagnosis_information(diagnoses, date) {

    //html = ""
    let diag = new Map();
    $.each(diagnoses, function(index, value){
        console.log('value', value)
        html = ""
        html += "<div class='card' style='border: 2px solid darkgrey ;'>"
        // Start card body
        html += "<div class='card-body'>"

        var media_html = "<div class='jumbotron media' style='padding:1em;'><div class='align-self-center mr-3'><h1><i class='fa fa-stethoscope'></i></h1></div>" +
            "<div class='media-body'>"
        var refs = "";
        for (const [code, url] of Object.entries(value["doid_ref"]["references"])) {
          refs += "<a href="+url+">"+ code + "</a>, ";
        }
        media_html += "<h2>"
        media_html += "<a href=" + value['doid_ref']['iri'] +">"
        media_html += value["doid_ref"]["label"]
        media_html += "</a>"
        media_html +=' <span id="doid-label" class="btn-sm btn-danger label label-default pull-right">'
        media_html += value["doid_ref"]["name"]
        media_html += "</span></h2>";


        media_html += "<table class='table table-striped'>";
        media_html += render_content("Description", value["doid_ref"]["description"]);
        media_html += render_content("References", refs);
        media_html += render_content("Stage", value["stage"]);
        media_html += render_content("Comments", value["comments"]);
        media_html += render_content("Date of Diagnosis", value["diagnosis_date"]);
        media_html += "</table>"
        media_html += "</div></div>"

        html += media_html;
        // end card body
        html += "<div id='remove-diagnosis-" + value["id"] + "' class='btn btn-danger float-right'>Remove</div>"

        html += "</div>"
        html += "</div>"
        // End ul
        //html += "</li>"
        diag.set(value["id"].toString(), value);

        $("#diagnosis-div").append(html);

    $("#remove-diagnosis-" + value["id"]).on("click", function () {
            var id = $(this).attr("id").split("-")[2];
            var warning_msg = "Press confirm to delete diagnosis!";
            $("#delete-protocol-warning").html(warning_msg)
            $("#delete-protocol-confirm-modal-title").html("Confirm Donor Diagnosis Removal")
            $("#delete-protocol-event-confirm").html("")
            $("#protocol-id-remove-confirmation-input").hide()

            $("#delete-protocol-confirm-modal").modal({
                show: true
            });

            var removal_link = window.location.origin + "/donor/LIMBDIAG-" + id +"/remove";
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
       });
     });

    if (html == "" ) {
        html += "<h2>No diagnosis information found.</h2>"
    }
}

function fill_consent_information(consent_information) {

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
    var donor_id = consent_information["donor_id"];
    donor_link = ""
    if (donor_id != null) {
        donor_link += "<a href=" + window.location.origin + "/donor/LIMBDON-" + donor_id + ">";
        donor_link += "LIMBDON-" + donor_id + "</a>";
        $("#donor_id").html(donor_link);
    } else {
        $("#donor_id").text(donor_link);
    }
    $("#consent_date").html(consent_information["date"]);
    $("#consent_status").html(consent_status);
    $("#withdrawal_date").html(consent_information["withdrawal_date"]);

    $('#print-consent').on('click', function () {
      var header = "Digital Consent Form: "+"LIMBDC-"+consent_information["id"];
      console.log('header', header)
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

function fill_consents_information(consent_information) {
    let consents = new Map();
    for (e in consent_information) {
        var consent_info = consent_information[e];

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
        html += "<div id='view-consent-" + consent_info["id"] + "' class='btn btn-secondary float-left'>View</div>"
        html += "<a href='" + consent_info["_links"]["edit"] + "'>";
        html += "<button class='btn btn-secondary'>Edit</button>";
        html += "</a>";
        html += "<div id='remove-consent-" + consent_info["id"] + "' class='btn btn-delete float-right'>Remove</div>"
        html += "</div>"
        html += "</div>"

        consents.set(consent_info["id"].toString(), consent_info);

        // End ul
        html += "</li>"
        $("#consent-li").append(html);

        $("#view-consent-" + consent_info["id"]).on("click", function () {
            var id = $(this).attr("id").split("-")[2];
            fill_consent_information(consents.get(id));
            $("#consentModal").modal('show');
        });

        if (consent_info['withdrawn']==true || consent_information["is_Locked"]==true) {
            $("#remove-consent-" + consent_info["id"]).hide();
        }

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
    var consents = {};

    console.log("donor_info", donor_information)
    //render_sample_table(donor_information["samples"]);
    fill_sample_table(donor_information["samples"]);

    render_window_title("LIMBDON-" + donor_information["id"]);

    $("#donor-id").html(donor_information["id"]);

    render_action_links(donor_information["_links"]["self"])

    $("#edit-donor-btn").on("click", function() {
        window.location.href = donor_information["_links"]["edit"];
    });

    $("#remove-donor-btn").on("click", function() {
        //window.location.href = donor_information["_links"]["remove"];
            var warning_msg = "<B>Warning:</B> This action cannot be undone!";
            warning_msg += "<br> <B>Shallow remove only removes a bare donor without any consents/diagnosis/samples associated. !!</B>" ;
            $("#delete-protocol-warning").html(warning_msg)
            $("#delete-protocol-confirm-modal-title").html("Confirm Donor Removal")
            $("#delete-protocol-event-confirm").html("Please enter the Donor ID LIMBDON-XXX to confirm that you want to remove this donor!")
            $("#delete-protocol-confirm-modal").modal({
                show: true
            });

            var removal_link = donor_information["_links"]["self"]+"/remove";
                            var limbdon_id = "LIMBDON-"+ $("#donor-id").text();

            $("#protocol-id-remove-confirmation-input").on("change", function() {
                var user_entry = $(this).val();

                if (user_entry == limbdon_id) {
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
                                window.location.assign(window.location.origin + "/donor");
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


    $("#deep-remove-donor-btn").on("click", function() {
        //window.location.href = donor_information["_links"]["self"]+"/deep_remove";
            var warning_msg = "<B>Warning:</B> This action cannot be undone!";
            warning_msg += "<br> <B>Deep remove removes the donor and all is associated samples and events (consents/diagnosis/samples/...).!!</B>" ;
            $("#delete-protocol-warning").html(warning_msg)
            $("#delete-protocol-confirm-modal-title").html("Confirm Donor Deep Removal")
            $("#delete-protocol-event-confirm").html("Please enter the Donor ID LIMBDON-XXX to confirm that you want to remove this donor and all associated samples and events!")
            $("#delete-protocol-confirm-modal").modal({
                show: true
            });

            var removal_link = donor_information["_links"]["self"]+"/deep_remove";
            var limbdon_id = "LIMBDON-"+ $("#donor-id").text();

            $("#protocol-id-remove-confirmation-input").on("change", function() {
                var user_entry = $(this).val();

                console.log("removal_link", removal_link)

                if (user_entry == limbdon_id) {
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
                                window.location.assign(window.location.origin + "/donor");
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

    $("#assign-diagnosis-btn").on("click", function() {
        window.location.href = donor_information["_links"]["assign_diagnosis"];
    });

    $("#new-sample-btn").on("click", function() {
        window.location.href = donor_information["_links"]["new_sample"]
        //window.open(donor_information["_links"]["new_sample"], "_blank");
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