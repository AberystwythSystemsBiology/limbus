/*
Copyright (C) 2021 C Lu <culATaberDOTacDOTuk>

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

function check_protocol_type() {
    var protocol_info = $("#protocol_id option:selected").text();
    const intact_types = ["Sample Transfer", "Collection", "Study", "Temporary Storage"];
    var matches = protocol_info.match(/\[(.*?)\]/);
    if (matches) {
        let protocol_type = matches[1];
        if (intact_types.includes(protocol_type))
            $("#sample-quantity").hide();
        else
            $("#sample-quantity").show();
    }
}

$(document).ready(function() {
    check_protocol_type();

    let remaining_qty = parseFloat($("#remaining_qty_old").val());
    $("#reduced_quantity").change(function () {
        var reduced_qty = $("#reduced_quantity").val();
        $("#remaining_quantity").val(remaining_qty - reduced_qty);
    });

    $("#protocol_id").change(function(){
        check_protocol_type();
    });


});