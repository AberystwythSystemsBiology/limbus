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

                    console.log(sample_type_information)

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
        
        console.log(value)

        html += media_html;
    });

    if (html == "" ) {
        html += "<h2>No diagnosis information found.</h2>"
    }

    $("#diagnosis-div").html(html);
    
 }


$(document).ready(function () {

    var donor_information = get_donor();


    render_sample_table(donor_information["samples"]);

    render_window_title("LIMBDON-" + donor_information["id"]);

    $("#donor-id").html(donor_information["id"]);


    $("#edit-donor-btn").on("click", function() {
        window.location.href = donor_information["_links"]["edit"];
    });


    $("#assign-diagnosis-btn").on("click", function() {
        window.location.href = donor_information["_links"]["assign_diagnosis"];
    });

    $("#assign-sample-btn").on("click", function() {
        window.location.href = donor_information["_links"]["associate_sample"]
    });

    var arr = render_dob(donor_information["dob"])

    var dob = arr[0];
    var age = arr[1];
    var date = arr[2];

    fill_basic_information(donor_information, age, dob)
    fill_diagnosis_information(donor_information["diagnoses"], date);

    $("#diagnosis-nav").on("click", function() {
        deactivate_nav();
        $(this).addClass("active");
        hide_all();
        $("#diagnosis-div").fadeIn(1000);
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