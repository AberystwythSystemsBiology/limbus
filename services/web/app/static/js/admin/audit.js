/*
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

function get_audit(query) {
    var api_url = encodeURI(window.origin);
    api_url = api_url+"/admin/audit/query";
    
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


function render_audit_table(trails, div_id) {
    $('#auditTable tfoot th').each(function() {
        var title = $(this).text();
        $(this).html('<input type="text" placeholder="Search ' + title + '" />');
    });

    var aTable = $('#' + div_id).DataTable({
        data: trails,
        dom: 'Blfrtip',
        buttons: [ 'print', 'csv', 'colvis',
             {
                extend: 'excel',
                messageTop: 'The information in this table is copyright to Sirius Cybernetics Corp.'
            }
        ],
        lengthMenu: [ [5, 10, 25, 50, -1], [5, 10, 25, 50, "All"] ],
        //pageLength: 50,
        columnDefs: [
            {targets: '_all', defaultContent: '-'},
            { targets: [6], visible: false, "defaultContent": ""},
        ],
        order: [[1, 'desc']],
        columns: [

            {data: "updated_on"},
            {data: "transaction_id"},
            {data: "end_transaction_id"},

            { // operator
                "mData": {},
                "mRender": function (data, type, row) {
                    if (data["operation_type"] == 0) {
                        try {
                            var name = [data["author"]["first_name"], data["author"]["last_name"]].join(" ");
                            return "["+data["author"]["id"]+"] " + data["author"]["email"] + ": " + name;
                        } catch {
                            return "";
                        }
                    } else {
                        try {
                            var name = [data["editor"]["first_name"], data["editor"]["last_name"]].join(" ");
                            return "["+data["editor"]["id"]+"] " + data["editor"]["email"] + ": " + name;
                        } catch {
                            if (data["operation_type"] == undefined) {
                                try {
                                    var name = [data["author"]["first_name"], data["author"]["last_name"]].join(" ");
                                    return "["+data["author"]["id"]+"] " + data["author"]["email"] + ": " + name;
                                } catch {
                                    return "";
                                }
                            }
                            return "";
                        }
                    };
                }
            },

            { // operation_type
                "mData": {},
                "mRender": function(data, type, row) {

                    if ("operation_type" in data) {
                        switch(data["operation_type"]) {
                            case 0:
                                return "Insert";
                            case 1:
                                return "Update";
                            case 2:
                                return "Delete";
                        };

                    } else {
                        return "";
                    }
                }
            },

            {data: "object"},
            {data: "id"},
            {data: "uuid"},
            // {data: "content"},
            { // content
                "mData": {},
                "mRender": function(data, type, row) {
                   const tranCols =["created_on", "author", "author_id", "updated_on", "editor", "editor_id",
                       "operation_type", "transaction_id", "end_transaction_id", "object", "uuid", "id"];
                   tmp = JSON.parse(JSON.stringify(data));
                   for (k in tmp) {
                       if (tranCols.includes(k))
                           delete tmp[k];
                   };
                   const res = JSON.stringify(tmp);
                   return res;
                }
            },

        ],

    });

     aTable.columns().every( function() {
        var that = this;
        $('input', this.footer()).on('keyup change', function() {
            if (that.search() !== this.value) {
                that
                    .search(this.value)
                    .draw();
            }
        });
    });

}


function fill_title(title){
    $("#report_type").html(title["report_type"]);
    $("#report_start_date").html(title["report_start_date"]);
    $("#report_end_date").html(title["report_end_date"]);
    //$("#report_objects").html(title["report_objects"].join(", "));
    $("#report_objects").html(JSON.stringify(title["report_object_counts"]));
    $("#report_user").html(title["report_user"]);
    $("#report_created_by").html(title["report_created_by"]);
    $("#report_created_on").html(title["report_created_on"]);
}


function render_table(query) {

    var res = get_audit(query);
    $("#table_view").delay(300).fadeOut();
    $("#loading").fadeIn();

    fill_title(res["title"]);
    render_audit_table(res["data"], "auditTable");

    $("#loading").fadeOut();
    $("#table_view").delay(300).fadeIn();

}


function get_filters() {
    var filters = {};

    var f = ["start_date", "end_date",
        "audit_type", "sample_object", "donor_object", "template_object",
        "auth_object", "storage_object", //"site_id",
        "user_id", "uuid"];

    $.each(f, function(_, filter) {
        var value = $("#"+filter).val();
        if (typeof(value) == 'object') {
            if (value.length>0) {
                filters[filter] = value.join();
            }
        } else {
            if (value && value != "None") {
                filters[filter] = value;
            }
        }
    });

    return filters;

}

function hide_all_select() {
    $("#general_object_div").hide();
    $("#sample_object_div").hide();
    $("#donor_object_div").hide();
    $("#template_object_div").hide();
    $("#auth_object_div").hide();
    $("#storage_object_div").hide();
}

function audit_object_select() {

    $("#audit_type").change(function() {
        var audit_type = $(this).val();

        if  (audit_type == "GEN") {
                hide_all_select();
                $("#general_object_div").show();
            }
        else if (audit_type == "SMP") {
                hide_all_select();
                $('#sample_object_div').show();
            }
        else if (audit_type == "DNR") {
                hide_all_select();
                $("#donor_object_div").show();
            }
        else if (audit_type == "SOP") {
                hide_all_select();
                $("#template_object_div").show();
            }
        else if (audit_type == "LTS") {
                hide_all_select();
                $("#storage_object_div").show();
            }
        else if (audit_type == "AUT") {
                hide_all_select();
                $("#auth_object_div").show();
            }
        else {
                hide_all_select();
                $("#general_object_div").show();
            }
    });
}


$(document).ready(function() {
    hide_all_select();
    $("#general_object_div").show();

    var filters = get_filters();
    render_table(filters);
    audit_object_select();

    $("#reset").click(function() {
        $('#auditTable').DataTable().destroy();
        window.location.reload();
    })

    $("#filter").click(function() {
        $("#table_view").fadeOut();
        $('#auditTable').DataTable().destroy();
        var filters = get_filters();
        //console.log("filters: ", filters);
        render_table(filters);
    });


});