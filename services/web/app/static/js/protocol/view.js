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


function lock_protocol(id) {
    var limbpro_id = "LIMBPRO-"+id;
    var warning_msg = "Press confirm to lock the protocol from being associated to sample/donors!";
    $("#confirm-modal-warning").html(warning_msg);
    $("#confirm-modal-title").html("Confirm locking protocol");
    $("#confirm-modal-input").html("");
    $("#confirm-modal-input").hide();
    $("#confirm-modal-guide").html("");

    $("#confirm-modal").modal({
        show: true
    });
 
    var action_link = window.location.origin + "/protocol/"+limbpro_id +"/lock";

    $("#confirm-modal-button").prop("disabled", false);
    $('#confirm-modal-button').click(function () {
        $("#confirm-modal-button").prop("disabled", true);

        $.ajax({
            type: "POST",
            url: action_link,
            dataType: "json",
            success: function (data) {
                $("#confirm-modal").modal({
                    show: false
                });

                if (data["success"]) {
                    window.location.href = window.location.origin + "/protocol/";
                } else {
                    window.location.reload();
                    return false;
                }
            }
        });
    });
};

function protocol_remove_logic(protocol_info) {
$("#protocol_remove").on("click", function () {
    msg = "Are you sure you want to delete this protocol?  ";
    msg += "Protocols with linked events can't be removed!";
    if (protocol_info["texts"].length>0) {
        msg += "Associated texts exist! Delete the protocol will deleted the texts as well";
    }
    if (protocol_info["documents"].length>0) {
        msg += "Associated documents exist! Delete the protocol will deleted the link, not the associated document.";
    }

    $("#cart-confirmation-label").text("Protocol Removal Confirmation")
    $("#cart-confirmation-msg").text(msg);
    $("#cart-confirmation-modal").modal({
        show: true
    });

    var removal_link = protocol_info['_links']["self"]+"/remove";
    $("#cart-confirm-button").on("click", function () {
        $("#cart-confirmation-modal").modal({
            show: false
        });
        $.ajax({
            type: "POST",
            url: removal_link,
            dataType: "json",
            success: function (data) {
                $("#cart-confirmation-modal").modal({
                    show: false
                });

                if (data["success"]) {
                    window.location.assign(window.location.origin + "/protocol");
                } else {
                    window.location.reload();
                }
            }
        });


    });

});
};

$(document).ready(function() {
    var protocol_info = JSON.parse(sessionStorage.getItem("protocol_info"));
    protocol_remove_logic(protocol_info);

    var protocol_id = $("#protocol-id").text();

    $("#lock-protocol").on("click", function () {
       
        lock_protocol(protocol_id);

      
    });
    /*    $('#protocol-table').DataTable( {
        });
    */
});