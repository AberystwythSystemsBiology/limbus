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


function get_shipment() {
    var current_url = encodeURI(window.location);
    var split_url = current_url.split("/");
    var api_url = split_url.join("/") + "/data"
    
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

function fill_jumbotron(shipment_data) {
    $("#created-on").html(shipment_data["created_on"]);
    $("#author").html(render_author(shipment_data["author"]));

}

function fill_table(shipment_data) {
    html = ""
    html += render_content("Date/Time", shipment_data["datetime"]);
    html += render_content("Comments", shipment_data["comments"]);
    $("#basic-information").html(html);

}


function hide_all() {
    $("#basic-info-div").fadeOut(50);
    $("#involved-samples-div").fadeOut(50);
    $("#shipment-status-div").fadeOut(50);
}


function deactivate_nav() {
    $("#basic-info-nav").removeClass("active");
    $("#involved-samples-nav").removeClass("active");
    $("#shipment-status-nav").removeClass("active");
}

function fill_involved_samples(involved_samples, new_site) {
    var html = "";
    for (i in involved_samples) {
        var inv = involved_samples[i];
        html += '<li class="list-group-item"> '
        html += '<a href="' + inv["sample"]["_links"]["self"] + '">'
        html += '<i class="fas fa-vial"></i>'
        html += inv["sample"]["uuid"]
        html += '</a>'
        html += '<p>'
        html +=  inv["old_site"]["name"] + '->' + new_site["name"]
        html += '</p>'

        html += '</li>'
    }

    console.log(html)

    $("#involved-samples-list-group").html(html);
}


$(document).ready(function() {
    var shipment_data = get_shipment();

    $("#loading-screen").fadeOut();
    fill_jumbotron(shipment_data);
    fill_table(shipment_data);
    fill_involved_samples(shipment_data["involved_samples"], shipment_data["new_site"]);
    
    $("#content").delay(500).fadeIn();

    $("#basic-info-nav").on("click", function () {
        deactivate_nav();
        $(this).addClass("active");
        hide_all();
        $("#basic-info-div").fadeIn(100);
    });

    $("#involved-samples-nav").on("click", function () {
        deactivate_nav();
        $(this).addClass("active");
        hide_all();
        $("#involved-samples-div").fadeIn(100);
    });

    $("#shipment-status-nav").on("click", function () {
        deactivate_nav();
        $(this).addClass("active");
        hide_all();
        $("#shipment-status-div").fadeIn(100);
    });

});