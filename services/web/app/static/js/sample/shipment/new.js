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

function compare_samples(a,b){
    return a["sample"]["id"]-b["sample"]["id"];
}

function reset_cart(){
    $("#samples-cart-list-group").empty();
    // var url = "{{ url_for('sample.shipment_cart') }}";
    $("#samples-cart-list-group").append("<a href='/sample/shipment/cart' class='list-group-item bg-primary text-white'>"+"<i class='fa fa-shopping-cart'></i> My Samples Cart</a>");
    cart = get_cart();
    fill_cart(cart);
}

function fill_cart(cart) {
    cart.sort(compare_samples);
    for (i in cart) {
        var sample = cart[i];
        if (sample["selected"]) {

            var href = sample["sample"]["_links"]["self"]


            var li_data = "";
            li_data += "<a class='list-group-item selected_cart_item' style='text-decoration: none'>";//href='" + href + "' target='_blank'
            li_data += "<i class='fas fa-vial'></i>"
            li_data += sample["sample"]["uuid"];
            li_data += "</a>"


            $("#samples-cart-list-group").append(li_data)
        } else {
            var href = sample["sample"]["_links"]["self"]


            var li_data = "";
            li_data += "<a class='list-group-item unselected_cart_item' style='text-decoration: line-through'>";//href='" + href + "' target='_blank'
            li_data += "<i class='fas fa-vial'></i>"
            li_data += sample["sample"]["uuid"];
            li_data += "</a>"

            $("#samples-cart-list-group").append(li_data)
        }
    }
        $('.unselected_cart_item').on("click", function() {
            // this.style = "text-decoration:none;";
            var UUID_text = this.text;//.substring(1)
            var UUID = {"UUID": UUID_text};
            var res;
            var api_url = window.location.origin + "/sample/shipment/cart/select/shipment";
            $.post({
                'async': false,
                'global': false,
                'url': api_url,
                'contentType': 'application/json',
                'data': JSON.stringify(UUID),
                'success': function (data) {
                    res = data;
                }
            });
            // console.log(res);
            reset_cart();
        });
    // }
        $('.selected_cart_item').on("click", function() {
            var UUID_text = this.text;//.substring(1)
            var UUID = {"UUID": UUID_text};
            var res;
            var api_url = window.location.origin + "/sample/shipment/cart/deselect/shipment";
            $.post({
                'async': false,
                'global': false,
                'url': api_url,
                'contentType': 'application/json',
                'data': JSON.stringify(UUID),
                'success': function (data) {
                    res = data;
                }
            });
            // console.log(res);
            reset_cart();
        });
// }
}


function update_site_addresses(site_id){
    var choices = addresses[site_id];
    var options = "";

    if (choices != undefined) {
        choices.forEach(function (value, index) {
            options += '<option value="' + value[0] + '">' + value[1] + '</option>';
        });
        //console.log("options", options);
        $("#address_id").empty().append(options);
        $("#address_id").val(choices[0][0]).change();

    } else {
        options += '<option value="' + 0 + '">' + "-- No address associated--" + '</option>';
        $("#address_id").empty().append(options);
        $("#address_id").val(0).change();
    }
}


function site_address_selection_logic() {
    if (($("#site_id").val()==0) && ($("#external_site_id").val()!=0)) {
        update_site_addresses(site_id);
    }

    $("#site_id").change(function(){
        if ($("#site_id").val()!=0) {
            $("#external_site_id").val(0).change();
            var  site_id = $("#site_id").val();
            update_site_addresses(site_id);
        }
    });
    $("#external_site_id").change(function(){
        if ($("#external_site_id").val()!=0) {
            $("#site_id").val(0).change();
            var  site_id = $("#external_site_id").val();
            update_site_addresses(site_id);
        }
    });

}

var addresses = JSON.parse(sessionStorage.getItem("addresses"));
$(document).ready(function() {
    //console.log("addresses ", addresses);
    var cart = get_cart();
    fill_cart(cart);
    site_address_selection_logic();


});