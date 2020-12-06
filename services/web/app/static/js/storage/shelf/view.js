function get_shelf_information() {
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

function render_subtitle(shelf_information) {
    $("#created-on").html(shelf_information["created_on"]);
    $("#created-by").html(shelf_information["author"]["first_name"] + " " + shelf_information["author"]["last_name"]);
    $("#storage-id").html(shelf_information["storage_id"]);
    $("#edit-details-btn").click(function() {
        window.location.href = shelf_information["_links"]["edit"];
    });

    $("#add-sample-btn").click(function() {
        window.location.href = shelf_information["_links"]["assign_sample_to_shelf"];
    });

    $("#add-rack-btn").click(function() {
        window.location.href = shelf_information["_links"]["assign_rack_to_shelf"];
    })

}

function render_information(shelf_information) {
    var html = render_content("UUID", shelf_information["uuid"]);
    html += render_content("Name", shelf_information["name"]);
    html += render_content("Description", shelf_information["description"]);
    $("#shelf-information").html(html);
}

function render_sample_table(samples) { 
    
}

function render_rack_table(racks) {
    if (racks.length > 0) {
        
        $('#rack-table').DataTable( {
            data: racks,
            dom: 'Bfrtip',
            buttons: [ 'print', 'csv', 'colvis' ],
            columnDefs: [
                { targets: -3,
                visible:false}, { targets: -2, visible: false}
            ],
            columns: [
                {
                    "mData": {},
                    "mRender": function(data, type,row) {
                        var render_html = "<a href='" + data["_links"]["self"] + "'>"
                        render_html += render_colour(data["colour"]) + "LIMBRACK-" + data["id"];
                        render_html += "</a>"
                        return render_html
                    }
                },
                {
                    "mData": {},
                    "mRender": function(data, type,row) {
                        return data["serial_number"];
                    }
                },
                {
                    "mData": {},
                    "mRender": function(data, type,row) {
                        return data["sample_count"] + " / " + data["num_rows"]*data["num_cols"]; 
                    }
                },
             {
                    "mData": {},
                    "mRender": function (data, type, row) {
                        return data["uuid"];
                    }
                },
                
                {
                    "mData" : {},
                    "mRender": function (data, type, row) {
                        return data["author"]["first_name"] + " " + data["author"]["last_name"]
                
                    }
                },
                {
                    "mData": {},
                    "mRender": function (data, type, row) {
                        return data["created_on"]
                    }
                },            
    
            ],
            
        });
    }
    else {
        $("#sample-rack-div").hide();
    }
}

function render_sample_table(samples) {
    if (samples.length > 0) {
        
        console.log(samples);

        $('#sample-table').DataTable( {
            data: samples,
            dom: 'Bfrtip',
            buttons: [ 'print', 'csv', 'colvis' ],
            columnDefs: [],
            columns: [
                {
                    "mData": {},
                    "mRender": function(data, type,row) {
                        var render_html = "<a href='" + data["_links"]["self"] + "'>"
                        render_html += render_colour(data["colour"]) + data["uuid"];
                        render_html += "</a>"
                        return render_html
                    }
                },
                {
                    "mData": {},
                    "mRender": function(data, type,row) {
                        return data["type"];
                    }
                },
                {
                    "mData": {},
                    "mRender": function(data, type,row) {
                        return data["source"]; 
                    }
                },
             {
                    "mData": {},
                    "mRender": function (data, type, row) {
                        return data["remaining_quantity"] + " / " + data["quantity"];
                    }
                },
               
    
            ],
            
        });
    }
    else {
        $("#sample-div").hide();
    }
}



$(document).ready(function () {
    var shelf_information = get_shelf_information();
    render_subtitle(shelf_information);
    render_information(shelf_information);
    render_rack_table(shelf_information["racks"]);
    render_sample_table(shelf_information["samples"]);
    $("#loading-screen").fadeOut();
    $("#content").delay(500).fadeIn();

});