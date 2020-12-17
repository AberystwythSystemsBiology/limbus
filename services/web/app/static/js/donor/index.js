function get_donors(query) {
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


function render_table(query) {
    var d = get_donors(query);
    $("#table_view").delay(300).fadeOut();
    $("#loading").fadeIn();



    $('#donor-table').DataTable({
        data: d,
        dom: 'Bfrtip',
        buttons: ['print', 'csv', 'colvis'],
        columnDefs: [

        ],
        columns: [
            {
                "mData": {},
                "mRender": function (data, type, row) {
                    var col_data = '';
                    col_data += render_colour(data["colour"])
                    col_data += "<a href='" + data["_links"]["self"] + "'>";
                    col_data += '<i class="fas fa-vial"></i> LIMBDON-'
                    col_data += data["id"];
                    col_data += "</a>";


                    return col_data
                }
            },

            {
                "mData": {},
                "mRender": function (data, type, row) {
                    // Age
                    return data["dob"];


                }
            },
            {
                "mData": {},
                "mRender": function (data, type, row) {
                    // Sex
                    return data["sex"];
                }
            },
            {
                "mData": {},
                "mRender": function (data, type, row) {
                    // Status
                    return data["status"]
                }
            },
            {
                "mData": {},
                "mRender": function (data, type, row) {
                    // Createi
                    console.log(data);
                    return data["created_on"]
                },
            }



        ],

    });

    $("#loading").fadeOut();
    $("#table_view").delay(300).fadeIn();


}


function get_filters() {
    var filters = {

    }

    var f = ["sex", "status", "race"];

    $.each(f, function (_, filter) {
        var value = $("#" + filter).val();
        if (value && value != "None") {
            filters[filter] = value;
        }
    });

    return filters;


}


$(document).ready(function () {

    render_table({});

    $("#reset").click(function () {

        $('#donor-table').DataTable().destroy()
        render_table({});
    });

    $("#filter").click(function () {
        $("#table_view").fadeOut();
        $('#donor-table').DataTable().destroy()
        var filters = get_filters();
        render_table(filters);
    });


});