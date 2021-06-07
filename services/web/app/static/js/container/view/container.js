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
    html = ""

    console.log(container)
    html += render_content("Name", container["container"]["name"]);
    html += render_content("Manufacturer", container["container"]["manufacturer"]);

    html += render_content("Description", container["container"]["description"]);
    html += render_content("Temperature (C)", container["container"]["temperature"]);

    $("#container-information").html(html);

}

$(document).ready(function () {
    var container = get_container();

    $("#name").html(container["container"]["name"])
    fill_content(container);
});