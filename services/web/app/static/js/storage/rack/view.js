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

function render_full(info, row_id, rc, count, assign_sample_url) {
    var sample_info = info["sample"]
    var content = '<div class="col" id="tube_' + rc.join("_") + '">'
    content += '<div class="square tube"><div class="align_middle present-tube">'
    content += '<img width="100%" src="' + sample_info["_links"]["qr_code"] + '">'
    content += "</div></div></div>"
    $("#" + row_id).append(content)


    $("#tube_" + rc.join("_")).click(function () {
        window.location = sample_info["_links"]["self"];
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



function render_information(rack_information) {
    console.log(rack_information);
    $("#rack_information").append(render_content("UUID", rack_information["uuid"]));
    $("#rack_information").append(render_content("Serial Number", rack_information["serial_number"]));
    $("#rack_information").append(render_content("Description", rack_information["description"]));

    $("#row").html(rack_information["num_rows"]);
    $("#col").html(rack_information["num_cols"]);
}

function render_view(view, assign_sample_url) {
    var count = 0;

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
            }
        }
    }


}

$(document).ready(function () {
    collapse_sidebar();

    var rack_information = get_rack_information();

    render_subtitle(rack_information);
    render_information(rack_information);
    render_view(rack_information["view"], rack_information["_links"]["assign_sample"]);
    render_occupancy_chart(rack_information["counts"])
    $("#loading-screen").fadeOut();
    $("#content").delay(500).fadeIn();


});