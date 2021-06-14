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

function get_container() {
    var current_url = encodeURI(window.location);
    var split_url = current_url.split("/");
    var api_url = split_url.join("/") + "/data"

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

function fill_content(container) {
    html = render_content("Name", container["container"]["name"]);
    html += render_content("Manufacturer", container["container"]["manufacturer"]);
    html += render_content("Description", container["container"]["description"]);
    html += render_content("Temperature (°C)", container["container"]["temperature"]);
    html += render_content("Used For", container["container"]["used_for"]);

    $("#container-information").html(html);

}

function fill_suitability(container) {
    // Fluid, Cellular, Tissue, Sample Rack

    let attrs_map = new Map();

    attrs_map.set("fluid", {
        "canonical": "Fluids",
        "glyphicon": "<i class='fa fa-water'></i>"
    })

    attrs_map.set("cellular", {
        "canonical": "Cells",
        "glyphicon": "<i class='fa fa-egg'></i>"
    })

    attrs_map.set("tissue", {
        "canonical": "Tissue",
        "glyphicon": "<i class='fab fa-envira'></i>"
    })

    attrs_map.set("sample_rack", {
        "canonical": "Sample Rack",
        "glyphicon": "<i class='fa fa-grip-vertical'></i>"
    })

    var attrs = Array.from(attrs_map.keys());

    console.log(attrs);

    var html = "";

    for (i in attrs) {
        var b = container[attrs[i]];
        if (b == true) {
            html += '<div class="col-sm-3 text-center"><div class="card"><div class="card-header bg-success text-white">'
            var data = attrs_map.get(attrs[i]);
            html += "<h2>" + data["glyphicon"] + "</h2>";
            html += "<h4>" + data["canonical"] + "</h4>";
            html += '</div></div></div>'
        }
        else {
            html += '<div class="col-sm-3 text-center"><div class="card"><div class="card-header bg-danger text-white">'
            var data = attrs_map.get(attrs[i]);
            html += "<h2>" + data["glyphicon"] + "</h2>";
            html += "<h4>" + data["canonical"] + "</h4>";
            html += '</div></div></div>'
        }
    }

    $("#suitability").html(html);

}

$(document).ready(function () {
    var container = get_container();
    $("#name").html(container["container"]["name"]);
    $("#created-on").html(container["created_on"]);
    $("#author").html(render_author(container["author"]));

    fill_content(container);
    fill_suitability(container);

    $("#edit-btn").click(function () {
        window.location.href = container["_links"]["edit"];
    })
});