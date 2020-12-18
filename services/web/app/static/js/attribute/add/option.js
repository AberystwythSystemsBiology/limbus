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

    var options = [];

    $("#submitOption").click(function(e) {
        var option = $("#optionInput").val();
        if (option != "") {
            options.push(option);
            update_view();
            $("#exampleModal").modal("hide");
            $("#optionInput").val("");
        }
    });

    function update_view() {
        $("#optionsDisplay").empty();
        for (i in options) {
            $("#optionsDisplay").append(
                '<li class="list-group-item">' +
                options[i] + '</li>');
        }
    }


    $("#submitButton").click(function submit_options(e) {
        if (options.length > 0 ) {

            var data = {
                "options[]": options
            };

            $.ajax({
            type: "POST",
            url: $(location).attr('href'),
            data: data,
            dataType: "json",
            success: function(response) {
                window.location = response["redirect"];
            }
        });


        }

        else {
            alert("We're going to need some options.")
        }
    });

});