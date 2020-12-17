function query_disease(query) {

    var api_url = "http://0.0.0.0:5000/donor/disease/api/label_filter"

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
        window.open(uri, '_blank');
    });

    $.each(disease_info["synonyms"], function(a, b) {
        $("#synonym-btns").append("<div class='btn btn-sm' style='margin-right:10px; margin-bottom: 10px;'>"+b+"</div>");
    })

    console.log(disease_info);

    $.each(disease_info["references"], function(a, b) {
        var html = "<a href='" + b["self"] + "' target='_blank'>"
        html += "<div class='btn btn-sm' style='margin-right:10px; margin-bottom: 10px;'>"+a+"</div>";
        html += "</a>"
        console.log(html);
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