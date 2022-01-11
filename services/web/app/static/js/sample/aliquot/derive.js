/*
Copyright (C) 2021 C Lu <culATaberDOTacDOTuk>

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

function get_types(typename, api_url='') {
    if (api_url=='') {
        api_url = encodeURI(window.location.origin);
        if (typename == "sampletotypes")
            api_url = api_url + "/" + ['sample', typename].join('/');
        else
            api_url = api_url + "/" + ['api', 'sample', typename].join('/');
    }
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

    return json["content"];}


function get_sample() {
    var current_url = encodeURI(window.location);
    var split_url = current_url.split("/");
    split_url.pop()
    var api_url = split_url.join("/") + "/data"

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

function check_barcode_form() {
    var present_barcodes = []
    var fail = false;

    $(".barcode").each(function() {
        var barcode = $(this).val();
        if (barcode != "") {
            if(jQuery.inArray(barcode, present_barcodes) != -1) {
                fail = true;
            }
            present_barcodes.push(barcode);
        }
        
    });

    return fail;
}

function remove_whitespace(v) { 
    return v.replace(/\s/g,'');

}

function check_barcode_database(entered_barcode) {

    var json = (function () {
        var json = null;
        $.post({
            'async': false,
            'global': false,
            'url': sample["_links"]["webapp_query"],
            'contentType': 'application/json',
            'data': JSON.stringify({barcode: entered_barcode}),
            'success': function (data) {
                json = data;
            }
        });
        return json;
    })();

    

    if (json["content"].length > 0) {
        return true
    }
    return false;
    
}


// Global

var sample = get_sample();
var samplebasetypes = get_types("samplebasetypes");
var containerbasetypes = get_types("containerbasetypes");
var sampletypes = get_types("sampletypes");
var containertypes = get_types("containertypes");
process_sample_container_type();

function process_sample_container_type() {
    // augment sample container types with existing hot sampletotype in the database
    if (!("sampletotype" in sessionStorage)) {
        var sampletotype = get_types("sampletotypes");
        sessionStorage.removeItem("sampletotype");
        sessionStorage.setItem("sampletotype", JSON.stringify(sampletotype));
    } else {
        var sampletotype = JSON.parse(sessionStorage.getItem("sampletotype"));
    }

    for (let key in containertypes) {
        try {
            let containertype_list = containertypes[key]["container"];
            let choice1 = sampletotype["container_choices"][key]["container"];
            containertypes[key]["container"] = choice1.concat(containertype_list);
        } catch (e) {};
    }

    for (let key in sampletypes) {
        try {
            let sampletype_list = sampletypes[key]["sample_type"];
            let choice1 = sampletotype["sampletype_choices"][key];
            sampletypes[key]["sample_type"] = choice1.concat(sampletype_list);
        } catch (e) {};
    }

    // set fixation_type default to NULL
    for (let key in containertypes) {
        let fixationtype_list = containertypes[key]["fixation_type"];
        fixationtype_list.unshift([null, "-- Select FixationType --"]);
    }

}


var derived_sample_counts = 0;
var indexes = [];
var lastvals={};

function update_graph() {
    var remaining_quantity = $("#remaining_quantity").val();
    var quantity = $("#original_quantity").val();
    var metric = $("#original_metric").html();

    $("#chart-div").empty();
    $("#chart-div").html('<canvas id="quantity-chart" width="100%" height="100%"></canvas>');

    new Chart(document.getElementById("quantity-chart"), {
        type: 'doughnut',
        data: {
            labels: ["Remaining " + metric, "Used " + metric],
            datasets: [
                {
                    backgroundColor: ["#28a745", "#dc3545"],
                    data: [remaining_quantity, quantity-remaining_quantity ]
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

function fill_sample_info() {
    $("#uuid").html(sample["uuid"]);
    $("#sample_href").attr("href", sample["_links"]["self"])
    $("#remaining_quantity").attr("value", parseFloat(sample["remaining_quantity"]));
    $("#original_quantity").attr("value", parseFloat(sample["quantity"]));
    $("#remaining_metric").html(get_metric(sample["base_type"]));
    $("#original_metric").html(get_metric(sample["base_type"]));

    if (sample["base_type"] == "Cell") {
        $("#fixation_type_th").show()
    }

}



function subtract_quantity() {
    var remaining_quantity = sample["remaining_quantity"].toFixed(4);

    $("#remove_zero_switch").hide();
    $("#submit").hide();

    if (derived_sample_counts>0) {
        var quantities = remaining_quantity;
        $("#submit").show();
        $("#remove_zero_switch").show();
    } else {
        var quantities = 0;
    };

    $('input[type="number"].aliquotted-quantity').each(function () {
        quantities += parseFloat($(this).val());
    });

    $("#remaining_quantity").attr("value",
        parseFloat(((remaining_quantity - quantities).toFixed(4)).toString() ));
    update_graph();

}

function update_number() {
    derived_sample_counts = $("#derived_sample_table > tbody > div.card").length;
    $("#total_derivatives").html(derived_sample_counts);
}

function select_html_type(indx, type="", type_list=[], select_val=null) {
    if (select_val==null) select_val = type_list[0][0];
    var select_html = '<select class="form-control" data-live-search=true id="'+type+'_select_'+indx+'" >';
    for (i in type_list) {
        if (type_list[i][0] == select_val) {
            //set the default value based on the values in the last selection
            select_html += '<option value="' + type_list[i][0] + '" selected>' + type_list[i][1] + '</option>'
        } else {
            select_html += '<option value="' + type_list[i][0] + '">' + type_list[i][1] + '</option>'
        }
    }

    // End html
    select_html += '</select>';
    return select_html;
};

function generate_samplebasetype_select(indx) {
    var samplebasetype_list = samplebasetypes;
    var lastsel = samplebasetype_list[0][0] // Container code for last selection
    if (derived_sample_counts>0 && indx > 1) {
        lastsel = lastvals["sample_basetype"];
    }

    select_html = 'BaseType ';
    select_html += select_html_type(indx, "samplebasetype", type_list=samplebasetype_list, select_val=lastsel);
    return select_html;
}


function generate_sampletype_select(indx) {
    var sbt = samplebasetypes[0][0];
    //var sampletype_list = sampletypes[sbt]["sample_type"];
    var sampletype_list = get_sampletype_list(sbt);
    var lastsel = sampletype_list[0][0] // Container code for last selection
    if (derived_sample_counts>0 && indx > 1) {
        sbt = lastvals["sample_basetype"];
        sampletype_list = sampletypes[sbt]["sample_type"];
        lastsel = lastvals["sample_type"];
    }
    select_html = ""; // "Sample Type"
    select_html += select_html_type(indx, "sampletype", type_list=sampletype_list, select_val=lastsel);
    return select_html;
}

function generate_containerbasetype_select(indx) {
    var containerbasetype_list = containerbasetypes;
    // var lastsel = containerbasetype_list[0][0]; // Container code for last selection
    var lastsel = containerbasetype_list[1][0]; ; //Default to long term preservation
    if (derived_sample_counts>0 && indx > 1) {
        lastsel = lastvals["container_basetype"];
    }

    select_html = 'BaseType ';
    select_html += select_html_type(indx, "containerbasetype", type_list=containerbasetype_list, select_val=lastsel);
    return select_html;
}

function generate_container_select(indx) {
    var cbt = containerbasetypes[1][0]; //"PRM"
    var containertype_list = containertypes[cbt]["container"];
    var lastsel = containertype_list[0][0]; // Container code for last selection
    if (derived_sample_counts>0 && indx > 1) {
        cbt = lastvals["container_basetype"];
        containertype_list = containertypes[cbt]["container"];
        lastsel = lastvals["container_type"];
    }

    select_html = ""; //"Container Type"
    select_html += select_html_type(indx, "containertype", type_list=containertype_list, select_val=lastsel);
    return select_html;
}


function generate_fixation_select(indx) {
    var cbt = containerbasetypes[0][0]; //"PRM"
    var fixation_list = containertypes[cbt]["fixation_type"];
    var lastsel = fixation_list[0][0]; // Container code for last selection
    if (derived_sample_counts>0 && indx > 1) {
        cbt = lastvals["container_basetype"];
        fixation_list = containertypes[cbt]["fixation_type"];
        lastsel = lastvals["fixation_type"];
    }

    select_html = select_html_type(indx, "fixationtype", type_list=fixation_list, select_val=lastsel);
    return select_html;
}

// Dealing with blood sample subtypes
function get_sampletype_list(sbt){
    var sampletype_list = sampletypes[sbt]["sample_type"];
    if (sbt == 'FLU') {
        if (sample["sample_type_information"]["fluid_type"] == "Blood (whole)") {
            sampletype_list = sampletypes[sbt]["blood_subtype"];
        }
    }
    return sampletype_list;
}

function make_new_form(indx) {
    var row_form_html = '';
    var lastval = 0.01;
    if (derived_sample_counts>0 && indx > 1) {
        lastval = lastvals["volume"];
    }

    // Start Card
    row_form_html += '<div class="card" id="card_'+indx+'" style="background-color:aliceblue ">'

    // basetypes + volume/barcode/action
    row_form_html += '<div class="row" id="row_'+indx+'" >';
        row_form_html += '<div class="col-3">'+generate_samplebasetype_select(indx)+'</div>'
        row_form_html += '<div class="col-4">'+generate_containerbasetype_select(indx)+'</div>'
        row_form_html += '<div class="col-2"> Volume'
            row_form_html += '<input id="volume_'+indx+'" type="number" class="form-control derived-quantity" step="0.05" min="0.01" value="'+lastval+'">'
        row_form_html += '</div>'
        row_form_html += '<div class="col-2"> Barcode'
            row_form_html += '<input id="barcode_'+indx+'" type="text" class="form-control barcode" placeholder="Sample Barcode">'
        row_form_html += '</div>'
        row_form_html += '<div id="trash_'+indx+'" class="btn btn-danger windows" style="margin-top: 18px;"><i class="fa fa-trash"></i></div>';
    row_form_html += '</div>'
    // sample type + container type / fixation type
    row_form_html += '<div class="row" id="rowa_'+indx+'">';
        row_form_html += '<div class="col-3" id="sampletype_div_'+indx+'">'+generate_sampletype_select(indx)+'</div>';
        row_form_html += '<div class="col-4" id="container_div_'+indx+'">'+generate_container_select(indx)+'</div>';
        row_form_html += '<div class="col-3" id="fixationtype_div_'+indx+'" '+'>'+generate_fixation_select(indx)+'</div>';
        row_form_html += '<div class="col-2"></div>';
    row_form_html += '</div>';
    // End Card
    row_form_html += '</div>';

    $("#derived_sample_table > tbody:last-child").append(row_form_html);
    if ($("#samplebasetype_select_"+indx).val()=='CEL') {
        $("#fixationtype_div_" + indx).show();
    } else {
        $("#fixationtype_div_" + indx).hide();
    };

    update_number();
    subtract_quantity();
    indexes.push(indx);

    $("#samplebasetype_select_"+indx).change(function(){
        var sbt = $("#samplebasetype_select_"+indx).val();
        //var sampletype_list = sampletypes[sbt]["sample_type"];
        var sampletype_list = get_sampletype_list(sbt);
        var options = ""; //<option>--Select--</option>";
        $("#sampletype_select_"+indx).empty();
        $(sampletype_list).each(function(index, value){
            options += '<option value="'+value[0]+'">'+value[1]+'</option>';
        });
        $("#sampletype_select_"+indx).html(options);

        if (sbt=='CEL') {
            $("#fixationtype_div_"+indx).show();
        } else {
            $("#fixationtype_div_"+indx).hide();
        }
        lastvals["sample_basetype"] = $("#samplebasetype_select_"+indx).val();
    });

    $("#sampletype_select_"+indx).change(function() {
        lastvals["sample_type"] = $("#sampletype_select_"+indx).val();
    })

    $("#containerbasetype_select_"+indx).change(function() {
        var cbt = $("#containerbasetype_select_"+indx).val();
        var containertype_list = containertypes[cbt]["container"];
        var options = "";
        $("#containertype_select_"+indx).empty();
        $(containertype_list).each(function(index, value){
            options += '<option value="'+value[0]+'">'+value[1]+'</option>';
        });
        $("#containertype_select_"+indx).html(options);

        var fixationtype_list = containertypes[cbt]["fixation_type"];
        var options = "";
        $("#fixationtype_select_"+indx).empty();
        $(fixationtype_list).each(function(index, value){
            options += '<option value="'+value[0]+'">'+value[1]+'</option>';
        });
        $("#fixationtype_select_"+indx).html(options);

        lastvals["container_basetype"] = $("#containerbasetype_select_"+indx).val();
    });

    $("#containertype_select_"+indx).change(function() {
        lastvals["container_type"] = $("#containertype_select_"+indx).val();
    })
    $("#fixationntype_select_"+indx).change(function() {
        lastvals["fixation_type"] = $("#fixationtype_select_"+indx).val();
    })
    $("#volume_" + indx).on("change", function(){
        lastvals["volume"] = $("#volume_"+indx).val();
    })

    lastvals = {sample_basetype: $("#samplebasetype_select_"+ indx).val(),
                sample_type: $("#sampletype_select_"+ indx).val(),
                container_basetype: $("#containerbasetype_select_"+indx).val(),
                container_type: $("#containertye_select_" + indx).val(),
                volume: $("#volume_" + indx).val()
    }

    // Because Windows is trash.
    $(".windows").click(function() {
        var to_remove = $(this).attr("id").split("_")[1];

        $("#card_" + to_remove).remove();
        update_number();
        subtract_quantity();
    });


    $(".derived-quantity").change(function() {
        subtract_quantity();
    });

    $('#derived-quantity').on('change keyup', function() {
        // Remove invalid characters
        var sanitized = $(this).val().replace(/[^0-9]/g, '');
        // Update value
        $(this).val(sanitized);
        lastvals["volume"] = sanitized;
    });


    $(".barcode").change(function() {
        $(this).val(remove_whitespace($(this).val()));
        // If the barcode is in the database
        
        if ($(this).val() != "") {
            if (check_barcode_database($(this).val()) == true ) {
                $("#submit").attr("disabled", true);
                $("#database_error").show();
                $(window).scrollTop(0);
            }
            else {
                $("#submit").attr("disabled", false);
                $("#database_error").hide();

            }
        }

        if (check_barcode_form() == true) {
            $("#submit").attr("disabled", true);
            $("#duplicate_barcode").show();
            $(window).scrollTop(0);
        }

        else {
            $("#submit").attr("disabled", false);
            $("#duplicate_barcode").hide();
        }

    });

}


function prepare_data() {

    var derivatives = [];

/*    $("tr.item").each(function() {
        var quantity1 = $(this).find("input.name").val(),
            quantity2 = $(this).find("input.id").val();
    });*/

    indexes.forEach(function(i) {
        if ($("#sampletype_select_"+i).length && $("#containertype_select_"+i).length) {
            var derivative = {
                sample_base_type: $("#samplebasetype_select_"+ i).val(),
                sample_type: $("#sampletype_select_"+ i).val(),
                container_base_type: $("#containerbasetype_select_"+i).val(),
                container_type: $("#containertype_select_" + i).val(),
                volume: $("#volume_" + i).val(),
                barcode: $("#barcode_" + i).val()

            }
            //if ($("samplebasetype_select_"+ i).val() == "Cell") {
            if ($("samplebasetype_select_"+ i).val() == "CEL") {
                derivative["fixation_type"] = $("#fixationtype_select_" + i).val()
            }

            if (derivative["volume"] > 0) {
                derivatives.push(derivative);
            }
        }

    });

    var data = {
        parent_id: sample["id"],
        processing_protocol: $("#processing_protocol").val(),
        processing_date: $("#processing_date").val(),
        processing_time: $("#processing_time").val(),
        processing_comments: $("#processing_comments").val(),
        processed_by: $("#processed_by").val(),
        derivation_protocol: $("#derivation_protocol").val(),
        derivation_date: $("#derivation_date").val(),
        derivation_time: $("#derivation_time").val(),
        derivation_comments: $("#derivation_comments").val(),
        derived_by: $("#derived_by").val(),
        remove_zero_parent_on: $("#remove_zero_on").prop('checked'),
        derivatives: derivatives

    }

    return data

    
}

