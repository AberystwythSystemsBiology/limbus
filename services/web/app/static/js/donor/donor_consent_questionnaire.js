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


function view_study_protocol() {
   if ($("#study_select").val()>0){
       $("#study-reference_id_div").show();
       $("#study-date_div").show();
       $("#study-comments_div").show();
       $("#study-undertaken_by_div").show();
   } else {
       $("#study-reference_id_div").hide();
       $("#study-date_div").hide();
       $("#study-comments_div").hide();
       $("#study-undertaken_by_div").hide();

   }
}

$(document).ready(function() {
    view_study_protocol();

    $("#consent_select").on("change", function() {
        view_form_helper("consent_select");
    });


    $("#study_select").on("change", function() {
        view_study_protocol();
    });

    $("#date").on("change", function() {
        if ($("#study-date").val() == null)
            $("#study-date").val($("#date").val())
    });
});