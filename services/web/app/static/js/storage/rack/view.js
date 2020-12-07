function get_rack_information() {
    var api_url = encodeURI(window.location + '/endpoint');

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


function render_subtitle(rack_information) {
    $("#colour").html(render_colour(rack_information["colour"]))
    $("#createdOn").html(rack_information["created_on"]);
    $("#createdBy").html(rack_information["author"]["first_name"] + " " + rack_information["author"]["last_name"]);
    var shelf_information = rack_information["shelf"];

    if (shelf_information != null) {
        var shelf_html = "<a href='" + shelf_information["_links"]["self"] + "'>"
        shelf_html += "<i class='fa fa-bars'></i> LIMBSHF-" + shelf_information["id"]
        shelf_html += "</a>"
        $("#sh").html(shelf_html);
    }

    else {
    }


}

function render_empty(row_id, rc, count, assign_sample_url) {

    assign_sample_url = assign_sample_url.replace("rph", rc[0]);
    assign_sample_url = assign_sample_url.replace("cph", rc[1]);
    var content = '<div class="col" id="tube_' + rc.join("_") + '">'
    content += '<div class="square tube">'
    content += '<div class="align-middle">'
    content += count
    content += "</div></div></div>"
    $("#" + row_id).append(content)

    $("#tube_" + rc.join("_")).click(function () {
        window.location = assign_sample_url;
    });
}

function render_modal(sample_info) {
    $("#sampleName").html(render_colour(sample_info["colour"]) + sample_info["uuid"])

    var html = render_content("Biobank Barcode", sample_info["biobank_barcode"]);
    html += render_content("Sample Type", sample_info["type"]);
    html += render_content("Collection Site", sample_info["collection_information"]["collection_site"]);
    html += render_content("Sample Source", sample_info["source"]);
    html += render_content("Created On", sample_info["created_on"]);

    $("#sample_barcode").html("<img class='margin: 0 auto 0;' src='" + sample_info["_links"]["qr_code"] + "'>")

    $("#sample_view_btn").click( function() {
        window.location.href = sample_info["_links"]["self"];
    })

    $("#sampleModalInformation").html(html);

}

function render_full(info, row_id, rc, count, assign_sample_url) {
    var sample_info = info["sample"]
    var content = '<div class="col" id="tube_' + rc.join("_") + '">'
    content += '<div class="square tube"><div class="align_middle present-tube">'
    content += '<img width="100%" src="' + sample_info["_links"]["qr_code"] + '">'
    content += "</div></div></div>"
    $("#" + row_id).append(content)


    $("#tube_" + rc.join("_")).click(function () {
        //window.location = sample_info["_links"]["self"];
        render_modal(sample_info);
        $("#sampleInfoModal").modal();
    });
}

function render_occupancy_chart(counts) {
    new Chart(document.getElementById("status_chart"), {
        type: 'doughnut',
        data: {
            labels: ["Occupied", "Empty"],
            datasets: [
                {
                    backgroundColor: ["#28a745", "#dc3545"],
                    data: [counts["full"], counts["empty"]]
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

function render_sample_table(samples) {


    if (samples.length > 0) {
        
        $('#sampleTable').DataTable( {
            data: samples,
            dom: 'Bfrtip',
            buttons: [ 'print', 'csv', 'colvis' ],
            columnDefs: [],
            columns: [
                {
                    "mData": {},
                    "mRender": function(data, type,row) {
                        return data["pos"][0] + "x" + data["pos"][1]
                    },
                    "width": "3%"
                },
             {
                    "mData": {},
                    "mRender": function (data, type, row) {
                        var col_data = '';
                        col_data += render_colour(data["sample"]["colour"])
                        col_data += "<a href='"+data["sample"]["_links"]["self"]+ "'>";
                        col_data += '<i class="fas fa-vial"></i> '
                        col_data += data["sample"]["uuid"];
                        col_data += "</a>";
                        if (data["sample"]["source"] != "New") {
    
                        col_data += '</br><small class="text-muted"><i class="fa fa-directions"></i> ';
                        col_data += '<a href="'+data["sample"]["parent"]["_links"]["self"]+'" target="_blank">'
                        col_data += '<i class="fas fa-vial"></i> ';
                        col_data += data["sample"]["parent"]["uuid"],
                        col_data += "</a></small>";
                    }
    
                        return col_data
                    }
                },
                
                {
                    "mData" : {},
                    "mRender": function (data, type, row) {
                        var sample_type_information = data["sample"]["sample_type_information"];
                        
        
                        if (data["sample"]["type"] == "Fluid") {
                            return sample_type_information["flui_type"];
                        }
                        else if (data["sample"]["type"] == "Cell") {
                            return sample_type_information["cell_type"] + " > " + sample_type_information["tiss_type"];
                        }
                        
        
                    }
                },
                {
                    "mData": {},
                    "mRender": function (data, type, row) {
                        var col_data = data["sample"]["collection_information"]["datetime"]
                        return col_data;
                    }
                },
                {
                    "mData": {},
                    "mRender": function (data, type, row) {
                        var percentage = data["sample"]["remaining_quantity"] / data["sample"]["quantity"] * 100 + "%"
                        var col_data = '';
                        col_data += '<span data-toggle="tooltip" data-placement="top" title="'+percentage+' Available">';
                        col_data += data["sample"]["remaining_quantity"]+"/"+data["sample"]["quantity"]+get_metric(data["sample"]["type"]); 
                        col_data += '</span>';
                        return col_data
                    }
            }
    
            
    
            ],
            
        });
    }


    else {
        $("#sample-table-div").hide();
    }
}

function render_information(rack_information) {
    var html = render_content("UUID", rack_information["uuid"]);
    html += render_content("Serial Number", rack_information["serial_number"]);
    html +=  render_content("Description", rack_information["description"])

    $("#rack-information").html(html);

    $("#row").html(rack_information["num_rows"]);
    $("#col").html(rack_information["num_cols"]);
}

function render_view(view, assign_sample_url) {
    var count = 0;

    var samples = [];

    for (r in view) {
        var row_id = "row_" + r
        $("#view_area").append('<div id="' + row_id + '" class="row no-gutters"></div>');
        var row = view[r]
        for (c in row) {
            count += 1
            var column = row[c];
            if (column["empty"]) {
                render_empty(row_id, c.split("\t"), count, assign_sample_url);
            }
            else {
                render_full(column, row_id, c.split("\t"), count, assign_sample_url);
                column["pos"] = c.split("\t");
                samples.push(column)

            }
        }
    }

    return samples;

}

$(document).ready(function () {
    collapse_sidebar();

    var rack_information = get_rack_information();

    render_subtitle(rack_information);
    render_information(rack_information);
    var samples = render_view(rack_information["view"], rack_information["_links"]["assign_sample"]);
    render_occupancy_chart(rack_information["counts"])
    render_sample_table(samples);
    $("#loading-screen").fadeOut();
    $("#content").delay(500).fadeIn();


});