function post_data(data) {
    var json = (function () {
        var json = null;
        $.post({
            'async': false,
            'global': false,
            'url': sample["_links"]["webapp_derive"],
            'contentType': 'application/json',
            'data': JSON.stringify(data),
            'success': function (data) {
                json = data;
                window.location.href = json["content"]["_links"]["self"];
                
            },
            'error': function (data) {
                $("#error_code").html(data.status);
                $("#derivative_error").show();
            }
        });
        return json;
    })();
}

$(document).ready(function () {
    fill_sample_info();
    subtract_quantity();
    //update_graph();
    if (sample["remaining_quantity"]<=0) {
        $("#submit").hide();
        alert("Sample remaining quantity is 0!");
        window.location.assign(sample["_links"]["self"]);
    }

    $("#processing_protocol").change(function(){
        var processing_protocol = $("#processing_protocol").val()
        if (processing_protocol==0) {
            $("#processing_date").val("");
            $("#processing_time").val("");
            $("#processed_by").val("");
        } else {
            $("#derivation_date").val(processing_date);
        }
    })

    $("#processing_date").change(function(){
        var processing_date = $("#processing_date").val();
        if (processing_date != "")
            $("#derivation_date").val(processing_date);
    })
    $("#processing_time").change(function(){
        var processing_time = $("#processing_time").val();
        if (processing_time != "")
            $("#derivation_time").val(processing_time);
    })
    $("#processed_by").change(function(){
        var processed_by = $("#processed_by").val();
        if (processed_by != "")
            $("#derived_by").val(processed_by);
    })


    var indx = 0;
    $("[name=new]").click(function(){
        indx += 1;
        make_new_form(indx);
    });


    $("#submit").click(function() {
        var data = prepare_data();
        $('#confirmationModal').modal("toggle");

        $("#modalSubmit").click(function() {
            post_data(data);
        });

    });



});
