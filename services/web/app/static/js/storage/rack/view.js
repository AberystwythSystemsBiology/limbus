function get_rack_information() {
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


function render_subtitle(rack_information) {
    $("#createdOn").html(rack_information["created_on"]);
    $("#createdBy").html(rack_information["author"]["first_name"] + " " + rack_information["author"]["last_name"] );

}

function render_empty(row_id, rc, count, assign_sample_url) {

    assign_sample_url = assign_sample_url.replace("rph", rc[0]);
    assign_sample_url = assign_sample_url.replace("cph", rc[1]);
    var content = '<div class="col" id="tube_'+ rc.join("_") + '">'
    content += '<div class="square align-middle">'
    content += '<div class="align-middle">'
    content += count
    content += "</div></div></div>"
    $("#"+ row_id).append(content)

    $( "#tube_"+ rc.join("_")) .click( function() {

        window.location = assign_sample_url;
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
              data: [counts["full"],  counts["empty"]]
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



function render_view(view, assign_sample_url) {
    var count = 0;

    for (r in view) {
        var row_id = "row_"+ r
        $("#view_area").append('<div id="' + row_id +'" class="row no-gutters"></div>');
        var row = view[r]
        for (c in row) {
            count += 1
            var column = row[c];
            if (column["empty"]) {
                render_empty(row_id, c.split("\t"), count, assign_sample_url);
            }
            else {

            }
        }
    }


}

$(document).ready(function() {
    var rack_information = get_rack_information();

    console.log(rack_information);

    render_subtitle(rack_information);
    render_view(rack_information["view"], rack_information["_links"]["assign_sample"]);
    render_occupancy_chart(rack_information["counts"])
});