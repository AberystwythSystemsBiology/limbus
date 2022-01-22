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


function lock_attribute(id) {
    var limbattr_id = "LIMBATTR-"+id;
    var warning_msg = "Press confirm to lock the attribute from being associated to sample/donors!";
    $("#confirm-modal-warning").html(warning_msg);
    $("#confirm-modal-title").html("Confirm locking attribute");
    $("#confirm-modal-input").html("");
    $("#confirm-modal-input").hide();
    $("#confirm-modal-guide").html("");

    $("#confirm-modal").modal({
        show: true
    });

    var action_link = window.location.origin + "/attribute/"+limbattr_id +"/lock";

    $("#confirm-modal-button").prop("disabled", false);
    $('#confirm-modal-button').click(function () {
        // window.location.href = removal_link;
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
                    window.location.reload();
                } else {
                    window.location.reload();
                    //alert("We have a problem! "+data["message"]);
                    return false;
                }
            }
        });
    });
};


function remove_attribute(id) {
    var limbattr_id = "LIMBATTR-"+id;
    var warning_msg = "Press confirm to delete the attribute!" +
        "Deleting an attribute with associated samples/donors will raise errors";
    $("#confirm-modal-warning").html(warning_msg);
    $("#confirm-modal-title").html("Confirm attribute removal");
    $("#confirm-modal-guide").html("To confirm, enter " + limbattr_id);
    $("#confirm-modal-input").html("");
    $("#confirm-modal-input").show();
    $("#confirm-modal").modal({
        show: true
    });

    var removal_link = window.location.origin + "/attribute/"+limbattr_id +"/remove";

    $("#confirm-modal-input").on("change", function () {
        var user_entry = $(this).val();
        // console.log("limbattr_id", limbattr_id);
        if (user_entry == limbattr_id) {
            $("#confirm-modal-button").prop("disabled", false);
            $('#confirm-modal-button').click(function () {
                // window.location.href = removal_link;
                $("#confirm-modal-button").prop("disabled", true);

                $.ajax({
                    type: "POST",
                    url: removal_link,
                    dataType: "json",
                    success: function (data) {
                        $("#confirm-modal").modal({
                            show: false
                        });

                        if (data["success"]) {
                            //window.location.reload();
                            window.location.href = window.location.origin + "/attribute/";
                        } else {
                            window.location.reload();
                            //alert("We have a problem! "+data["message"]);
                            return false;
                        }
                    }
                });
            });
        } else {
            $("#confirm-modal-button").prop("disabled", true);
        }
    })
};


$(document).ready(function () {
var attr_id = $("#attribute-id").text();

$("#lock-attribute").on("click", function () {
    lock_attribute(attr_id);
});

$("#remove-attribute").on("click", function () {
    remove_attribute(attr_id);
});

});