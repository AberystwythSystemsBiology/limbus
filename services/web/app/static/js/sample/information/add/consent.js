/*
Copyright (C) 2022 Keiron O'Shea <keo7@aber.ac.uk>

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


function check_study_reference_id(study_id, reference_id) {
    var api_url = encodeURI(window.location.origin) + "/donor/get_study_reference";
    var json = (function () {
        var json = null;
        $.post({
            'async': false,
            'global': false,
            'url': api_url,
            'contentType': 'application/json',
            'data': JSON.stringify({protocol_id: study_id, reference_id: reference_id}),
            'success': function (data) {
                json = data;
            }
        });
        //console.log(json["content"]);
        return json["content"];
    })();

    if (json===null) {
        return false;
    }
    if (json.length > 0) {
        return true;
    }
    return false;
}


function study_reference_check() {
    $("#study-reference_id").change(function() {
        var study_id = $("#study_select").val();
        var reference_id = $("#study-reference_id").val();
        var existed = check_study_reference_id(study_id, reference_id);
        if (existed) {
            var msg = "Warning: The participant reference id for this study already exist in the database, " +
                "please make sure the reference is correct before continue!";
            $("#confirmation-msg").html(msg);
            $("#confirmation-modal").modal({
                show: true
            });
        };
        }
    );
}
$(document).ready(function() {
    $("#check-button").on("click", function() {
        var check_status = $("#check-status").html();

        if (check_status == "Check") {
            $("#check-status").text("Uncheck");
            $("#check-button").removeClass("btn-success").addClass("btn-danger");
            $('.form-check-input').prop('checked', true);    
        }

        else {
            $("#check-status").text("Check");
            $("#check-button").removeClass("btn-danger").addClass("btn-success");
            $('.form-check-input').prop('checked', false);            
        }
    });

    study_reference_check();
});