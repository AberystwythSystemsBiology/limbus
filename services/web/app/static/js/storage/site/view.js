/*
Copyright (C) 2020 Keiron O'Shea <keo7@aber.ac.uk>

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

function set_default_address(id_checked, i_checked){
    // -- uncheck disallowed!
    var checked = $("#"+id_checked).is(":checked");

    if (checked == false) {
        $("#"+id_checked).prop('checked', true);
    } else if ($("#addresses-"+i_checked+"-delete").is(":checked")) {
        $("#"+id_checked).prop('checked', false);
    }
    else {
        addr_active.forEach(function (k, index) {
            if (k != i_checked)
                $("#addresses-" + k + "-is_default").prop('checked', false);
        });
    }

}

function delete_address(id_checked, i_checked){

    if (addr_active.length==1) {
        msg = "Need to keep at least one address for the site!";
        alert(msg);
        return false;
    }
    var checked = $("#addresses-"+i_checked+"-delete").is(":checked");
    if (checked == false) {
        $("#addresses-" + i_checked + "-delete").prop('checked', true);
        return false;
    }

    $("#li-addresses-"+i_checked).hide();

    addr_active = addr_active.filter( (el) => el != i_checked);
    if ($("#addresses-" + i_checked + "-is_default").is(":checked")) {
        $("#addresses-" + i_checked + "-is_default").prop('checked', false);
        $("#addresses-" + addr_active[0] + "-is_default").prop('checked', true);
    }
}

function active_address_logic() {
    for (var k = 0; k < num_addr; k++) {
        if (addr_active.includes(k)) {
            $("#li-addresses-"+k).show();
            $("#addresses-" + k + "-delete").prop('checked', false);
        }
        else {

            $("#li-addresses-" + k).hide();
            $("#addresses-" + k + "-delete").prop('checked', true);
        }
    }
}


var num_addr = $("#addresses").children().length;
console.log("num", num_addr);
var addr_active = [];

$(document).ready(function () {
    var valid;

    scheduled = $.ajax({
        type: "get",
        url: $(location).attr('href'),
        async: false,
        success: function (response) {
            valid = response;
        }
    });

    // last address table is for new address, hide unless click new address
    var num_actual = parseInt($("#num_addresses").val());
    //console.log("num_actual", num_actual);

    for (var k = 0; k < num_addr; k++) {
        $("#h-addresses-"+k).html("Address-"+(k+1));
        if (k >= num_actual) {
            $("#li-addresses-"+k).hide();
        } else {
            $("#li-addresses-"+k).show();
            addr_active.push(k);
        }
    }

    active_address_logic();

    $("#btn_add_address").click(function () {
         $("#li-addresses-"+num_actual).show();
         addr_active.push(num_actual);
         num_actual += 1;
         active_address_logic();
    });

    $(":checkbox").change(function() {
        var id_checked = $(this).attr('id');
        var regex = /\d+/g;
        var i_checked = parseInt(id_checked.match(regex));
        if (id_checked.search("-is_default")>0) {
            set_default_address(id_checked, i_checked);

        } else if (id_checked.search("-delete")>0) {
            delete_address(id_checked, i_checked);
        }
        active_address_logic();
    });

});