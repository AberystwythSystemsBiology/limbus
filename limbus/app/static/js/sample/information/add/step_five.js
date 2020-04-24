function add_warning(question) {
    $(question).addClass("list-group-item-warning")
    $(question).find(".question-warning").css("visibility", 'visible');
    var modal_question = $(`#${$(question).attr('id')}-m`)
    var fa = $(`#${$(question).attr('id')}-m`).find(".fa")

    fa.removeClass("fa-check-circle")
    fa.removeClass("text-success")
    fa.addClass("fa-exclamation-circle")
    fa.addClass("text-white")

    $(modal_question).addClass("bg-danger")
    $(modal_question).addClass("text-white")
}

function remove_warning(question) {
    $(question).removeClass("list-group-item-warning")
    $(question).find(".question-warning").css("visibility", 'hidden');
    var modal_question = $(`#${$(question).attr('id')}-m`)
    var fa = $(`#${$(question).attr('id')}-m`).find(".fa")

    fa.removeClass("fa-exclamation-circle")
    fa.removeClass("text-white")
    fa.addClass("fa-check-circle")
    fa.addClass("text-success")

    $(modal_question).removeClass("bg-danger")
    $(modal_question).removeClass("text-white")
}

function style_item(item) {
    var question = $(item).parents(".list-group-item")
    if (item.checked) {
        remove_warning(question)
    } else {
        add_warning(question)
    }
}

$(document).ready(function() {
    $('#selectAttribute').DataTable( {
        dom: 'Pfrtip'
    });

    $("#sampleTable_filter").hide();

    $(".dtsp-panesContainer").hide();

    $("#questionnaire-list").find(".form-check-input")
                            .change(function(e) {
        style_item(this)
    })

    $("#questionnaire-list").find(".form-check-input")
                            .each( (i, item) => {style_item(item)});

    $("#showFilter").click(function(e) {
        if ($(".dtsp-panesContainer").is(":visible")) {
            $(".dtsp-panesContainer").hide();
            $("#showFilter").text("Show Filters")
        }

        else {
            $("#showFilter").text("Hide Filters")
            $(".dtsp-panesContainer").show();
        }

    });
});
