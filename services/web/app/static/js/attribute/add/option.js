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

function query_diod(query=null, subclass=null, iri=null) {
    var api_url = window.location.origin+ "/donor/disease/api/label_filter";
    if (iri === null) {
        var json_query = JSON.stringify({"label": query, "subclass": subclass});
    }
    else {
        var json_query = JSON.stringify({"iri": iri});
    }

    var json = (function () {
        var json = null;
        $.post({
            'async': false,
            'global': false,
            'url': api_url,
            'contentType': 'application/json',
            'data': json_query, //JSON.stringify({"label": query, "subclass": subclass}),
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
        var html = "<a href='" + b["self"] + "'>";
        html += "<div class='btn btn-sm' style='margin-right:10px; margin-bottom: 10px;'>"+a+"</div>";
        html += "</a>"
        $("#disease-references").append(html);
    });

    $("#disease-description").html(disease_info["description"]);
}

function update_accession(diseases) {
    $("#accession").html('');

    $.each(diseases, function(uri, info) {
        $("#accession").append($("<option />").text(info.label).val(uri));
    });

    $('.selectpicker').selectpicker('refresh');

    fill_content(diseases[$("#accession").val()], $("#accession").val());

    $("#accession").on("change", function() {
        fill_content(diseases[$("#accession").val()], $("#accession").val());
    });
}

function validate_form() {
    if ($("#accession").val() == null) {
        $("#submit").attr('disabled','disabled');
    }

    else {
        $("#submit").removeAttr('disabled');
    }
}

$(document).ready(function () {

    var iri = $("#accession").val();
    if (iri !== null && iri !== "") {
        var diseases = query_diod(query = null, null, iri)["content"];
        if (diseases.length > 0) {
            update_accession(diseases);
            $("#disease-result").show();
        }
    }

    $("#disease-search").on("click", function() {
        $("#disease-result").fadeOut();
        var search_query = $("#term").val();
        var subclass = $("#subclass").val();

        if (search_query.length > 2) {
            $("#disease-result").fadeOut();

            var diseases = query_diod(search_query, subclass, null)["content"];
            update_accession(diseases);

            $("#disease-result").fadeIn();
            //validate_form();

        }
    });

    //validate_form();
    //
    // $("#accession").on("change", function() {
    //     validate_form();
    // });

/*
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
    });*/

});