/*
Copyright (C) 2021 Keiron O'Shea <keo7@aber.ac.uk>

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

function get_containers(endpoint) {
    var current_url = encodeURI(window.location);
    var split_url = current_url.split("/");
    split_url.pop()
    var api_url = split_url.join("/") + endpoint

    var json = (function () {
        var json = null;
        $.get({
            'async': false,
            'global': false,
            'url': api_url,
            'contentType': 'application/json',
            'success': function (data) {
                json = data;
            }
        });
        return json;
    })();



    return json["content"];
}




function render_check(bool) {
    if (bool == true) {
        return '<i class="fa fa-check-circle text-success"></i>'
    }
    else {
        return '<i class="fa fa-minus-circle text-danger"></i>'
    }
}

function fill_containers_table(containers) {
    $("#container-table").DataTable( {
        data: containers,
        dom: 'Bfrtip',
        buttons: [ 'print', 'csv', 'colvis' ],
        columnDefs: [
        ],
        columns: [
            {
                "mData": {},
                "mRender": function (data, type, row) {
                    var uuid = "";
                    uuid += '<a href="' + data["_links"]["self"] + '">'
                    uuid += '<i class="fa fa-dot-circle"></i> LIMBCT-';
                    uuid += data["id"];
                    uuid += ': '+ data["container"]["name"] +'</a>'
                    return uuid
                }
            },

            {
                "mData" : {},
                "mRender": function (data, type, row) {
                    return data["container"]["used_for"]
                }
            },
            {
                "mData" : {},
                "mRender": function (data, type, row) {
                    return render_check(data["tissue"])

                }
            },
            {
                "mData" : {},
                "mRender": function (data, type, row) {
                    return render_check(data["fluid"])

                }
            },
            {
                "mData" : {},
                "mRender": function (data, type, row) {
                    return render_check(data["cellular"])

                }
            },
            {
                "mData" : {},
                "mRender": function (data, type, row) {
                    return render_check(data["sample_rack"])

                }
            },
            {
                "mData" : {},
                "mRender": function (data, type, row) {
                    return data["created_on"]
                }
            },
            {
                "mData": {},
                "mRender": function (data, type, row) {
                    return render_author(data["author"])
                }
        }

        ],

    });
}

function fill_fixation_table(fixations) {
    $("#fixation-table").DataTable( {
        data: fixations,
        dom: 'Bfrtip',
        buttons: [ 'print', 'csv', 'colvis' ],
        columnDefs: [
        ],
        columns: [
            {
                "mData": {},
                "mRender": function (data, type, row) {
                    var uuid = "";
                    uuid += '<a href="' + data["_links"]["self"] + '">'
                    uuid += '<i class="fab fa-codepen"></i> LIMBFIX-';
                    uuid += data["id"];
                    uuid += ': '+ data["container"]["name"] +'</a>'
                    return uuid
                }
            },

            {
                "mData" : {},
                "mRender": function (data, type, row) {
                    return data["container"]["used_for"]
                }
            },
            {
                "mData" : {},
                "mRender": function (data, type, row) {
                    return data["created_on"]
                }
            },
            {
                "mData": {},
                "mRender": function (data, type, row) {
                    return render_author(data["author"])
                }
        }

        ],

    });
}

function deactivate_nav() {
    $("#fixation-nav").removeClass("active");
    $("#containers-nav").removeClass("active");
}



$(document).ready(function () {
    var containers = get_containers("/data/container");
    var fixations = get_containers("/data/fixation");
    fill_containers_table(containers);
    fill_fixation_table(fixations);

    $("#containers-nav").click(function() {
        deactivate_nav();
        $("#fixation").fadeOut(500);
        $("#containers").fadeIn(500);
        $(this).addClass("active");

    });

    $("#fixation-nav").click(function () {
        deactivate_nav();
        $("#containers").fadeOut(500);
        $("#fixation").fadeIn(500);
        $(this).addClass("active");

    })


});