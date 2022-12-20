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

$(document).ready(function () {
    var api_url = encodeURI(window.location);
    var uuid = api_url.split("/")[4];

    $("#remove").on("click", function (event) {
        event.preventDefault(); //prevent form submit before confirming the removal

        var warning_msg = "<B>Warning:</B> This action cannot be undone!";
        warning_msg += "<br> <B>Deep remove will delete the sample and its sub-samples and associated data. !!</B>";
        $("#delete-protocol-warning").html(warning_msg);
        $("#delete-protocol-confirm-modal-title").html("Confirm Sample Removal");
        $("#delete-protocol-event-confirm").html("Please enter the Sample UUID to confirm that you want to remove this Sample!")

        $("#delete-protocol-confirm-modal").modal({
            show: true
        });

        $("#protocol-uuid-remove-confirmation-input").on("change", function () {
            var user_entry = $(this).val();

            $('#confirm').prop('checked', false);
            if (user_entry == uuid) {
                $("#protocol-remove-confirm-button").prop("disabled", false);
                $('#protocol-remove-confirm-button').click(function () {
                    $("#delete-protocol-confirm-modal").modal({
                        show: false
                    });
                    $("form").submit();
                });

            } else {
                $("#delete-protocol-confirm-modal").modal({
                    show: true
                });
                $("#protocol-remove-confirm-button").prop("disabled", true);

            };
        });
    });

});
