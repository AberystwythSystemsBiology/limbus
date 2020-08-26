function get_samples(query) {
    var current_url = encodeURI(window.location);
    var split_url = current_url.split("/");
    split_url.pop()
    var api_url = split_url.join("/") + "/query"
    
    var json = (function () {
        var json = null;
        $.post({
            'async': false,
            'global': false,
            'url': api_url,
            'contentType': 'application/json',
            'data': JSON.stringify(query),
            'success': function (data) {
                json = data;
            }
        });
        return json;
    })();
    
    

    return json["content"];
}

function render_colour(colour) {
    if (colour == "Blue") {
        var colour_class = "bg-primary";
    }
    else if (colour == "Red") {
        var colour_class = "bg-danger";
    }
    else if (colour == "Green") {
        var colour_class = "bg-success";
    }
    else if (colour == "Yellow") {
        var colour_class= "bg-warning";
    }

    var colour_html = '<span class="colour-circle '+colour_class+'"></span>';
    
    return colour_html;

}

function render_table(query) {
    var d = get_samples(query);
    $("#table_view").delay(300).fadeOut();
    $("#loading").fadeIn();


    $('#sampleTable').DataTable( {
        data: d,
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

    $("#loading").fadeOut();
    $("#table_view").delay(300).fadeIn();


}


function get_filters() {
    var filters = {

    }

    var f = ["barcode", "type", "colour", "source"];

    $.each(f, function(_, filter) {
        var value = $("#"+filter).val();
        if (value && value != "None") {
            filters[filter] = value;
        }
    });

    return filters;


}

$(document).ready(function() {

    render_table({});
    
    $("#reset").click(function() {
        
        $('#sampleTable').DataTable().destroy()
        render_table({});
    });

    $("#filter").click(function() {
        $("#table_view").fadeOut();
        $('#sampleTable').DataTable().destroy()
        var filters = get_filters();
        render_table(filters);
    });

});