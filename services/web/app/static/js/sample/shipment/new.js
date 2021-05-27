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

function get_cart() {
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

function fill_cart(cart) {
    for (i in cart) {
        var sample = cart[i];
        
        var href = sample["sample"]["_links"]["self"]


        var li_data = "";
        li_data +=  "<a href='" + href + "' target='_blank' class='list-group-item'>";
        li_data += "<i class='fas fa-vial'></i> "
        li_data += sample["sample"]["uuid"];
        li_data += "</a>"

        $("#samples-cart-list-group").append(li_data)

    }
}

$(document).ready(function() {
    var cart = get_cart();
    fill_cart(cart);
});