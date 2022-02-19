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

function query_disease(query) {
    var api_url = window.location.origin+ "/donor/disease/api/label_filter";

    var json = (function () {
        var json = null;
        $.post({
            'async': false,
            'global': false,
            'url': api_url,
            'contentType': 'application/json',
            'data': JSON.stringify({"label": query}),
            'success': function (data) {
                json = data;
            }
        });
        return json;
    })();



    return json;
}

function fill_content(disease_info, uri) {
    $("#disease-name").html(disease_info["label"]);
    $("#doid-id").html(disease_info["name"]);

    $("#synonym-btns").html('');

    $("#doid-label").on("click", function() {
        window.open(uri);
    });

    $.each(disease_info["synonyms"], function(a, b) {
        $("#synonym-btns").append("<div class='btn btn-sm' style='margin-right:10px; margin-bottom: 10px;'>"+b+"</div>");
    })


    $.each(disease_info["references"], function(a, b) {
        var html = "<a href='" + b["self"] + "'>"
        html += "<div class='btn btn-sm' style='margin-right:10px; margin-bottom: 10px;'>"+a+"</div>";
        html += "</a>"
        $("#disease-references").append(html);
    });

    $("#disease-description").html(disease_info["description"]);
}

function update_disease_select(diseases) {
    $("#disease_select").html('');

    $.each(diseases, function(uri, info){
        $("#disease_select").append($("<option />").text(info.label).val(uri));
    }) 
    
    $('.selectpicker').selectpicker('refresh');

    fill_content(diseases[$("#disease_select").val()], $("#disease_select").val());

    $("#disease_select").on("change", function() {
        fill_content(diseases[$("#disease_select").val()], $("#disease_select").val());
    });
}

function validate_form() {
    if ($("#disease_select").val() == null) {
        $("#submit").attr('disabled','disabled');
    }

    else {
        $("#submit").removeAttr('disabled');
    }
}

$(document).ready(function(){
    $("#disease-search").on("click", function() {
        $("#disease-result").fadeOut();
        var search_query = $("#disease_query").val();
        
        if (search_query.length > 2) {
            $("#disease-result").fadeOut();

            var diseases = query_disease(search_query)["content"];
            update_disease_select(diseases);

            $("#disease-result").fadeIn();
            validate_form();

        } 
    });

    validate_form();

    $("#has_procedure").on("change", function() {
        if ($(this).prop("checked")) {
            console.log("Aeeeyooo")
        }

        else {
            console.log("Aeee")
        }
    });

    $("#disease_select").on("change", function() {
        validate_form();
    })

});