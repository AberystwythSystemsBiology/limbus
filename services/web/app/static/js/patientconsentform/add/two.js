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

    $("#remove_question").click(function (e) {
        alert("Hello World")
    });

    function update_view() {
        $("#questionsToSubmit").empty();


        for (o in options) {
            var q_num = parseInt(parseInt(o)+parseInt(1));
            $("#questionsToSubmit").append(
                '<div class="list-group-item list-group-item-action">\n' +
                '            <div class="d-flex w-100 justify-content-between">\n' +
                '              <h5 class="mb-1">Question '+ q_num +'</h5>\n' +
                '            </div>\n' +
                '            <p class="mb-1">'+options[o]+'</p>\n' +
                '          </div>'
            );
        }
    }

    update_view();

    $("#submitOption").click(function (e) {
        options.push($("#questionInput").val());
        update_view();
        $("#exampleModal").modal("hide");
        $("#questionInput").val("");
    });

    $("#submitButton").click(function (e) {
        if (options.length > 0) {
            var data = {
            "questions[]": options
        }

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

        else (
            alert("No questions have been entered?")
        )

    });
});


